"""
CH-001 LAB FINDING #3: URL Canonicalization Issue
=================================================

Engine                 : Checkmarx SAST
Query family           : URL_Canonicalization_Issue
CWE                    : CWE-647
Default severity       : Low (per Checkmarx v9.7.0 catalog)
Role in CH-001         : L2 Bridge — bypasses auth via path-encoding mismatch

before_request decides authentication based on the *raw requested path
string*, while Flask routes the *canonicalized* path. An attacker
submitting a request with mixed encoding, double slashes, or trailing
dot segments can reach internal endpoints whose authorization check
matched the raw form (which "doesn't look internal") but which Flask
routed to the internal handler.
"""

from __future__ import annotations

from flask import Flask, abort, request

INTERNAL_PATH_PREFIXES = (
    "/internal/",
    "/__internal__",
)


def install_canonicalization_buggy_auth(app: Flask) -> None:
    """LAB-VULN-CH001-F3: install auth middleware that uses raw path."""

    @app.before_request
    def _maybe_require_auth():
        # Bug: read raw path, not Flask's canonicalized form.
        raw_path = request.environ.get("RAW_URI") or request.environ.get(
            "REQUEST_URI", request.path
        )
        is_internal_request = any(
            raw_path.startswith(prefix) for prefix in INTERNAL_PATH_PREFIXES
        )
        if is_internal_request and "user_id" not in (request.cookies or {}):
            abort(401)
