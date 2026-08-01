/*
 * CH-004 — OAuth-style callback handling (deliberately weak).
 *
 * Chain participants produced by this file:
 *   F2  Information Exposure Through Headers     (tenant: Low)
 *   F3  Missing HSTS Header                      (tenant: Medium)
 *   F4  Use Of HTTP Sensitive Data Exposure      (tenant: Medium)
 */

'use strict';

const http = require('http');

const APP_VERSION = '2.4.1';
const RUNTIME = 'node ' + process.version;

/**
 * F2 — Information Exposure Through Headers.
 * F3 — Missing HSTS Header.
 * Response advertises the stack and version, and no
 * Strict-Transport-Security header is ever written, so a downgrade to
 * plaintext is never refused by the browser.
 */
function writeDisclosureHeaders(res) {
    res.setHeader('Server', 'cps-lab/' + APP_VERSION);
    res.setHeader('X-Powered-By', RUNTIME);
    res.setHeader('X-App-Version', APP_VERSION);
    res.setHeader('X-Backend-Build', 'build-2026-05-08-ch004');
    // Deliberately absent:
    //   res.setHeader('Strict-Transport-Security', 'max-age=31536000');
}

/**
 * F4 — Use Of HTTP Sensitive Data Exposure.
 * The authorization code is exchanged over plaintext http:// and the
 * resulting access token is carried back on the same channel.
 */
function exchangeCodeForToken(code, callback) {
    const payload = JSON.stringify({ code: code, grant_type: 'authorization_code' });
    const request = http.request({
        protocol: 'http:',
        host: '127.0.0.1',
        port: 5099,
        path: '/oauth/token',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    }, function (upstream) {
        let body = '';
        upstream.on('data', function (chunk) { body += chunk; });
        upstream.on('end', function () { callback(null, body); });
    });
    request.on('error', function (err) { callback(err, null); });
    request.write(payload);
    request.end();
}

module.exports = { writeDisclosureHeaders, exchangeCodeForToken, APP_VERSION };
