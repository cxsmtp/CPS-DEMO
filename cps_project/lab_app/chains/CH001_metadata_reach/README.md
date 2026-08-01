# CH-001 — Cloud-Metadata Reach via Internal Trust-Boundary Violation

> **Chain anatomy:** SAST findings + IaC findings compose into a chain
> that, on a real cloud workload, terminates in unauthorized retrieval
> of cached internal data and/or service-account credentials from the
> cloud metadata service. Pattern matches the 2019 Capital One breach.

## What's in this directory

```
CH001_metadata_reach/
├── README.md                  # this file
├── src/                       # Python Flask app — produces SAST findings
│   └── app/
│       ├── auth/
│       │   └── session_handler.py        # F1: Trust_Boundary_Violation
│       ├── routes/
│       │   ├── internal.py               # chain terminal endpoint
│       │   └── supporting.py             # peripheral Low findings
│       └── utils/
│           ├── canonicalization_auth.py  # F3: URL_Canonicalization_Issue
│           ├── header_disclosure.py      # F2: Information_Exposure_via_Headers
│           └── insecure_random.py        # F4: Use_of_Insufficiently_Random_Values
├── iac/                       # Infrastructure as Code — produces KICS findings
│   ├── terraform/main.tf      # IAM wildcard, IMDSv1, S3 hygiene
│   └── kubernetes/deployment.yaml  # K8s container hygiene
└── sca/
    └── requirements.txt       # Pinned old dependencies — produces SCA findings
```

## Expected findings on a Checkmarx One scan

When you scan this directory with Checkmarx One (SAST + IaC + SCA engines
enabled), you should see findings across all three engines. The
`chains_index.json` at the parent directory level is the authoritative
machine-readable list of expected findings.

### CH-001 primary chain anatomy (these MUST be present for chain to assemble)

| # | Engine | Query | Severity | Role |
|---|---|---|---|---|
| F1 | SAST | `Trust_Boundary_Violation_in_Session_Variables` | Low | L2 Bridge |
| F2 | SAST | `Information_Exposure_via_Headers` | Low | L1 Signal |
| F3 | SAST | `URL_Canonicalization_Issue` | Low | L2 Bridge |
| F4 | SAST | `Use_of_Insufficiently_Random_Values` | Low | L2 Bridge |
| IAC1 | IaC | `IAM_Policy_With_Resource_Wildcard` | Low | L3 Amplifier |
| IAC2 | IaC | `Instance_Metadata_Service_v1_Allowed` | Low | L2 Bridge |

### Peripheral Low findings (also produced; not part of CH-001 anatomy)

- SAST: `Open_Redirect`, `Log_Forging`, `Use_of_Hardcoded_Password`,
  `Information_Exposure_Through_an_Error_Message`, `HttpOnly_Cookie_Flag_Not_Set`
- IaC (Terraform): `S3_Bucket_Without_Versioning`, `S3_Bucket_Logging_Disabled`,
  `Resource_Without_Tags`, KMS-related findings
- IaC (Kubernetes): `Container_CPU_Limit_Not_Set`, `Container_Memory_Limit_Not_Set`,
  `Service_Account_Token_Automount`
- SCA: vulnerable Flask, Werkzeug, Jinja2, itsdangerous transitively

## How to scan

```bash
# From the repo root, point Checkmarx One at this chain directory only:
#   chains/CH001_metadata_reach/
#
# Enable SAST, IaC Security, and SCA engines.
# Use the Python preset for SAST. KICS auto-detects Terraform and K8s.
```

## How to interpret the CPS engine output

After your scan completes, export results-level JSON (not the Improved
Project Report — that's aggregate-only) and run:

```bash
python -m cps_engine.cli path/to/scan_results.json -v
```

Predicted CPS values for the six chain-anatomy findings:

| Query | Individual CPS |
|---|---|
| `Trust_Boundary_Violation_in_Session_Variables` | ~7.87 (High band) |
| `Use_of_Insufficiently_Random_Values` | ~7.75 (High) |
| `Information_Exposure_via_Headers` | ~7.37 (Moderate) |
| `URL_Canonicalization_Issue` | ~6.75 (Moderate) |
| `IAM_Policy_With_Resource_Wildcard` | TBD — needs IaC scoring entry |
| `Instance_Metadata_Service_v1_Allowed` | TBD — needs IaC scoring entry |

**Chain CPS prediction (Section 4.5 formula, α=0.1, applied to top finding plus
secondary contributions):** if all six are present, chain CPS saturates at 10.0
(Critical band).

## Severity drift to watch for

The published Checkmarx v9.7.0 query catalog rates `Open_Redirect` and
`Use_of_Hardcoded_Password` as **Low**. Live tenants sometimes rate them
**Medium** depending on preset and library version. If your tenant rates
them Medium, the Low-only filter in the CPS engine will exclude them
from chain scoring — that's correct behaviour, but it's also a real
empirical observation worth capturing in the paper.
