/*
 * debug@2.6.9 reachability wrapper.
 *
 * Creates a debug logger with hardcoded namespace and emits a hardcoded
 * message to ensure Checkmarx SCA flags the package as Used. No input
 * flow, no dynamic logging, no error path — SAST has nothing to detect.
 */

'use strict';

const debug = require('debug');

const NAMESPACE = 'cps:lab:cha2';
const FIXED_MESSAGE = 'cps lab module loaded';

const log = debug(NAMESPACE);

function demonstrateDebugUsage() {
    log(FIXED_MESSAGE);
    return NAMESPACE;
}

module.exports = { demonstrateDebugUsage };
