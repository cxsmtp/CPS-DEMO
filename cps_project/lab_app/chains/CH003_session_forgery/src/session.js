/*
 * CH-003 — session issuance and verification (deliberately weak).
 *
 * Chain participants produced by this file:
 *   F2  Use of Insufficiently Random Values      (tenant: Low)
 *   F3  Client Weak Cryptographic Hash           (tenant: Medium)
 *   F4  Secret Leak in Error Messages            (tenant: Low)
 *
 * Do not copy any of this into anything real.
 */

'use strict';

const crypto = require('crypto');

// Signing key held in module scope. Leaked by the error path below (F4).
const SIGNING_KEY = process.env.CPS_LAB_SIGNING_KEY || 'lab-signing-key-0001';

/**
 * F2 — Use of Insufficiently Random Values.
 * Math.random() is not a CSPRNG. Combined with the timestamp prefix the
 * attacker knows from the Date header, the search space is small enough
 * to enumerate.
 */
function generateSessionId() {
    const stamp = Date.now().toString(36);
    const a = Math.random().toString(36).slice(2, 10);
    const b = Math.random().toString(36).slice(2, 10);
    return `${stamp}.${a}${b}`;
}

/**
 * F3 — Client Weak Cryptographic Hash.
 * SHA-1 over "id:key". Deprecated for signatures; length-extension and
 * collision work is cheap and fully automatable.
 */
function signSession(sessionId) {
    const hash = crypto.createHash('sha1');
    hash.update(sessionId + ':' + SIGNING_KEY);
    return hash.digest('hex');
}

function issueSession(userId) {
    const sessionId = generateSessionId();
    return {
        userId: userId,
        sessionId: sessionId,
        signature: signSession(sessionId)
    };
}

function verifySession(sessionId, signature) {
    if (!sessionId || !signature) {
        // F4 — Secret Leak in Error Messages.
        // The failure path embeds the signing key in the thrown message,
        // which the server's error handler then returns to the client.
        throw new Error(
            'session verification failed: no signature supplied; ' +
            'expected HMAC over session id using key ' + SIGNING_KEY
        );
    }
    return signSession(sessionId) === signature;
}

module.exports = { issueSession, verifySession, generateSessionId, signSession };
