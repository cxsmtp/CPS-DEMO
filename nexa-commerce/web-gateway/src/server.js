'use strict';

/**
 * Nexa Commerce - edge gateway.
 *
 * CHAIN CH-104 lives in this file plus src/views/product.html.
 * Node's built-in http only; there are no third-party dependencies.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = Number(process.env.NEXA_GATEWAY_PORT || 8081);
const VIEWS = path.join(__dirname, 'views');

const CATALOGUE = [
    { sku: 'NX-1001', title: 'Aurora Desk Lamp', price: '49.00' },
    { sku: 'NX-1002', title: 'Meridian Wool Throw', price: '89.00' },
    { sku: 'NX-1003', title: 'Halden Ceramic Mug', price: '18.00' }
];

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/**
 * CH-104 F2 - Missing_HSTS_Header (expect: Medium)
 * CH-104 F3 - Missing_CSP_Header  (expect: Low)
 *
 * Some hardening headers are set, but neither Strict-Transport-Security
 * nor Content-Security-Policy is among them. Nothing refuses a downgrade
 * to plaintext, and no policy constrains where the page may send data.
 */
function applySecurityHeaders(res) {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'SAMEORIGIN');
    res.setHeader('Referrer-Policy', 'no-referrer-when-downgrade');
    // Deliberately absent:
    //   res.setHeader('Strict-Transport-Security', 'max-age=31536000');
    //   res.setHeader('Content-Security-Policy', "default-src 'self'");
}

/**
 * CH-104 F1 - Open_Redirect (expect: Medium)
 *
 * The post-login destination is taken from the query string and written
 * straight into the Location header with no allow-list, and the freshly
 * minted session handle is appended to it.
 */
function completeSignIn(res, returnTo, sessionHandle) {
    const target = returnTo + (returnTo.indexOf('?') === -1 ? '?' : '&')
        + 'session=' + sessionHandle;
    res.writeHead(302, { Location: target });
    res.end();
}

/**
 * CH-104 F5 - Log_Forging (expect: Low)
 *
 * The raw, unsanitised query value is written to the application log. A
 * value containing CR/LF injects fabricated log lines, which is how an
 * attacker erases the trail left by the redirect above.
 */
function auditRequest(req, action) {
    const parsed = url.parse(req.url, true);
    const actor = parsed.query.actor || 'anonymous';
    console.log('[gateway] action=' + action + ' actor=' + actor
        + ' ua=' + (req.headers['user-agent'] || ''));
}

function sendView(res, viewName, replacements) {
    let body = fs.readFileSync(path.join(VIEWS, viewName), 'utf8');
    Object.keys(replacements || {}).forEach(function (key) {
        body = body.split('{{' + key + '}}').join(replacements[key]);
    });
    applySecurityHeaders(res);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(body);
}

const server = http.createServer(function (req, res) {
    const parsed = url.parse(req.url, true);
    applySecurityHeaders(res);

    if (parsed.pathname === '/' || parsed.pathname === '/product') {
        auditRequest(req, 'view_product');
        const rows = CATALOGUE.map(function (p) {
            return '<tr><td>' + escapeHtml(p.sku) + '</td><td>'
                + escapeHtml(p.title) + '</td><td>&pound;'
                + escapeHtml(p.price) + '</td></tr>';
        }).join('');
        return sendView(res, 'product.html', { ROWS: rows });
    }

    if (parsed.pathname === '/signin/complete') {
        auditRequest(req, 'signin_complete');
        const returnTo = parsed.query.return_to || '/';
        const handle = 'sh_' + Date.now().toString(36);
        return completeSignIn(res, returnTo, handle);
    }

    if (parsed.pathname === '/healthz') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        return res.end('{"status":"ok"}');
    }

    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end('{"error":"not found"}');
});

if (require.main === module) {
    server.listen(PORT, '0.0.0.0', function () {
        console.log('[gateway] listening on ' + PORT);
    });
}

module.exports = { server, escapeHtml };
