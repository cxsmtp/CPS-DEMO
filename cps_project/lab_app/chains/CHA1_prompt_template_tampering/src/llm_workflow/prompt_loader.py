"""
CH-A1 LAB FINDING #1: Path Traversal in prompt template loader
==============================================================

Engine                 : Checkmarx SAST
Query family           : Path_Traversal (Python)
CWE                    : CWE-22 / CWE-23
Default severity       : Low (per Checkmarx Python_Low_Visibility)
Role in CH-A1          : L2 Bridge — attacker-influenceable file path

The loader accepts a `template_name` from request input and concatenates
it into a file path without canonicalization or allowlist checks. An
attacker who reaches this primitive can read or (with the writable mount
from F3 / F4) overwrite arbitrary files under the prompt directory, including
the system_prompt.txt that the LLM workflow reads on every invocation.

Sink locations marked LAB-VULN-CHA1-F1.
"""

from __future__ import annotations

import os
from pathlib import Path

# Base directory where prompt templates live. The mount on top of this is
# what the IaC chain participants make writable.
PROMPT_BASE_DIR = os.environ.get(
    "CPS_LAB_PROMPT_DIR",
    str(Path(__file__).resolve().parent / "prompts"),
)


def load_prompt_template(template_name: str) -> str:
    """LAB-VULN-CHA1-F1: path concatenation without canonicalization.

    Checkmarx will trace `template_name` (request.args / request.form)
    -> `os.path.join` -> `open()` without an allowlist check.
    """
    # VULN: no allowlist, no canonicalization, no traversal check.
    template_path = os.path.join(PROMPT_BASE_DIR, template_name)
    with open(template_path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_prompt_template(template_name: str, contents: str) -> None:
    """LAB-VULN-CHA1-F1: write path concatenation without sanitization.

    The "admin" (per the lab's threat model: any caller in production)
    can overwrite any file under the prompt directory. Combined with F3
    (writable K8s volume mount), this becomes the chain's terminal step.
    """
    # VULN: same path issue on the write side.
    template_path = os.path.join(PROMPT_BASE_DIR, template_name)
    with open(template_path, "w", encoding="utf-8") as fh:
        fh.write(contents)


def load_system_prompt() -> str:
    """Read the system prompt that ships with every LLM call."""
    return load_prompt_template("system_prompt.txt")
