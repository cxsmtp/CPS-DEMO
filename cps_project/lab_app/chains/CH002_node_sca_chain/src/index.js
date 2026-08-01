/*
 * CH-002 lab — top-level entry
 * =============================
 *
 * Goal: ensure cookie@0.6.0 and debug@2.6.9 are flagged "Used" by
 * Checkmarx SCA reachability analysis, while producing zero SAST
 * findings in this lab's own source code.
 *
 * SAST-clean discipline applied:
 *   - No request handling, no input flow, no taint sources.
 *   - No Math.random() (would trigger Use of Insufficiently Random Values).
 *   - No Buffer(string) (would trigger Use of Deprecated Functions).
 *   - No error logging or stack-trace exposure (would trigger Secret Leak).
 *   - No HTTP server (would trigger HSTS / sensitive data findings).
 *   - No string formatting on dynamic data (would trigger Format String).
 *   - No deprecated APIs (Buffer constructor, crypto.createCredentials, etc.)
 *   - No switch statements without default (would trigger Missing Default Case).
 *
 * The libraries are exercised with hardcoded literal arguments only.
 * Reachability is established but no taint flow exists for SAST to follow.
 */

'use strict';

const labGuard = require('./lab_guard');
const cookieLib = require('./cookie_lib');
const debugLib = require('./debug_lib');

function main() {
    labGuard.assertLabEnvironment();
    cookieLib.demonstrateCookieUsage();
    debugLib.demonstrateDebugUsage();
}

if (require.main === module) {
    main();
}

module.exports = { main };
