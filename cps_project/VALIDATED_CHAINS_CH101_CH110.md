# Five Validated Chains — Observed Evidence Report

**Tenant:** `checkmarx-global-services-internal`
**Validated:** 2026-08-01, live via Checkmarx MCP
**Method:** every constituent finding was read out of a *completed* Checkmarx One
scan. Nothing here is predicted, synthesised, or assumed. Each finding carries
the scan ID and finding ID it came from, so any reviewer with tenant access can
re-check it with `getFindingDetails`.

**The constraint that governs all five chains:** no constituent finding is rated
High or Critical. Every chain is built exclusively from findings Checkmarx rated
**Medium** or **Low** — the tiers that severity-ordered triage defers. A smoke
test enforces this and fails the build if any High or Critical creeps in.

---

## Summary

| Chain | Stack | Findings | Highest constituent | Chain CPS | Band |
|---|---|---|---|---|---|
| CH-101 Predictable Session to Account Takeover | PHP | 3 Med + 2 Low | Medium | **10.00** | High |
| CH-102 Error-Leak to Credential Disclosure | Java | 3 Med + 2 Low | Medium | **9.49** | High |
| CH-103 Config Tamper to Arbitrary File Write | Java | 3 Med + 2 Low | Medium | **9.96** | High |
| CH-104 Redirect to Token Theft | JavaScript / Node | 2 Med + 3 Low | Medium | **9.14** | High |
| CH-105 Container Escape Surface | Docker / K8s (SAST + IaC) | 4 Med + 1 Low | Medium | **9.25** | High |

Five chains, five stacks, 25 findings, zero Highs, every chain in the High band.

---

## Source scans

| Project | Scan ID | Stack |
|---|---|---|
| `cx-andy-schmit/dvwa` | `c389b5e7-34fc-4be6-821b-59cd647c7f0b` | PHP |
| `cx-carolyn-yates/JavaVulnerableLab` | `382c4fa6-5687-4b5a-8205-6ca91269c0fa` | Java |
| `OWASP/NodeGoat Demo` | `b0fa38ca-d352-483a-9197-41f5e1dc0dec` | JavaScript / Node + Docker |
| `cx-jeremy-polansky/authlab-canary` | `2e83d245-5417-4076-a24e-34622e6fd073` | Go (severity corroboration) |
| `owasp-juice-lab` | `b0b1dcd6-4cdc-4a3e-bb66-f689ec8e4999` | Terraform / K8s (severity corroboration) |

---

## CH-101 — Predictable Session to Account Takeover (PHP)

Chain CPS **10.00**. Terminal outcome: full account takeover with no credential theft.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Use of Insufficiently Random Values` | Medium | `/vulnerabilities/weak_id/index.php:17` | `0cKWgAwBbW5DRBdAsAtFgWlDSps=` |
| L2 Bridge | `Broken_or_Risky_Hashing_Function` | Medium | `/vulnerabilities/brute/source/impossible.php:16` | `1vhAEfdo6gX4o01jNtoWlL+5pFw=` |
| L3 Amplifier | `Insecure_Value_of_the_SameSite_Cookie_Attribute` | Medium | `/vulnerabilities/weak_id/source/low.php:11` | `38KP0fXVsu0eaztrIE7FQMvcz3M=` |
| L3 Amplifier | `Cookie_Overly_Broad_Path` | Low | `/vulnerabilities/weak_id/source/low.php:11` | `fJwgEKiARdqTuc14ELI/eHWQNSE=` |
| L1 Signal | `Use_of_Non_Cryptographic_Random` | Low | `/vulnerabilities/weak_id/source/impossible.php:6` | `9nyPzW//SeMEwPhgCqv0U/sDuzg=` |

A non-cryptographic PRNG produces the session identifier. The verifier over it
uses a broken hash. The cookie ships without SameSite protection and with a path
scope broader than the endpoint that issued it. Enumerate the PRNG, forge the
verifier, deliver the cookie cross-site — the session is valid site-wide.

## CH-102 — Error-Leak to Credential Disclosure (Java)

Chain CPS **9.49**. Terminal outcome: credentials and PII reconstructed from
disclosure alone — no injection, no traversal.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Information_Exposure_Through_Query_String` | Medium | `Install.java:57` | `tgntZzrWo1jl7GbAn6d9U92okIU=` |
| L2 Bridge | `Exposure of Sensitive Information to an Unauthorized Actor` | Medium | `ForgotPassword.jsp:10` | `odE2Z3LeAPVEmVcBoqlnC+wBjkc=` |
| L3 Amplifier | `Privacy_Violation` | Medium | `XPathQuery.java:50` | `qJaqS2qGP2h7Yg1/u45ItVUL1F0=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `EmailCheck.java:60` | `467161` |
| L1 Signal | `Heap_Inspection` | Low | `LoginValidator.java:44` | `67831` |

## CH-103 — Config Tamper to Arbitrary File Write (Java)

