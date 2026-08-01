"""
LAB ENVIRONMENT GUARD — DO NOT REMOVE.

This module enforces that the deliberately-vulnerable lab application
can only start when CPS_LAB_ENVIRONMENT=1 is explicitly set in the
environment. The check is intentionally redundant with README warnings.
"""

from __future__ import annotations

import os
import sys

LAB_ENV_VAR = "CPS_LAB_ENVIRONMENT"
LAB_BANNER = """
================================================================================
  CPS LAB APPLICATION (CH-001) — DELIBERATELY VULNERABLE
  
  This application contains intentional security weaknesses for the purpose
  of validating Chain Potential Score (CPS) predictions. It must not be
  exposed to any network other than localhost, and must never be deployed
  in any environment containing real data, real credentials, or real users.
================================================================================
"""


def assert_lab_environment() -> None:
    if os.environ.get(LAB_ENV_VAR) != "1":
        sys.stderr.write(LAB_BANNER)
        sys.stderr.write(
            f"\nERROR: This is a deliberately-vulnerable lab application.\n"
            f"It will not start unless {LAB_ENV_VAR}=1 is set in your env.\n"
            f"If you understand the warnings above, run:\n"
            f"    export {LAB_ENV_VAR}=1\n\n"
        )
        sys.exit(1)
    sys.stderr.write(LAB_BANNER)
