# CH-002 — SCA + Container Security Composition (All-Low Chain)

> **Chain anatomy**: a two-engine chain where vulnerable Python
> dependencies (SCA) compose with deliberately-misconfigured container
> runtime (Container Security) into blast-radius amplification. **Every
> required finding is expected to rate Low by Checkmarx.** Chain CPS is
> projected to reach High band (≥ 7.6) via cross-engine composition
> alone, demonstrating the framework's central thesis at maximum
> rhetorical strength: severity-tier triage missing chain-tier risk
> when no individual finding warrants Critical-tier attention.

## Why this chain matters for the paper

CH-001-DEMO and CH-A1 mixed Low + Medium + High findings. Chain CPS
reached High band, but reviewers can argue "CPS just amplified the
existing Medium/High findings." CH-002 closes that gap: every
constituent finding is Low; the High band result emerges purely from
composition.

The chain story is **blast radius amplification**. Vulnerable
dependencies provide the primitives (response cache, signed-token,
YAML deserialization). The deliberately-misconfigured container amplifies
the blast radius (root execution, no healthcheck, retained APT metadata).
The terminal outcome is cross-tenant information leakage in shared
hosting contexts.

## What's in this directory

```
CH002_sca_container_chain/
├── README.md                 # this file
├── Dockerfile                # F4 (base image CVEs), F5/F6 (Dockerfile misconfigs)
├── requirements.txt          # F1, F2, F3 (vulnerable Python deps)
└── src/app/
    ├── __init__.py
    ├── lab_guard.py          # safety guard (env var required to start)
    └── main.py               # minimal Flask app exercising all 3 deps
```

## Chain anatomy

| # | Engine | Finding (expected Low) | Role |
|---|---|---|---|
| F1 | SCA | `CVE-2026-27205` Flask 2.0.1 (CWE-524, response cache leak) | L2 Bridge |
| F2 | SCA | itsdangerous 2.0.1 Low advisory | L2 Bridge |
| F3 | SCA | PyYAML 5.4.1 Low advisory (regex DoS class) | L2 Bridge |
| F4 | Container Security | python:3.11.4-slim base-image package Low CVE | L1 Signal |
| F5 | Container Security | Dockerfile misconfig: USER root + missing HEALTHCHECK (KICS Low) | L3 Amplifier |
| F6 | Container Security | Dockerfile misconfig: ADD instead of COPY + apt lists not cleaned (KICS Low) | L3 Amplifier |

**Hypothesis:** chain CPS lands in High band (≥ 7.6) on engine
math alone, with all six findings rated Low individually.

## How to scan

Add this directory to your Checkmarx One project source (the same
project that scans CH-001 and CH-A1 is fine — the matcher distinguishes
chains by query name and file path). Ensure the scan profile has
**SCA + Container Security + IaC Security** enabled. Container Security
will scan the Dockerfile statically (Branch 1 confirmed in tenant
diagnosis: zero results when no Dockerfile present, findings produced
when Dockerfile added).

After completion, export the Vulnerability Type comprehensive report
and run the matcher:

```
python -m cps_engine.cli sample_data\cx_results.json \
    --aibom sample_data\ai-bom.json --aibom-project-filter "CH01_Lab" \
    --catalog lab_app\chains_index.json --all
```

## Severity substitution loop

If your scan rates F2 (itsdangerous) or F3 (PyYAML) higher than Low,
report back and these will be substituted for fallback candidates:

- F2 fallback: `urllib3 1.26.x` (documented Low cookie-leakage advisory)
- F3 fallback: older `certifi` bundle (typically Low when flagged)
- F1 (Flask 2.0.1) is confirmed Low at 2.3 in your existing scan

## Severity drift to expect

Container Security findings are the most variable across tenants.
Some tenants rate `Use of Add Instead of Copy` as Informational;
some as Low. The `Missing User Instruction` rule is sometimes rated
Medium. The chain matcher reports honest results either way — if
two findings come back Medium, the chain still demonstrates the
central claim, just with slightly less rhetorical purity than
"all-Low → High."
