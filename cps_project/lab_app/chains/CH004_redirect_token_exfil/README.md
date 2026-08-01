# CH-004 — Redirect-to-Token-Exfiltration

Four SAST findings, none rated High by the scanner, composing into
third-party theft of an OAuth access token.

| # | Finding | Tenant severity | Individual CPS | Role |
|---|---|---|---|---|
| F1 | Open Redirect | Medium | 7.12 | L2 Bridge |
| F2 | Information Exposure Through Headers | Low | 6.00 | L1 Signal |
| F3 | Missing HSTS Header | Medium | 4.37 | L3 Amplifier |
| F4 | Use Of HTTP Sensitive Data Exposure | Medium | 6.12 | L2 Bridge |

**Predicted chain CPS: 8.77 (High band).**

## Chain walkthrough

1. Every response advertises `Server`, `X-Powered-By`, `X-App-Version` and
   `X-Backend-Build` (F2). The attacker learns the exact stack and build.
2. `Strict-Transport-Security` is never written (F3), so a browser will
   follow a downgrade to plaintext without complaint.
3. `/oauth/callback` exchanges the authorization code over plaintext `http://`
   and the access token returns on the same channel (F4).
4. The callback then redirects to whatever `return_to` contains, with no
   allow-list, and appends the token to the query string (F1).

Individually: a headers finding, a missing header, a transport finding, and
a redirect finding. Composed: the token leaves the trust boundary attached
to an attacker-controlled URL.

## Running

Zero dependencies by design.

```
CPS_LAB_ENVIRONMENT=1 node src/server.js
```
