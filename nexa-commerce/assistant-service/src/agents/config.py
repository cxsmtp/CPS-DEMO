"""Runtime configuration loader for the Nexa shopping assistant.

Reads config/agent.env. The secret-shaped values there are the NX-12 secret
chain participants; loading them here ties each secret to consuming code.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

_ENV_FILE = Path(__file__).resolve().parents[2] / "config" / "agent.env"


def load_config() -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not _ENV_FILE.exists():
        return values
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    # Fall back to real environment where present.
    for k in list(values):
        values[k] = os.environ.get(k, values[k])
    return values
