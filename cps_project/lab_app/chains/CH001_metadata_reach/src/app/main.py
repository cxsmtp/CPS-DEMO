"""
CPS Lab App (CH-001 chain) — Flask app factory.

Run:
    export CPS_LAB_ENVIRONMENT=1
    cd chains/CH001_metadata_reach/src
    python -m app.main

Binds to 127.0.0.1:5050 only.
"""

from __future__ import annotations

import logging

from flask import Flask

from app.lab_guard import assert_lab_environment

LAB_BIND_HOST = "127.0.0.1"
LAB_BIND_PORT = 5050


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "lab-secret-do-not-use-anywhere-real"  # noqa: S105

    from app.utils.header_disclosure import (
        install_information_disclosure_middleware,
    )
    install_information_disclosure_middleware(app)

    from app.utils.canonicalization_auth import (
        install_canonicalization_buggy_auth,
    )
    install_canonicalization_buggy_auth(app)

    from app.auth.session_handler import bp as session_bp
    app.register_blueprint(session_bp)

    from app.routes.internal import bp as internal_bp
    app.register_blueprint(internal_bp)

    from app.routes.supporting import bp as supporting_bp
    app.register_blueprint(supporting_bp)

    @app.route("/")
    def index():
        return {"app": "ch01-lab", "warning": "deliberately vulnerable"}

    return app


def main() -> None:
    assert_lab_environment()
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run(host=LAB_BIND_HOST, port=LAB_BIND_PORT, debug=False)


if __name__ == "__main__":
    main()
