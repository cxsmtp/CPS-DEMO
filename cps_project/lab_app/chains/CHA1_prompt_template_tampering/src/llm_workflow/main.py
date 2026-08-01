"""
CH-A1 minimal Flask app — exposes the vulnerable prompt-loading surface
to keep the SAST scanner happy with realistic source-to-sink flows.
"""

from __future__ import annotations

from flask import Flask, request

from llm_workflow.lab_guard import assert_lab_environment
from llm_workflow.prompt_loader import (
    load_prompt_template,
    write_prompt_template,
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return {"app": "cha1-llm-workflow", "warning": "lab only"}

    @app.route("/template/load")
    def template_load():
        """LAB-VULN-CHA1-F1: route exposing path traversal sink."""
        name = request.args.get("name", "system_prompt.txt")
        return {"contents": load_prompt_template(name)}

    @app.route("/template/save", methods=["POST"])
    def template_save():
        """LAB-VULN-CHA1-F1: route exposing the write side of the path traversal."""
        name = request.form.get("name", "system_prompt.txt")
        contents = request.form.get("contents", "")
        write_prompt_template(name, contents)
        return {"saved": name}

    return app


def main() -> None:
    assert_lab_environment()
    app = create_app()
    app.run(host="127.0.0.1", port=5050, debug=False)


if __name__ == "__main__":
    main()
