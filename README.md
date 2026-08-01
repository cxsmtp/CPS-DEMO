# CPS Demo — Chain Potential Score

This repository is a self-contained demonstration of the **Chain Potential
Score (CPS)** framework: a way of scoring vulnerability *chains* rather than
individual findings, so that a set of weaknesses each triaged as "won't fix
this sprint" is surfaced when — composed — it reaches the High band on chain
risk.

It has two halves that are meant to be read together:

| Directory | What it is |
|---|---|
| [`cps_project/`](cps_project/) | The **scoring engine**. Rubric, per-query dimension defaults, a Checkmarx result parser (Checkmarx One / SARIF / legacy JSON), the scorer, a CLI, the chain catalog + matcher, unit tests, and the evidence pack. |
| [`nexa-commerce/`](nexa-commerce/) | The **specimen**. A small but real e-commerce app across seven technology stacks, built so that *no* application-code or IaC finding rates High or Critical, yet ten distinct vulnerability chains compose into the High band. |

## The point in one paragraph

Every constituent of every chain in `nexa-commerce/` sits at **Medium, Low or
Informational** — the tiers a severity-ordered backlog defers. Taken finding by
finding, each is something a security programme closes as low priority. Composed,
each of the ten chains reaches the High band on chain risk. CH-106 is the extreme
case: all five of its constituents are rated *Informational* (the tier below Low,
which most programmes never even render in the backlog), and the chain still
scores 9.15. See [`nexa-commerce/CHAIN_MAP.md`](nexa-commerce/CHAIN_MAP.md) for
the finding-by-finding map and [`cps_project/SCAN_RESULTS_EVIDENCE.md`](cps_project/SCAN_RESULTS_EVIDENCE.md)
for the evidence pack.

## Quick start

Run the engine's unit tests:

```bash
cd cps_project
python -m pytest tests/ -q
```

Dry-run the chain verifier against the specimen using the expected-shape
fixture (no Checkmarx scan required — this proves the harness and catalog are
consistent, not that a scan will emit these findings):

```bash
cd nexa-commerce
PYTHONPATH=../cps_project python3 verify_chains.py expected_scan_shape.json
```

Expected output ends with:

```
Chains fully assembled: 10 of 10
No High or Critical findings present.
```

Score a real Checkmarx export through the CLI:

```bash
cd cps_project
python -m cps_engine.cli sample_data/sample_checkmarx_export.json
```

## Verifying against a live scan

Scan the specimen and run the verifier over the real export:

```bash
cd nexa-commerce
./scan.sh Nexa-Commerce main
cx results show --scan-id <SCAN_ID> --report-format json --output-name nexa-results
PYTHONPATH=../cps_project python3 verify_chains.py nexa-results.json
```

The verifier reports, per chain, which required findings fired and at what
severity, flags any severity drift from the catalog, and fails if any High or
Critical finding is present.

## A warning that should not need saying

Every weakness in `nexa-commerce/` is intentional. Do not deploy it, do not
lift code from it, and do not point it at anything you care about. It exists to
be scanned.
