"""
CH-001 INTERNAL ENDPOINT — chain terminal target
================================================

This blueprint should only be reachable to authenticated requests, but
the canonicalization-buggy auth middleware (Finding #3) lets the attacker
through. Once reachable, it returns cached internal responses keyed by
predictable IDs (Finding #4), so an attacker enumerating IDs reads
records intended for other users.
"""

from __future__ import annotations

from flask import Blueprint, request

from app.utils.insecure_random import (
    INTERNAL_CACHE,
    fetch_internal_response,
    store_internal_response,
)

bp = Blueprint("internal", __name__)


@bp.route("/internal/cache/<rid>")
def read_cache(rid: str):
    record = fetch_internal_response(rid)
    if record is None:
        return {"error": "not found"}, 404
    return {"rid": rid, "data": record}


@bp.route("/internal/cache", methods=["POST"])
def write_cache():
    payload = request.get_json(silent=True) or {}
    rid = store_internal_response(payload)
    return {"rid": rid}


@bp.route("/internal/cache")
def list_cache():
    return {"ids": list(INTERNAL_CACHE.keys())}
