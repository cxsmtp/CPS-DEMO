"""
CH-002 lab application — SCA + Container Security chain
========================================================

Minimal Flask app whose only job is to *exercise* the three vulnerable
Python dependencies so SCA flags them as in-use rather than as inactive
manifest entries. The chain story is composition, not application code:

    F1 (Flask 2.0.1, CVE-2026-27205)   - response cache primitive
    F2 (itsdangerous 2.0.1, Low)        - signed-token primitive
    F3 (PyYAML 5.4.1, Low)              - YAML deserialization primitive
    F4 (python:3.11.4-slim Low CVE)     - runtime extension
    F5 (Dockerfile USER root, no HC)    - privilege amplification
    F6 (K8s permissive runtime)         - blast radius amplification

No SAST findings are intentionally designed into this code.

Real-world parallel: the Flask + itsdangerous + PyYAML stack is the
canonical "minimum viable Flask app with config loading and signed
sessions" combination, used by thousands of production deployments.
"""

from __future__ import annotations

import yaml
from flask import Flask, request, session, jsonify
from itsdangerous import URLSafeSerializer

from app.lab_guard import assert_lab_environment


def _load_config() -> dict:
    """Use PyYAML to deserialize a config blob.

    The file path is fixed (config.yaml in the working directory) — no
    user input flows here, so this is not a SAST finding. The point is
    to ensure PyYAML is *imported and called* so SCA flags the
    dependency as in-use. Default to a minimal stub config if the file
    isn't present (so the lab still runs).
    """
    try:
        with open("config.yaml", "r", encoding="utf-8") as fh:
            # yaml.safe_load is the safe variant; we use it deliberately
            # so this code is not itself a SAST finding. The CVE on
            # PyYAML 5.4.1 is a Low-rated regex DoS class, not the
            # historic yaml.load RCE class.
            return yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return {"signing_secret": "lab-stub-do-not-use-in-prod"}


def create_app() -> Flask:
    app = Flask(__name__)
    config = _load_config()
    app.secret_key = config.get("signing_secret", "lab-stub")

    # Use itsdangerous explicitly so SCA flags it as in-use. Flask uses
    # itsdangerous internally for session signing; this redundant import
    # is a guarantee for SCA detection.
    serializer = URLSafeSerializer(app.secret_key)

    @app.route("/")
    def index():
        return jsonify(
            app="cps-ch002-lab",
            warning="lab only — vulnerable dependencies in use",
            libraries=["Flask", "itsdangerous", "PyYAML"],
        )

    @app.route("/sign")
    def sign():
        """Demonstrate itsdangerous in use — signs a fixed payload."""
        token = serializer.dumps({"role": "demo"})
        return jsonify(token=token)

    @app.route("/info")
    def info():
        """Demonstrate Flask's session in use — Flask uses itsdangerous
        internally to sign session cookies."""
        session["last_visit"] = "now"
        return jsonify(session_keys=list(session.keys()))

    return app


def main() -> None:
    assert_lab_environment()
    app = create_app()
    app.run(host="127.0.0.1", port=5060, debug=False)


if __name__ == "__main__":
    main()
