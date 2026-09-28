# CPS Project — knowledge index

Chain Potential Score (CPS): a framework arguing that individually low-severity
findings compose into high-impact exploit chains, and that AI lowers the cost of
weaponizing them. This bundle is the complete working set.

## Deliverables

| File | What it is |
|---|---|
| `../reports/Nexa_Commerce_Chains.xlsx` | **Primary.** 13 chains in the self-built Nexa specimen. Sheets: Chains, Findings & Engines (per-finding engine + severity + file + result ID), Attack Paths (step-by-step exploitation), Validation & Method. |
| `../reports/CPS_Chain_Catalogue.xlsx` | 22 chains across the broader research pool, with per-finding Checkmarx traceability. |
| `../reports/CPS_Triage_FalsePositives.xlsx` | Four proposed NOT_EXPLOITABLE findings with data-flow reasoning, plus the reviewed-and-kept set. |
| `FINAL_TEN_CHAINS.md` | Narrative catalogue of the ten validated chains with provenance. |
| `SCAN_RESULTS_EVIDENCE.md` | Per-chain scan evidence with triage-queue context. |
| `CHAIN_MAP.md` | Every finding mapped to file and expected severity in the specimen. |
| `LINKEDIN_POST.md` | Leader-level thought-leadership post drafted for publishing. |
| `PUSH_AND_SCAN.md` | Runbook to push the v3 specimen and re-scan. |
| `../nexa-commerce/` | The full specimen codebase, in place (all engine surfaces: SAST, SCA, IaC, secrets, AI-BOM). |
| `../cps_project/` | The CPS engine, catalogues, fixtures and tests. |
| `../reports/` | All three workbooks. |

## Status (as of this bundle)

- Ten chains validated against real Checkmarx scans; specimen scans clean of High/Critical.
- Three additional engine surfaces (secrets, AI-BOM, SCA) are coded in v3 but not yet
  confirmed in the repo — pending a push of the v3 bundle and a re-scan.
- Repo: github.com/cxsmtp/CPS-DEMO  (project id d182f9ec-bb1e-40fb-9b79-12dbb96f7f1c)

## Key methodology findings (for Checkmarx)

1. Query severity is language-preset dependent.
2. Query-name casing is unstable, even within one scan.
3. Query names vary across presets for the same rule.
4. listFindings server-side engine/query filters are partly inert.
5. AISC / AI-BOM results are not exposed via listFindings — CycloneDX export only.
