# CH-003 — Session Forgery to Account Takeover

Four SAST findings, none rated High by the scanner, composing into full
account takeover without credential theft.

| # | Finding | Tenant severity | Individual CPS | Role |
|---|---|---|---|---|
| F1 | HttpOnly Cookie Flag Not Set | Medium | 6.50 | L1 Signal |
| F2 | Use of Insufficiently Random Values | Low | 7.75 | L2 Bridge |
| F3 | Client Weak Cryptographic Hash | Medium | 6.75 | L2 Bridge |
| F4 | Secret Leak in Error Messages | Low | 6.75 | L3 Amplifier |

**Predicted chain CPS: 9.75 (High band).**

## Chain walkthrough

1. `/login` writes the session cookie with no `HttpOnly` flag (F1), so any
   script executing in the page can read both `sid` and `sig`.
2. The session identifier is `Date.now()` in base36 plus two `Math.random()`
   segments (F2). The timestamp component is disclosed by the response
   `Date` header, so the attacker only has to enumerate the PRNG output.
3. The signature is SHA-1 over `sessionId + ':' + signingKey` (F3) — no HMAC,
   no constant-time comparison, and a hash whose collision cost is now trivial.
4. Calling `/whoami` with a `sid` but no `sig` throws, and the error handler
   returns the raw message — which contains the signing key (F4).

With the key from step 4 and the identifier structure from step 2, the
attacker mints valid `sid`/`sig` pairs for arbitrary users. Steps 1 and 3
are what make steps 2 and 4 reachable and useful.

## Running

Zero dependencies by design, so the SCA surface is empty and the chain is
purely SAST composition.

```
CPS_LAB_ENVIRONMENT=1 node src/server.js
```
