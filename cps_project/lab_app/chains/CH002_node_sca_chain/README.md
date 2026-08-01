# CH-002 — SCA + Container Security Composition (Cleansed Design)

> **Chain anatomy**: a focused two-engine chain. Two pinned vulnerable
> npm libraries (cookie + debug) compose with deliberately-misconfigured
> Dockerfile + base-image package CVEs into blast-radius amplification.
> **Goal: every chain participant rates Low or Medium-Low. SAST returns
> zero chain-relevant findings.**

## Why this lab is structured this way

Three earlier iterations of CH-002 informed this design:

1. **v0.0 (Python, Flask + itsdangerous + PyYAML)** — itsdangerous and
   PyYAML returned zero advisories in the test tenant. Partial chain.
2. **v0.1 (Node, Express + mime + semver + ms)** — Express transitives
   pulled 3 High-rated CVEs (path-to-regexp x2, semver). Defeats the
   no-Highs constraint. Six SCA findings, three of them High.
3. **v0.2 (current)** — Express dropped entirely. Direct-only deps:
   cookie + debug, both confirmed Low/Medium-Low in v0.1 tenant scan.
   SAST surface eliminated by removing all input flow from app code.

## What's in this directory

```
CH002_node_sca_chain/
├── README.md                 # this file
├── .cxignore                 # excludes node_modules from SAST scan
├── package.json              # cookie + debug as direct dependencies
├── Dockerfile                # F3-F6 — Container Security findings
└── src/
    ├── index.js              # entry point — calls libs with hardcoded args
    ├── lab_guard.js          # safety guard
    ├── cookie_lib.js         # cookie.parse with hardcoded header
    └── debug_lib.js          # debug logger with hardcoded namespace
```

## Chain anatomy

| # | Engine | Finding (expected Low/Medium-Low) | Role |
|---|---|---|---|
| F1 | SCA | cookie 0.6.0 — CVE-2024-47764 (out-of-bounds chars) | L2 Bridge |
| F2 | SCA | debug 2.6.9 — Cx8bc4df28-fcf5 (ReDoS class) | L2 Bridge |
| F3 | Container Security | Healthcheck Instruction Missing (KICS Low) | L1 Signal |
| F4 | Container Security | Apt Get Install Lists Were Not Deleted (KICS Info) | L3 Amplifier |
| F5 | Container Security | APT-GET Not Avoiding Additional Packages (KICS Info) | L3 Amplifier |
| F6 | Container Security | Low-rated base-image package CVE (one of node:20-slim's) | L1 Signal |

**Hypothesis:** chain CPS lands in High band on these 6 findings. Five
are confirmed Low/Info in tenant scan of v0.1; F6 needs identification.

## SAST cleanliness

The lab code is structured to produce zero chain-relevant SAST findings:

- No `req.query`, `req.body`, `req.params` — no taint sources
- No `Math.random()` — no Insufficiently Random Values
- No `Buffer(string)` constructor — no Deprecated Functions
- No `console.error(err)` — no Secret Leak in Error Messages
- No HTTP server — no HSTS / Cookie Flag findings
- No deprecated APIs (crypto.createCredentials, etc.)
- No switch statements — no Missing Default Case findings

Plus `.cxignore` excludes `node_modules/` so transitive code doesn't
get SAST-scanned. **Configure path exclusion in Checkmarx One Project
Settings → Scan Configuration → Source Exclusions: `**/node_modules/**`.**

## Pre-scan checklist

Before scanning:

1. From this directory, run `npm install` (regenerates lockfile + node_modules)
2. **Configure SAST source exclusion in Checkmarx One** to exclude
   `**/node_modules/**`. This is the most important step — without it,
   transitive code in `node_modules` will produce dozens of SAST
   findings that have nothing to do with the lab.
3. Add this directory to the project source upload (zip excluding
   node_modules/ is fine; the lockfile alone tells SCA what to look at)
4. Enable SAST + SCA + Container Security + IaC Security in scan profile
5. Scan

## Substitution loop

| If this returns 0 advisories | Substitute with |
|---|---|
| cookie 0.6.0 | jsonwebtoken (older version with Low CVE) |
| debug 2.6.9 | ms 2.0.0 (if it flags this time) |

## Honest expectations

- **Likely outcome**: cookie + debug both flag Low advisories, 4-5
  Container Security findings on the Dockerfile fire (Low/Info), and
  maybe 1-2 Low base-image CVEs surface from node:20-slim. Chain
  assembles at CPS in the High band.
- **Possible outcome**: 1 of cookie/debug returns zero advisories. We
  substitute one library and re-scan once.
- **Worst case**: SAST exclusion isn't configured and node_modules
  produces dozens of transitive findings. Nothing breaks the chain;
  the SAST noise is just present in per-finding output.
