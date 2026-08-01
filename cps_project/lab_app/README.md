# CPS Lab — Deliberately Vulnerable Multi-Chain Test Bed

> **This is a research lab artifact. Every file in `chains/` contains
> intentional security weaknesses for the purpose of validating Chain
> Potential Score (CPS) predictions against real Checkmarx One scan
> output. Do not deploy. Do not run against real data. Do not expose
> beyond localhost. Do not `terraform apply`. Do not `pip install -r
> requirements.txt` outside an isolated lab.**

## Structure

```
lab_app/
├── README.md                 # this file
├── chains_index.json         # machine-readable catalog of chains + expected findings
└── chains/
    ├── CH001_metadata_reach/    # SAST + IaC + (peripheral SCA)
    ├── CH002_log4shell/         # SAST + SCA — TBD
    ├── CH003_oauth_hijack/      # SAST + IaC — TBD
    ├── CH006_agentic_exfil/     # AI-BOM + IaC + SAST — TBD
    └── CH008_prompt_tampering/  # AI-BOM + IaC — TBD
```

## Status of chains

| Chain | Status | Engines |
|---|---|---|
| CH-001 Cloud-Metadata Reach | **delivered** | SAST + IaC + (SCA peripheral) |
| CH-002 Log4Shell-Class | not yet delivered | SAST + SCA |
| CH-003 OAuth Hijack | not yet delivered | SAST + IaC |
| CH-006 Agentic Email Exfiltration | not yet delivered | AI-BOM + IaC + SAST |
| CH-008 Prompt-Template Tampering | not yet delivered | AI-BOM + IaC |

Each chain ships in its own subtree. Scan a single chain in isolation
to see only that chain's findings, or scan the whole `chains/` tree to
see the full multi-chain test bed.

## chains_index.json

This file is the bridge between the lab and the CPS engine. It declares,
for each chain, the findings the lab is *intended* to produce and their
roles in the chain anatomy. The chain matcher (Session 2 of the engine)
reads this file plus a real Checkmarx scan output and reports which
chains are fully or partially assembled.

If your scan produces findings not in `chains_index.json`, that's normal
— peripheral findings from supporting code, scanner false positives, and
new query families all show up. The matcher reports them as "extras"
rather than treating them as anomalies.

If your scan does NOT produce findings that `chains_index.json` declared
required, that's the interesting case — it means either (a) the lab
code didn't actually trigger the rule we expected, (b) your tenant's
rule set differs from the one we wrote against, or (c) the engine
preset filtered the rule out. Each case is diagnostic information, and
the matcher logs all three explicitly.

## Recommended scan workflow

```bash
# Start with one chain to validate the workflow.
# Configure Checkmarx One:
#   - Enable SAST + IaC Security + SCA engines
#   - For chains involving AI-BOM (CH-006, CH-008): also enable AI Supply Chain Security
#   - Use Python preset for SAST
#   - Point scan at chains/CH001_metadata_reach/

# Export results-level JSON (not Improved Project Report — aggregate-only).

# Run CPS engine:
python -m cps_engine.cli path/to/scan_results.json -v
```

## What you should see

For CH-001, scan output (Low-filtered) should rank the four primary SAST
findings in the High/Moderate band:

```
   CPS  Band       Query
  ~7.87 High       Trust_Boundary_Violation_in_Session_Variables
  ~7.75 High       Use_of_Insufficiently_Random_Values
  ~7.37 Moderate   Information_Exposure_via_Headers
  ~6.75 Moderate   URL_Canonicalization_Issue
```

Plus IaC findings for `IAM_Policy_With_Resource_Wildcard`,
`Instance_Metadata_Service_v1_Allowed`, plus peripheral findings.

When the chain matcher (Session 2 of the engine) ships, the same scan
will additionally produce:

```
Chain CH-001 (Cloud-Metadata Reach via Internal Trust-Boundary Violation):
  6 of 6 required findings present.
  Aggregate chain CPS: 10.0 (saturated, Critical band)
  Real-world anchor: Capital One 2019.
```

## Safety guards (every chain)

- All Flask apps refuse to start without `CPS_LAB_ENVIRONMENT=1`.
- All Flask apps bind to 127.0.0.1 only.
- Terraform files have placeholder credentials; do not `terraform apply`.
- Kubernetes manifests reference `:0.1.0` images that don't exist; do not
  `kubectl apply` anywhere connected to a real cluster.
- requirements.txt files contain deliberately vulnerable pins; install
  only in isolated environments.
