"""
CH-001 PERIPHERAL SAST FINDINGS
================================

These are not part of the CH-001 primary chain but produce additional
Low findings on scan, exercising more of the CPS engine's defaults table.
"""

from __future__ import annotations

import logging

from flask import Blueprint, request, redirect, make_response

bp = Blueprint("supporting_findings", __name__)
logger = logging.getLogger("lab_app")


# Open_Redirect (CWE-601, Low) ---------------------------------------------
@bp.route("/auth/return")
def auth_return():
    """LAB-VULN: open redirect (Open_Redirect)."""
    next_url = request.args.get("next", "/")
    return redirect(next_url)


# Log_Forging (CWE-117, Low) -----------------------------------------------
@bp.route("/track")
def track_event():
    """LAB-VULN: log forging (Log_Forging)."""
    event = request.args.get("event", "view")
    logger.info("user event: %s", event)
    return {"logged": event}


# Use_of_Hardcoded_Password (CWE-259, Low in v9.7.0; sometimes Medium per tenant)
DB_USER = "lab_user"
DB_PASSWORD = "L4bP@ssw0rd!"  # LAB-VULN: hardcoded credential
DB_HOST = "127.0.0.1"


def get_db_connection_string() -> str:
    """LAB-VULN: hardcoded password in connection string."""
    return f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/labdb"


# Information_Exposure_Through_an_Error_Message (CWE-209, Low) -------------
@bp.route("/calc")
def divide_endpoint():
    """LAB-VULN: returns full exception details to the client."""
    a = int(request.args.get("a", "0"))
    b = int(request.args.get("b", "0"))
    try:
        return {"result": a / b}
    except Exception as exc:
        return {"error": str(exc), "type": type(exc).__name__}, 500


# HttpOnly_Cookie_Flag_Not_Set (CWE-614, Low in JavaScript_Server_Side) ----
@bp.route("/auth/login-naive", methods=["POST"])
def login_naive():
    """LAB-VULN: sets session cookie without HttpOnly/Secure flags."""
    user_id = request.form.get("user_id", "guest")
    resp = make_response({"ok": True})
    resp.set_cookie("user_id", user_id)
    return resp
