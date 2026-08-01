"""
Recon endpoints that exercise the disclosed dependency (so SCA flags
it as Used) and provide additional information disclosure surfaces.

These endpoints exist to:
1. Use the F4 SCA-target dependency so it's flagged Used in scan
2. Provide additional /api/info-style disclosure leakage for F2
"""

from __future__ import annotations

import logging
import sys

import requests  # F4 SCA target — older requests has Low CVEs in some tenants
from flask import Flask, jsonify

logger = logging.getLogger("cps.lab.cha2")
logger.setLevel(logging.INFO)


def register_recon_routes(app: Flask) -> None:
    @app.route("/api/info")
    def api_info():
        # F2 amplification: disclose dep versions in response body.
        return jsonify(
            framework_versions={
                "flask_version": _safe_version("flask"),
                "requests_version": _safe_version("requests"),
                "werkzeug_version": _safe_version("werkzeug"),
            },
            python_version=sys.version,
        )

    @app.route("/api/health")
    def api_health():
        # Exercise requests so SCA flags it as Used.
        # The URL is hardcoded — no input flow, no SAST surface.
        try:
            response = requests.head(
                "http://127.0.0.1:1/", timeout=0.001
            )
            status = response.status_code
        except Exception:
            status = "unreachable"
        logger.info("health probe completed")
        return jsonify(status="ok", probe_status=status)


def _safe_version(package_name: str) -> str:
    try:
        module = __import__(package_name)
        return getattr(module, "__version__", "unknown")
    except ImportError:
        return "not-installed"