Chain CPS **9.96**. Terminal outcome: arbitrary file write leading to execution.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `External_Control_of_System_or_Config_Setting` | Medium | `Install.java:57` | `117621` |
| L2 Bridge | `Parameter_Tampering` | Medium | `EmailCheck.java:42` | `oLhf1Sa69rpDxNtxDtYOlWclNgs=` |
| L2 Bridge | `Stored_Relative_Path_Traversal` | Medium | `download_id_union.jsp:24` | `pCeSA+Se0EWYdLfztdcz5VMoa4s=` |
| L3 Amplifier | `Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions` | Low | `AddPage.java:45` | `ppKpfm8TZs9xeAZbkQZ8YK2YDt4=` |
| L3 Amplifier | `Race_Condition` | Low | `Install.java:59` | `MLft8mwUe92v5D6e6BOWNT+gC90=` |

## CH-104 — Redirect to Token Theft (JavaScript / Node)

Chain CPS **9.14**. Terminal outcome: third-party capture of a session token.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Open_Redirect` | Medium | `app/routes/index.js:72` | `/dnIdCbf68zHdxSQp2JaS1OJKzc=` |
| L3 Amplifier | `Missing_HSTS_Header` | Medium | `app/routes/allocations.js:25` | `hm7Z3uvUdX4eYqPsqP0g1+nBdAg=` |
| L3 Amplifier | `Missing_CSP_Header` | Low | `app/routes/allocations.js:25` | `/aEsdK5ud63aXPZ7wiuUUMjW3z0=` |
| L2 Bridge | `Unsafe_Use_Of_Target_blank` | Low | `app/views/tutorial/a7.html:31` | `8606084` |
| L1 Signal | `Log_Forging` | Low | `app/routes/session.js:57` | `jV5Jfp7QHotJ/S1rIqQstuRJCZ8=` |

## CH-105 — Container Escape Surface (cross-engine: SAST + IaC)

Chain CPS **9.25**. Terminal outcome: escape to host, then lateral movement.
The chain's practical significance is that the SAST finding and the IaC findings
are owned by different teams, and neither is escalated alone.

| Role | Query | Engine | Severity | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Use_Of_Hardcoded_Password` | SAST | Medium | `6cZYX5Wlml3T9zR0xiuyTLYhFBI=` |
| L3 Amplifier | `Container Capabilities Unrestricted` | IaC | Medium | `6KfFKsfD633WAC53IIyANWDnYhg=` |
| L3 Amplifier | `Security Opt Not Set` | IaC | Medium | `15674550` |
| L3 Amplifier | `Container Traffic Not Bound To Host Interface` | IaC | Medium | `15674535` |
| L1 Signal | `Healthcheck Instruction Missing` | IaC | Low | `15674561` |

---

## Findings about Checkmarx behaviour surfaced during validation

Three observations that may be useful to the product team.

**1. Query severity is language-preset dependent.** `Use of Insufficiently
Random Values` is rated **Medium** in the PHP preset (DVWA, `weak_id/index.php:17`)
and **Low** in the JavaScript preset. Both are defensible, but it means a
chain catalog — or any cross-language risk model — must bind severity to the
pair *(query, language)* rather than to the query alone. Our rubric now records
the preset alongside every verified severity.

**2. Query-name casing is not stable, even within one scan.** The DVWA scan
`c389b5e7` emits both `Unsafe_Use_Of_Target_blank` (finding `137772`) and
`Unsafe_Use_Of_Target_Blank` (finding `6O5ipx96`). `Use_Of_Hardcoded_Password`
appears in the JavaScript preset while Go emits `Use_of_Hardcoded_Password`.
Any consumer joining on query name needs case-insensitive normalisation or it
will silently split one rule into several.

**3. `listFindings` server-side filters are partially inert.** `engine_type`,
`query_name`, and `language_name` are accepted but ignored server-side (the
response flags this under `notes`). Only `severity`, `state`, and `status`
actually narrow the result set, which makes locating SAST findings inside a
large mixed scan a paging exercise — in the NodeGoat scan the SAST Medium block
began at offset 4 of 13 pages, behind ~80 SCA rows. A working `engine_type`
filter would materially reduce round-trips for agent-driven workflows.

---

## Reproducing

```bash
python -m cps_engine.cli sample_data/observed_dvwa_ch101.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_javavulnlab_ch102_ch103.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_nodegoat_ch104_ch105.json \
    --catalog lab_app/chains_index.json --all
python run_smoke_tests.py      # 34/34
```

Each fixture reproduces its own chains at the CPS values above and reports the
other chains as NOT_ASSEMBLED — the negative control showing the matcher
requires the catalog's declared composition rather than matching on
co-occurrence.


---

# Second batch — CH-106 to CH-110

Same method, same tenant, validated 2026-08-01. Two of these are new in kind:
CH-106 is built entirely from **Informational** findings, and CH-107 is built
from a **production AI agent framework** rather than a deliberately vulnerable lab.

| Chain | Stack | Composition | Chain CPS |
|---|---|---|---|
| CH-106 Informational-Only Chain to Silent Data Exfiltration | Java | **5 Informational** | **9.15** |
| CH-107 Agent Tool-Path Error Disclosure | Python / OpenAI Agents SDK | 1 Med + 4 Low | **9.78** |
| CH-108 Defence-in-Depth Erosion to Session Ride | PHP | 3 Med + 2 Low | **9.24** |
| CH-109 Cloud Exfiltration Blindness | Terraform / AWS | 5 Med | **8.32** |
| CH-110 API Auth Weakening to Token Forgery | Go | 2 Med + 1 Low | **8.01** |

