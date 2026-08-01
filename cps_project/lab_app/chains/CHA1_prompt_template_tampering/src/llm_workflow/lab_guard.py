"""
LAB ENVIRONMENT GUARD — DO NOT REMOVE.

CH-A1 lab: Prompt-Template Tampering for Persistent Backdoor.
Refuses to start unless CPS_LAB_ENVIRONMENT=1.
"""

from __future__ import annotations

import os
import sys

LAB_ENV_VAR = "CPS_LAB_ENVIRONMENT"
LAB_BANNER = """
================================================================================
  CPS LAB APPLICATION (CH-A1) — DELIBERATELY VULNERABLE
  Prompt-Template Tampering for Persistent Backdoor
  
  This application contains intentional security weaknesses for the purpose
  of validating Chain Potential Score (CPS) predictions. It must not be
  exposed to any network other than localhost. The LLM SDK imports below
  are for AI-BOM detection only; no API calls are made to any provider.
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
