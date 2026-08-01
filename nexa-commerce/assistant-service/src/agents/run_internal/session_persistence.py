"""Conversation session storage for the Nexa shopping assistant."""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List

SESSION_DB = os.environ.get("NEXA_ASSISTANT_DB", "assistant-sessions.sqlite")


class SessionStoreError(RuntimeError):
    pass


def _connect() -> sqlite3.Connection:
    cx = sqlite3.connect(SESSION_DB)
    cx.execute(
        "CREATE TABLE IF NOT EXISTS sessions "
        "(id TEXT PRIMARY KEY, turns TEXT NOT NULL)"
    )
    return cx


def load_turns(session_id: str) -> List[Dict[str, Any]]:
    """Load a conversation's turns.

    CH-107 F4 - Information_Exposure_Through_an_Error_Message (expect: Low)

    The failure path returns the on-disk store location, the schema and the
    raw driver message, which together describe how sessions are keyed and
    therefore how one could be replayed.
    """
    try:
        cx = _connect()
        row = cx.execute(
            "SELECT turns FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return json.loads(row[0]) if row else []
    except (sqlite3.Error, ValueError) as exc:
        raise SessionStoreError(
            "session load failed for '{sid}': {exc}; store={store}; "
            "schema=sessions(id TEXT PRIMARY KEY, turns TEXT)".format(
                sid=session_id, exc=exc, store=os.path.abspath(SESSION_DB)
            )
        ) from exc


def save_turns(session_id: str, turns: List[Dict[str, Any]]) -> None:
    cx = _connect()
    cx.execute(
        "INSERT OR REPLACE INTO sessions (id, turns) VALUES (?, ?)",
        (session_id, json.dumps(turns)),
    )
    cx.commit()