## CH-106 — the Informational-only result

Scan `382c4fa6`, project `cx-carolyn-yates/JavaVulnerableLab`. Every constituent
is rated **Information** — the tier *below* Low, which most programs never render
in a backlog at all.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Dynamic_SQL_Queries` | Information | `LoginValidator.java:52` | `0XBp02QSHGEql4giNp73keCA3Es=` |
| L3 Amplifier | `Insufficient_Logging_of_Database_Actions` | Information | `change-email.jsp:32` | `12jj98OpDWTFsrU0lpG1XUagp/Y=` |
| L2 Bridge | `Pages_Without_Global_Error_Handler` | Information | `admin.jsp:1` | `0tZuTNbFjEN8ykwCCIAbRU3KNJA=` |
| L1 Signal | `Unchecked_Error_Condition` | Information | `Logout.java:42` | `3iWHH6gMkWJLKli9QiunyCCQIG0=` |
| L1 Signal | `Use_of_System_Output_Stream` | Information | `DisplayMessage.jsp:35` | `0APbv9DRr/LUAZserU2/2fSPWus=` |

Queries are assembled dynamically, so the injection surface exists. Database
actions are not logged, so exploitation leaves no trail. There is no global error
handler, so failures surface raw. Error conditions are returned but never acted
on. Internal detail goes to the system output stream. **Chain CPS 9.15 — High.**

## CH-107 — the AI agent framework chain

Scan `5797794c`, project `AISC_openai_agents_python`. This is not a lab; it is an
agent framework's own source tree. The same error-disclosure rule fires 23 times
across it, concentrated in the paths that matter most.

| Role | Query | Severity | Code path | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Object_Access_Violation` | Medium | `/src/agents/tool.py:1284` | `p9H+6K7MHD/gKWBQ699t5SEO4Pw=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/mcp/util.py:296` | `gPZSEBzeEMW5I9wlkSoHqZvh4eQ=` |
| L2 Bridge | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/run_internal/tool_actions.py:130` | `FRtCxgpOBDPuQtV+qNVxGbJ97BQ=` |
| L2 Bridge | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/run_internal/session_persistence.py:479` | `NwUJPu9T7HKfoPXIvLPqn011OpM=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/tracing/provider.py:95` | `32+Yo0mzZGU30FIJH3+Qi0oLngA=` |

Individually: five error messages that are slightly too helpful. Composed: the
agent's tool schema, its MCP wiring, its session storage semantics and its trace
identifiers — the reconnaissance an attacker needs to craft a tool-poisoning
payload the model will faithfully execute. **Chain CPS 9.78 — High.**

This chain required an engine change. Four participants share one query name and
are distinguished by code path, so required findings now support
`match_file_contains`. A regression test asserts each scoped participant matches
exactly one finding.

## CH-108, CH-109, CH-110

- **CH-108** (PHP, DVWA `c389b5e7`): `CSRF` + `Exposure of Sensitive Information to an Unauthorized Actor` + `Missing_HSTS_Header` (Medium) with `Improper_Exception_Handling` + `Information_Exposure_Through_an_Error_Message` (Low). Every barrier around an authenticated admin session removed one Medium at a time. **9.24**
- **CH-109** (Terraform/AWS, owasp-juice-lab `b0b1dcd6`): `IAM policy allows for data exfiltration`, `S3 Bucket Logging Disabled`, `RDS Without Logging`, `RDS With Backup Disabled`, `Using Unrecommended Namespace` — all Medium. Exfiltration permitted by policy, invisible to telemetry, unrecoverable from backup. **8.32**
- **CH-110** (Go, authlab-canary `2e83d245`): `Use_of_Hardcoded_Password` + `Client_Weak_Cryptographic_Hash` (Medium) with `JWT_No_Claims_Directives_Validation` (Low). Key material, reproducible derivation, unvalidated claims — token forgery. **8.01**

## Fourth Checkmarx finding: AISC results are not exposed via listFindings

No `aisc`-typed result appears at any severity tier through `listFindings`, on any
scan we queried, including scans whose engine list contains `aisc`. AI-BOM
component detection appears to be reachable only through the CycloneDX export
path. For agent-driven workflows this means AI inventory cannot be correlated with
SAST/SCA/IaC findings in a single API surface — which is precisely what
chain-aware analysis of AI systems needs. CH-107 therefore carries its AI
inventory as declared context, with component-detection accuracy validated
separately (7 of 10 detected in the earlier CH-A1 run).

## Reproducing batch two

```bash
for f in observed_javavulnlab_ch106 observed_openai_agents_ch107 \
         observed_dvwa_ch108 observed_juicelab_ch109 observed_authlab_ch110; do
  python -m cps_engine.cli sample_data/$f.json --catalog lab_app/chains_index.json --all
done
python run_smoke_tests.py     # 36/36
```
