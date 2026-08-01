/*
 * Lab environment guard — refuses to start unless CPS_LAB_ENVIRONMENT=1.
 *
 * SAST-clean: no input flow, no error message disclosure, no dynamic
 * string formatting on user-controlled data.
 */

'use strict';

const LAB_ENV_VAR = 'CPS_LAB_ENVIRONMENT';

function assertLabEnvironment() {
    if (process.env[LAB_ENV_VAR] !== '1') {
        process.stderr.write(
            'CPS LAB APPLICATION (CH-002 Node) - DELIBERATELY VULNERABLE\n' +
            'Refusing to start without CPS_LAB_ENVIRONMENT=1.\n'
        );
        process.exit(1);
    }
}

module.exports = { assertLabEnvironment };
