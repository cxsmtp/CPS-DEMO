"""
CH-001 LAB FINDING #2: Information Exposure via Headers
========================================================

Engine                 : Checkmarx SAST
Query family           : Information_Exposure_via_Headers
CWE                    : CWE-200
Default severity       : Low (per Checkmarx v9.7.0 catalog)
Role in CH-001         : L1 Signal — reveals internal endpoint topology

Custom response headers disclose framework version, internal service
routing identifiers, and debug build tags. Pure recon material — no
credentials, but lets an attacker fingerprint the stack and select
known exploits or chain primitives.
"""

from __future__ import annotations

from flask import Flask

INTERNAL_BUILD_ID = "build-2026.04.r17-internal"
INTERNAL_ROUTE_ID = "internal-router-tier-3"
FRAMEWORK_BANNER = "Flask/3.0.x — lab-app/0.1.0"


def install_information_disclosure_middleware(app: Flask) -> None:
    """LAB-VULN-CH001-F2: middleware leaking internal state in headers."""

    @app.after_request
    def _add_debug_headers(response):
        response.headers["X-Powered-By"] = FRAMEWORK_BANNER
        response.headers["X-Internal-Build"] = INTERNAL_BUILD_ID
        response.headers["X-Internal-Route"] = INTERNAL_ROUTE_ID
        response.headers["X-Session-Inspector"] = "available-via-/__internal__"
        return response
