"""
CH-002 lab — recon-to-exploit chain entry point.

The chain story is: F1 (info exposure on errors) + F2 (header disclosure)
+ F3 (weak token generation) provide reconnaissance primitives. F4 (Low
SCA on logging dep) provides a known CVE on the disclosed dep. F5 (AI
agent in AI-BOM with tool access) is the weaponisation contribution.
F6 (NetworkPolicy missing) is the exfiltration path.

Without F5 in the chain, the framework predicts the same Low findings
score in Moderate band (recon-only). With F5, the chain reaches High
band (AI-amplified targeted compromise).
"""

from __future__ import annotations

import logging
import os
import platform
import sys
import traceback

import flask
from flask import Flask, jsonify, request

from app.lab_guard import assert_lab_environment
from app.token_helper import issue_session_token
from app.recon_endpoints import register_recon_routes


def create_app() -> Flask:
    app = Flask(__name__)

    @app.errorhandler(Exception)
    def handle_exception(exc):
        # F1 Information_Exposure_Through_an_Error_Message (Low SAST)
        # The error response includes stack trace, Python version, Flask
        # version, and module path — all reconnaissance signal.
        tb = traceback.format_exc()
        return jsonify(
            error=str(exc),
            error_type=type(exc).__name__,
            stack_trace=tb,
            framework="Flask",
            framework_version=flask.__version__,
            python_version=sys.version,
            platform=platform.platform(),
            module=__name__,
        ), 500

    @app.after_request
    def add_disclosure_headers(response):
        # F2 Information_Exposure_via_Headers (Low SAST)
        # The Server header discloses framework + library versions,
        # enabling targeted CVE lookup against the disclosed deps.
        response.headers["Server"] = f"Flask/{flask.__version__} Python/{sys.version_info.major}.{sys.version_info.minor}"
        response.headers["X-Powered-By"] = "Flask"
        response.headers["X-App-Version"] = "0.1.0-cps-lab"
        return response

    @app.route("/")
    def index():
        return jsonify(
            app="cps-ch002-ai-weaponised-recon-lab",
            warning="lab only — deliberate reconnaissance primitives in use",
            chain="CH-002 AI Weaponisation",
        )

    @app.route("/session/issue")
    def issue_token():
        # Endpoint exercises F3 — weak session token generation.
        token = issue_session_token()
        return jsonify(session_token=token)

    register_recon_routes(app)
    return app


def main() -> None:
    assert_lab_environment()
    app = create_app()
    app.run(host="127.0.0.1", port=5080, debug=False)


if __name__ == "__main__":
    main()
