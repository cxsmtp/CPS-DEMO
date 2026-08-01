"""
CH-001 LAB FINDING #1: Trust Boundary Violation in Session Variables
====================================================================

Engine                 : Checkmarx SAST
Query family           : Trust_Boundary_Violation_in_Session_Variables
CWE                    : CWE-501
Default severity       : Low (per Checkmarx v9.7.0 catalog, Python_Low_Visibility)
Role in CH-001         : L2 Bridge — entry to internal trust zone

User-controlled HTTP request data is written directly into the Flask
session without sanitization or validation. Downstream code in the
internal blueprint reads from the session expecting vetted values.

Sink locations are marked with LAB-VULN-CH001-F1 so a scan reviewer
can map findings to chain anatomy.
"""

from __future__ import annotations

from flask import Blueprint, request, session

bp = Blueprint("session_handler", __name__)


@bp.route("/auth/setpref", methods=["POST"])
def set_preferences():
    """LAB-VULN-CH001-F1: writes attacker-controlled values straight into session."""
    # Trust boundary violation — no validation, no allowlist.
    session["display_name"] = request.form.get("display_name", "")
    session["preferred_role"] = request.form.get("role", "user")
    session["next_redirect"] = request.form.get("next", "/")
    session["debug_view"] = request.form.get("debug", "0")
    return {"ok": True, "stored": dict(session)}


@bp.route("/auth/setheader", methods=["GET"])
def set_from_header():
    """LAB-VULN-CH001-F1: stores attacker-controlled header into session."""
    forwarded_user = request.headers.get("X-Forwarded-User", "")
    if forwarded_user:
        session["forwarded_user"] = forwarded_user
    return {"ok": True}
