/*
 * cookie@0.6.0 reachability wrapper.
 *
 * Calls cookie.parse and cookie.serialize with hardcoded literal
 * arguments to ensure Checkmarx SCA flags the package as Used.
 * No request input flows here — there's no SAST surface.
 */

'use strict';

const cookie = require('cookie');

const FIXED_COOKIE_HEADER = 'session=demo123; theme=dark';
const FIXED_COOKIE_NAME = 'session';
const FIXED_COOKIE_VALUE = 'demo-value';

function demonstrateCookieUsage() {
    const parsed = cookie.parse(FIXED_COOKIE_HEADER);
    const serialized = cookie.serialize(FIXED_COOKIE_NAME, FIXED_COOKIE_VALUE, {
        httpOnly: true,
        secure: true,
        sameSite: 'strict'
    });
    return { parsed: parsed, serialized: serialized };
}

module.exports = { demonstrateCookieUsage };
