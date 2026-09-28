"""Template + outbound-fetch helpers for the Nexa shopping assistant.

These use the two pinned dependencies that carry Medium SCA advisories, so the
SCA findings correspond to code that genuinely exercises the vulnerable paths.

  - Jinja2 3.0.1   renders assistant reply templates (CVE-2024-56326)
  - requests 2.25.1 fetches catalogue enrichment over HTTP (CVE-2024-35195)
"""

from __future__ import annotations

from typing import Any, Dict

import requests
from jinja2 import Environment, BaseLoader

# NX-13 F1 - Jinja2 3.0.1 sandbox escape surface (CVE-2024-56326, Medium).
# The assistant renders a short reply template. If a future maintainer sources
# any part of the template string from user input, the pinned Jinja2's
# indirect str.format handling is the documented escape path.
_env = Environment(loader=BaseLoader(), autoescape=True)

REPLY_TEMPLATE = "Found {{ count }} item(s) matching your search."


def render_reply(count: int) -> str:
    return _env.from_string(REPLY_TEMPLATE).render(count=count)


# NX-13 F2 - requests 2.25.1 sticky verify=False (CVE-2024-35195, Medium).
# A single early verify=False call poisons cert verification for the lifetime
# of the pooled connection to that host.
_session = requests.Session()


def fetch_enrichment(url: str, insecure_first: bool = False) -> Dict[str, Any]:
    try:
        if insecure_first:
            # Documented trigger for the advisory: the first call disables
            # verification, and the pooled connection keeps ignoring it.
            _session.get(url, verify=False, timeout=3)
        resp = _session.get(url, timeout=3)
        return {"status": resp.status_code}
    except requests.RequestException as e:
        return {"error": str(e)}
