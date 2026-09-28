# CPS-DEMO — Chain Potential Score

Research artefact for the **Chain Potential Score (CPS)**: a framework showing that
individually low-severity findings compose into high-impact exploit chains, and
that AI collapses the cost of composing them.

Headline result: a working exploit chain built **entirely from Informational
findings** scores in the High band on impact. A team would clear 554 higher-rated
findings before the first constituent was even displayed.

## Layout

| Path | What it is |
|---|---|
| `nexa-commerce/` | **The specimen.** A working polyglot e-commerce app (PHP, Java, Node, Go, Python, Terraform, K8s, Docker) that reproduces 13 chains in one codebase with zero High or Critical findings from application code or IaC. v3 — carries SAST, SCA, IaC, secret-detection and AI-BOM surfaces. |
| `cps_project/` | **The engine.** CPS scoring rubric, chain matcher, Checkmarx parser, chain catalogues, fixtures, workbook generators, 36 automated tests. |
| `reports/` | **The workbooks.** Chain catalogue with attack paths, broader research catalogue, false-positive triage. |
| `docs/` | **The write-ups.** Validated chains, scan evidence, chain map, runbooks, brief, LinkedIn drafts. |

## Start here

- **`reports/Nexa_Commerce_Chains.xlsx`** — 13 chains, 60 findings across five engines, each with the detecting engine, vulnerability name, severity, file, result ID, and a step-by-step attack path.
- **`docs/FINAL_TEN_CHAINS.md`** — the ten validated chains with full provenance.
- **`docs/CHAIN_MAP.md`** — every finding mapped to its file and expected severity in the specimen.

## Reproduce

```bash
# Score and match chains against a Checkmarx export
cd cps_project && python run_smoke_tests.py              # 36/36

# Scan the specimen (all engines) and verify every chain
cd nexa-commerce && ./scan.sh Nexa-Commerce main
PYTHONPATH=../cps_project python verify_chains.py <export>.json
```

Full push-and-scan runbook: `docs/PUSH_AND_SCAN.md`.

## Method in one paragraph

Findings are read out of *completed* Checkmarx One scans with the severity
already assigned — no prediction step. Each is scored on five dimensions
(Prevalence 0.15, Chain Utility 0.30, AI Leverage 0.25, Blast Radius 0.15,
Impact Proximity 0.15), then a chain scores `max + 0.1 × sum(rest)`, capped at
10. A guard test fails the build if any High or Critical enters a chain; a
negative control confirms each fixture assembles only its own chains.

## Status

- Ten chains validated against real scans; the specimen scans clean of High/Critical.
- Secrets, AI-BOM and SCA chains (NX-11..13) are coded in v3 and pending confirmation on the next scan.
- Checkmarx project `CPS-DEMO` · id `d182f9ec-bb1e-40fb-9b79-12dbb96f7f1c`.

## Five observations for Checkmarx

1. Query severity is language-preset dependent.
2. Query-name casing is unstable, even within one scan.
3. Query names vary across presets for the same rule.
4. `listFindings` engine/query filters are partly inert server-side.
5. AISC / AI-BOM results are not exposed via `listFindings` — CycloneDX export only.

> Every weakness in `nexa-commerce/` is intentional. Do not deploy it.
