"""
CH-001 LAB FINDING #4: Use of Insufficiently Random Values
==========================================================

Engine                 : Checkmarx SAST
Query family           : Use_of_Insufficiently_Random_Values
                         (also Use_of_Non_Cryptographic_Random in Python)
CWE                    : CWE-330
Default severity       : Low (per Checkmarx v9.7.0 catalog)
Role in CH-001         : L2 Bridge — predicts internal resource identifiers

random.random() / random.randint() (Mersenne Twister, non-cryptographic)
generate session tokens, password reset tokens, and internal cache keys.
MT state is recoverable from observed outputs, so once enough tokens
are seen, an attacker predicts all past and future outputs.
"""

from __future__ import annotations

import random  # LAB-VULN-CH001-F4: non-cryptographic; should be `secrets`
import time

INTERNAL_CACHE: dict[str, dict] = {}


def make_session_token() -> str:
    """LAB-VULN-CH001-F4: session token from non-cryptographic PRNG."""
    return f"sess-{random.randint(10**11, 10**12 - 1)}"


def make_reset_token() -> str:
    """LAB-VULN-CH001-F4: password reset token from non-cryptographic PRNG."""
    return f"reset-{random.random()}"


def make_internal_resource_id() -> str:
    """LAB-VULN-CH001-F4: predictable internal cache key."""
    return f"ires-{int(time.time())}-{random.randint(0, 9999)}"


def store_internal_response(payload: dict) -> str:
    rid = make_internal_resource_id()
    INTERNAL_CACHE[rid] = payload
    return rid


def fetch_internal_response(rid: str) -> dict | None:
    return INTERNAL_CACHE.get(rid)
