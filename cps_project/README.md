# CPS Engine — Session 1 Scaffold

This is the proof-of-concept implementation of the Chain Potential Score
(CPS) framework. Session 1 delivers the engine core: rubric, dimension
defaults, Checkmarx CSV parser, scorer, and CLI.

## Layout

```
cps_project/
├── cps_engine/            # The scoring engine package.
│   ├── __init__.py        # Public API surface.
│   ├── rubric.py          # Section 4 rubric implementation.
│   ├── dimension_defaults.py  # Per-Checkmarx-query default scores.
│   ├── checkmarx_parser.py    # JSON ingestion (Cx One / SARIF / legacy).
│   ├── scorer.py          # Orchestration.
│   └── cli.py             # Command-line entry point.
├── lab_app/               # (Session 4-5) Vulnerable Flask demo.
├── validation/            # (Session 6+) Chain validation harness.
├── tests/
│   └── test_rubric.py     # Unit tests including paper stress cases.
├── sample_data/
│   └── sample_checkmarx_export.csv
├── docs/                  # (To be populated.)
└── conftest.py            # pytest sys.path setup.
```

## Run the tests

```bash
cd cps_project
python -m pytest tests/ -v
```

## Run the CLI against the sample data

```bash
cd cps_project
python -m cps_engine.cli sample_data/sample_checkmarx_export.json
# or test the SARIF path:
python -m cps_engine.cli sample_data/sample_checkmarx_export.sarif.json
```

By default this scores Low and Informational findings only. To include
High and Medium, pass `--all`. To see warnings about query names not in
the defaults table, pass `-v`.

The parser auto-detects three input shapes: Checkmarx One results JSON,
SARIF 2.1.0, and CxSAST legacy JSON. If your tenant's export doesn't
match any of these, the parser tells you what it tried and asks for a
sample so the shape can be added.

## What's next

- Session 2: chain catalog data structure and a few seed chain definitions
  (CH-001 first), plus the chain matcher.
- Session 3: chain-level CPS reporting in the CLI.
- Session 4-5: vulnerable Flask demo containing CH-001's findings wired
  together as the chain anatomy describes.
- Session 6+: validation harness that walks the chain against the demo
  app and reports whether the predicted terminal outcome is achieved.
