"""
LAB ENVIRONMENT GUARD — DO NOT REMOVE.

CH-002 lab: SCA + Container Security composition into blast-radius
amplification. Two-engine chain. All findings expected Low.
Refuses to start unless CPS_LAB_ENVIRONMENT=1.
"""

from __future__ import annotations

import os
import sys

LAB_ENV_VAR = "CPS_LAB_ENVIRONMENT"
LAB_BANNER = """
================================================================================
  CPS LAB APPLICATION (CH-002) — DELIBERATELY VULNERABLE
  SCA + Container Security composition (all-Low chain)

  This application contains intentional vulnerable dependencies and a
  deliberately-misconfigured Dockerfile for the purpose of validating Chain
  Potential Score (CPS) predictions. It must not be exposed to any network
  other than localhost. Containers built from the included Dockerfile must
  not be pushed to any production registry.
================================================================================
"""


def assert_lab_environment() -> None:
    if os.environ.get(LAB_ENV_VAR) != "1":
        sys.stderr.write(LAB_BANNER)
        sys.stderr.write(
            f"\nERROR: This is a deliberately-vulnerable lab application.\n"
            f"It will not start unless {LAB_ENV_VAR}=1 is set.\n"
            f"  export {LAB_ENV_VAR}=1\n\n"
        )
        sys.exit(1)
    sys.stderr.write(LAB_BANNER)
