/*
 * CH-003 — Session Forgery to Account Takeover
 * =============================================
 *
 * Deliberately vulnerable. Node built-in http only, zero dependencies,
 * so the SCA surface is empty and the chain is purely SAST composition.
 *
 * Chain participant produced by this file:
 *   F1  HttpOnly Cookie Flag Not Set             (tenant: Medium)
 *
 * Will not start unless CPS_LAB_ENVIRONMENT=1.
 */

'use strict';

const http = require('http');
const url = require('url');
const session = require('./session');

const PORT = 5090;
const LAB_ENV_VAR = 'CPS_LAB_ENVIRONMENT';

function assertLabEnvironment() {
    if (process.env[LAB_ENV_VAR] !== '1') {
        process.stderr.write(
            'CPS LAB (CH-003) - DELIBERATELY VULNERABLE.\n' +
            'Refusing to start without CPS_LAB_ENVIRONMENT=1.\n'
        );
        process.exit(1);
    }
}

/**
 * F1 — HttpOnly Cookie Flag Not Set.
 * The session cookie is written without HttpOnly, so any script running
 * in the page can read it. No Secure flag either, which pairs with the
 * missing HSTS in CH-004.
 */
function setSessionCookie(res, issued) {
    res.setHeader('Set-Cookie', [
        'sid=' + issued.sessionId + '; Path=/',
        'sig=' + issued.signature + '; Path=/'
    ]);
}

function handleLogin(req, res) {
    const issued = session.issueSession('demo-user');
    setSessionCookie(res, issued);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', user: issued.userId }));
}

function handleWhoAmI(req, res, query) {
    const ok = session.verifySession(query.sid, query.sig);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ authenticated: ok }));
}

const server = http.createServer(function (req, res) {
    const parsed = url.parse(req.url, true);
    try {
        if (parsed.pathname === '/login') {
            return handleLogin(req, res);
        }
        if (parsed.pathname === '/whoami') {
            return handleWhoAmI(req, res, parsed.query);
        }
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'not found' }));
    } catch (err) {
        // Returns the raw error text, which carries the signing key
        // thrown by session.verifySession (completes F4).
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(err.message);
    }
});

function main() {
    assertLabEnvironment();
    server.listen(PORT, '127.0.0.1', function () {
        process.stderr.write('CH-003 lab listening on 127.0.0.1:' + PORT + '\n');
    });
}

if (require.main === module) {
    main();
}

module.exports = { server };
