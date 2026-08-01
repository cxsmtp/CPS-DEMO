"""
CH-A1 LAB FINDING #2: Use of Hardcoded Credentials
==================================================

Engine                 : Checkmarx SAST
Query family           : Use_of_Hardcoded_Password / Use_Of_Hardcoded_Credentials
CWE                    : CWE-259 / CWE-798
Default severity       : Low (Checkmarx v9.7.0 Python_Low_Visibility)
                         (some tenants rate Medium — see severity drift discussion)
Role in CH-A1          : L1 Signal — peripheral chain Low; recon material

Hardcoded API keys for LLM providers. These are obvious-fake placeholder
strings used purely as Checkmarx detection bait — no real key has the
exact `LAB_NEVER_REAL_*` prefix below.

LAB-VULN-CHA1-F2 markers below.
"""

from __future__ import annotations

# LAB-VULN-CHA1-F2: hardcoded LLM provider keys (placeholder strings only).
OPENAI_API_KEY = "sk-LAB_NEVER_REAL_openai_placeholder_do_not_use_0000"
ANTHROPIC_API_KEY = "sk-ant-LAB_NEVER_REAL_anthropic_placeholder_0000"
GOOGLE_API_KEY = "LAB_NEVER_REAL_google_placeholder_0000"
COHERE_API_KEY = "LAB_NEVER_REAL_cohere_placeholder_0000"
MISTRAL_API_KEY = "LAB_NEVER_REAL_mistral_placeholder_0000"


def get_provider_key(provider: str) -> str:
    """LAB-VULN-CHA1-F2: returns hardcoded credentials based on provider."""
    keys = {
        "openai": OPENAI_API_KEY,
        "anthropic": ANTHROPIC_API_KEY,
        "google": GOOGLE_API_KEY,
        "cohere": COHERE_API_KEY,
        "mistral": MISTRAL_API_KEY,
    }
    return keys.get(provider, "")
