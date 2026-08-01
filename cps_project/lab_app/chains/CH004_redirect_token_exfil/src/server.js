/*
 * CH-004 — Redirect-to-Token-Exfiltration
 * ========================================
 *
 * Deliberately vulnerable. Node built-in http only, zero dependencies.
 *
 * Chain participant produced by this file:
 *   F1  Open Redirect                            (tenant: Medium)
 *
 * Chain story: the callback discloses stack and version (F2), never sets
 * HSTS (F3), exchanges the authorization code over plaintext http (F4),
 * and then hands control to an attacker-supplied return URL (F1) with the
 * token still on the query string. Four findings, none rated High by the
 * scanner, composing into third-party token theft.
 *
 * Will not start unless CPS_LAB_ENVIRONMENT=1.
 */

'use strict';

const http = require('http');
const url = require('url');
const oauth = require('./oauth_callback');

const PORT = 5091;
const LAB_ENV_VAR = 'CPS_LAB_ENVIRONMENT';

function assertLabEnvironment() {
    if (process.env[LAB_ENV_VAR] !== '1') {
        process.stderr.write(
            'CPS LAB (CH-004) - DELIBERATELY VULNERABLE.\n' +
            'Refusing to start without CPS_LAB_ENVIRONMENT=1.\n'
        );
        process.exit(1);
    }
}

/**
 * F1 — Open Redirect.
 * The return_to parameter is taken from the request and written straight
 * into the Location header with no allow-list check, and the freshly
 * minted token is appended to it.
 */
function redirectAfterAuth(res, returnTo, token) {
    const target = returnTo + '?access_token=' + token;
    res.writeHead(302, { Location: target });
    res.end();
}

const server = http.createServer(function (req, res) {
    const parsed = url.parse(req.url, true);
    oauth.writeDisclosureHeaders(res);

    if (parsed.pathname === '/oauth/callback') {
        const code = parsed.query.code || '';
        const returnTo = parsed.query.return_to || '/';
        oauth.exchangeCodeForToken(code, function (err, body) {
            if (err) {
                res.writeHead(502, { 'Content-Type': 'application/json' });
                return res.end(JSON.stringify({ error: 'token exchange failed' }));
            }
            let token = '';
            try {
                token = JSON.parse(body).access_token || '';
            } catch (parseErr) {
                token = '';
            }
            return redirectAfterAuth(res, returnTo, token);
        });
        return;
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ app: 'cps-ch004-lab', version: oauth.APP_VERSION }));
});

function main() {
    assertLabEnvironment();
    server.listen(PORT, '127.0.0.1', function () {
        process.stderr.write('CH-004 lab listening on 127.0.0.1:' + PORT + '\n');
    });
}

if (require.main === module) {
    main();
}

module.exports = { server };
