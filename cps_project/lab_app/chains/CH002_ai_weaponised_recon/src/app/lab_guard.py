"""
Lab environment guard — refuses to start unless CPS_LAB_ENVIRONMENT=1.
"""

from __future__ import annotations

import os
import sys

LAB_ENV_VAR = "CPS_LAB_ENVIRONMENT"
LAB_BANNER = """
================================================================================
  CPS LAB APPLICATION (CH-002 AI Weaponisation) — DELIBERATELY VULNERABLE
  Recon-to-exploit chain demonstrating AI's contribution to chain risk

  This application contains intentional reconnaissance primitives
  (info-exposure, weak token generation, version disclosure) and declares
  an AI agent in the AI-BOM. It is for Chain Potential Score (CPS) AI-delta
  validation only and must not be exposed to any non-localhost network.
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
