# The Ten Chains

*Chain Potential Score — validated chain catalogue*

Ten vulnerability chains. **48 constituent findings. Zero High. Zero Critical.**
Every chain reaches the High band on composite risk.

Each finding below was read out of a *completed* Checkmarx One scan in the
`checkmarx-global-services-internal` tenant, with the severity Checkmarx
assigned. Nothing is predicted or synthesised. Finding IDs are re-checkable
by any reviewer with tenant access via `getFindingDetails(scan_id, finding_id)`.

---

## Summary

| Chain | Stack | Composition | Top severity | Ranked ahead in queue | Chain CPS |
|---|---|---|---|---|---|
| **CH-101** Predictable Session to Account Takeover | PHP | 3 Med + 2 Low | Medium | 163 (59 C + 104 H) | **10.00** |
| **CH-102** Error-Leak to Credential Disclosure | Java | 3 Med + 2 Low | Medium | 243 (124 C + 119 H) | **9.49** |
| **CH-103** Config Tamper to Arbitrary File Write | Java | 3 Med + 2 Low | Medium | 243 (124 C + 119 H) | **9.96** |
| **CH-104** Redirect to Token Theft | JavaScript / Node | 2 Med + 3 Low | Medium | 384 (84 C + 300 H) | **9.14** |
| **CH-105** Container Escape Surface | Docker / Compose | 4 Med + 1 Low | Medium | 384 (84 C + 300 H) | **9.25** |
| **CH-106** Informational-Only Chain to Silent Data Exfiltration | Java | 5 Info | Information | 554 (every C/H/M/L) | **9.15** |
| **CH-107** Agent Tool-Path Error Disclosure | Python (AI agent framework) | 1 Med + 4 Low | Medium | 23 (16 C + 7 H) | **9.78** |
| **CH-108** Defence-in-Depth Erosion to Credentialed Session Ride | PHP | 3 Med + 2 Low | Medium | 163 (59 C + 104 H) | **9.24** |
| **CH-109** Cloud Exfiltration Blindness | Terraform / AWS / K8s | 5 Med | Medium | 15 (3 C + 12 H) | **8.32** |
| **CH-110** API Auth Weakening to Token Forgery | Go | 2 Med + 1 Low | Medium | 36 (12 C + 24 H) | **8.01** |

The fifth column is the argument. A severity-ordered backlog reaches each chain
only after clearing everything above it. For CH-106 that means clearing 554
findings — every Critical, High, Medium and Low in an 860-finding scan — before
the first constituent is even rendered. The chain scores 9.15.

---

## Source scans

| Project | Scan ID | Stack |
|---|---|---|
| `cx-andy-schmit/dvwa` | `c389b5e7-34fc-4be6-821b-59cd647c7f0b` | PHP |
| `cx-carolyn-yates/JavaVulnerableLab` | `382c4fa6-5687-4b5a-8205-6ca91269c0fa` | Java |
| `OWASP/NodeGoat Demo` | `b0fa38ca-d352-483a-9197-41f5e1dc0dec` | JavaScript / Node |
| `AISC_openai_agents_python` | `5797794c-4ea0-4553-a883-c908a6fec287` | Python (AI agent framework) |
| `owasp-juice-lab` | `b0b1dcd6-4cdc-4a3e-bb66-f689ec8e4999` | Terraform / AWS / K8s |
| `cx-jeremy-polansky/authlab-canary` | `2e83d245-5417-4076-a24e-34622e6fd073` | Go |

---

## CH-101 — Predictable Session to Account Takeover (PHP)

**Chain CPS 10.00 (High).** Source: `cx-andy-schmit/dvwa` scan `c389b5e7-34fc-4be6-821b-59cd647c7f0b`.

Full account takeover with no credential theft. A non-cryptographic PRNG generates the session identifier (F1, F5), the verifier over it uses a broken hash (F2), the cookie is delivered without SameSite protection (F3), and its path scope is broader than the issuing endpoint (F4). Enumerate the PRNG, forge the verifier, deliver the cookie cross-site, and the session is valid site-wide. Highest-severity constituent is Medium.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Use of Insufficiently Random Values` | Medium | `/vulnerabilities/weak_id/index.php:17` | `0cKWgAwBbW5DRBdAsAtFgWlDSps=` |
| L2 Bridge | `Broken_or_Risky_Hashing_Function` | Medium | `/vulnerabilities/brute/source/impossible.php:16` | `1vhAEfdo6gX4o01jNtoWlL+5pFw=` |
| L3 Amplifier | `Insecure_Value_of_the_SameSite_Cookie_Attribute` | Medium | `/vulnerabilities/weak_id/source/low.php:11` | `38KP0fXVsu0eaztrIE7FQMvcz3M=` |
| L3 Amplifier | `Cookie_Overly_Broad_Path` | Low | `/vulnerabilities/weak_id/source/low.php:11` | `fJwgEKiARdqTuc14ELI/eHWQNSE=` |
| L1 Signal | `Use_of_Non_Cryptographic_Random` | Low | `/vulnerabilities/weak_id/source/impossible.php:6` | `9nyPzW//SeMEwPhgCqv0U/sDuzg=` |

*Nexa Commerce reproduction:* `storefront/public/lib/session.php` — 2 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-102 — Error-Leak to Credential Disclosure (Java)

**Chain CPS 9.49 (High).** Source: `cx-carolyn-yates/JavaVulnerableLab` scan `382c4fa6-5687-4b5a-8205-6ca91269c0fa`.

Reconstruction of user credentials and PII from disclosure alone. Query strings carry sensitive values into logs and referers (F1), an unauthorised actor can reach sensitive responses (F2), PII flows into sinks that were never meant to hold it (F3), error messages return internal state (F4), and credentials sit unscrubbed in heap-resident objects (F5). No injection, no traversal, no High-rated finding.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Information_Exposure_Through_Query_String` | Medium | `/src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:57` | `tgntZzrWo1jl7GbAn6d9U92okIU=` |
| L2 Bridge | `Exposure of Sensitive Information to an Unauthorized Actor` | Medium | `/src/main/webapp/ForgotPassword.jsp:10` | `odE2Z3LeAPVEmVcBoqlnC+wBjkc=` |
| L3 Amplifier | `Privacy_Violation` | Medium | `/src/main/java/org/cysecurity/cspf/jvl/controller/XPathQuery.java:50` | `qJaqS2qGP2h7Yg1/u45ItVUL1F0=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `/src/main/java/org/cysecurity/cspf/jvl/controller/EmailCheck.java:60` | `467161` |
| L1 Signal | `Heap_Inspection` | Low | `/src/main/java/org/cysecurity/cspf/jvl/controller/LoginValidator.java:44` | `67831` |

*Nexa Commerce reproduction:* `catalog-service/src/main/java/com/nexa/catalog/` — 1 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-103 — Config Tamper to Arbitrary File Write (Java)

**Chain CPS 9.96 (High).** Source: `cx-carolyn-yates/JavaVulnerableLab` scan `382c4fa6-5687-4b5a-8205-6ca91269c0fa`.

Arbitrary file write leading to code execution. Attacker-controlled input reaches a system or config setting (F1), request parameters are trusted for authorisation-relevant decisions (F2), and a stored relative path is resolved without canonicalisation (F3). A temp file created with permissive permissions (F4) plus a race window on the write (F5) turn the traversal into a reliable write primitive.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `External_Control_of_System_or_Config_Setting` | Medium | `/src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:57` | `117621` |
| L2 Bridge | `Parameter_Tampering` | Medium | `/src/main/java/org/cysecurity/cspf/jvl/controller/EmailCheck.java:42` | `oLhf1Sa69rpDxNtxDtYOlWclNgs=` |
| L2 Bridge | `Stored_Relative_Path_Traversal` | Medium | `/src/main/webapp/vulnerability/sqli/download_id_union.jsp:24` | `pCeSA+Se0EWYdLfztdcz5VMoa4s=` |
| L3 Amplifier | `Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions` | Low | `/src/main/java/org/cysecurity/cspf/jvl/controller/AddPage.java:45` | `ppKpfm8TZs9xeAZbkQZ8YK2YDt4=` |
| L3 Amplifier | `Race_Condition` | Low | `/src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:59` | `MLft8mwUe92v5D6e6BOWNT+gC90=` |

*Nexa Commerce reproduction:* `catalog-service/src/main/java/com/nexa/catalog/` — 1 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-104 — Redirect to Token Theft (JavaScript / Node)

**Chain CPS 9.14 (High).** Source: `OWASP/NodeGoat Demo` scan `b0fa38ca-d352-483a-9197-41f5e1dc0dec`.

Third-party capture of a session or access token. An unvalidated redirect hands control to an attacker-chosen destination (F1), no HSTS means a downgrade to plaintext is not refused (F2), no CSP means no policy blocks the outbound request (F3), reverse tabnabbing gives the opened page a handle back to the opener (F4), and log forging lets the attacker pollute the audit trail that would otherwise reconstruct the sequence (F5).

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Open_Redirect` | Medium | `/NodeGoat-master/app/routes/index.js:72` | `/dnIdCbf68zHdxSQp2JaS1OJKzc=` |
| L3 Amplifier | `Missing_HSTS_Header` | Medium | `/NodeGoat-master/app/routes/allocations.js:25` | `hm7Z3uvUdX4eYqPsqP0g1+nBdAg=` |
| L3 Amplifier | `Missing_CSP_Header` | Low | `/NodeGoat-master/app/routes/allocations.js:25` | `/aEsdK5ud63aXPZ7wiuUUMjW3z0=` |
| L2 Bridge | `Unsafe_Use_Of_Target_blank` | Low | `/NodeGoat-master/app/views/tutorial/a7.html:31` | `8606084` |
| L1 Signal | `Log_Forging` | Low | `/NodeGoat-master/app/routes/session.js:57` | `jV5Jfp7QHotJ/S1rIqQstuRJCZ8=` |

*Nexa Commerce reproduction:* `web-gateway/src/` — 2 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-105 — Container Escape Surface (cross-engine: SAST + IaC)

**Chain CPS 9.25 (High).** Source: `OWASP/NodeGoat Demo` scan `b0fa38ca-d352-483a-9197-41f5e1dc0dec`.

Escape from the container to the host, then lateral movement. A hardcoded credential in the image (F1) gives an authenticated foothold; unrestricted capabilities (F2) and no seccomp or AppArmor profile (F3) remove the kernel-level barriers to escape; unbound host interface binding (F4) exposes the escape path across the node; and no healthcheck (F5) means the orchestrator never notices the workload misbehaving. The SAST finding and the IaC findings are triaged by different teams, which is precisely why the chain survives.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Use_Of_Hardcoded_Password` | Medium | `/NodeGoat-master/artifacts/db-reset.js:27` | `6cZYX5Wlml3T9zR0xiuyTLYhFBI=` |
| L3 Amplifier | `Container Capabilities Unrestricted` | Medium | `*` | `6KfFKsfD633WAC53IIyANWDnYhg=` |
| L3 Amplifier | `Security Opt Not Set` | Medium | `*` | `15674550` |
| L3 Amplifier | `Container Traffic Not Bound To Host Interface` | Medium | `*` | `15674535` |
| L1 Signal | `Healthcheck Instruction Missing` | Low | `*` | `15674561` |

*Nexa Commerce reproduction:* `docker-compose.yml + ops/seed/` — 1 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-106 — Informational-Only Chain to Silent Data Exfiltration

**Chain CPS 9.15 (High).** Source: `cx-carolyn-yates/JavaVulnerableLab` scan `382c4fa6-5687-4b5a-8205-6ca91269c0fa`.

Undetected data exfiltration. Queries are assembled dynamically (F1) so the injection surface exists; database actions are not logged (F2) so exploitation leaves no trail; there is no global error handler (F3) so failures surface raw to the caller; error conditions are returned but never acted on (F4) so the application continues in a bad state; and internal detail is written to the system output stream (F5) where it lands in aggregated logs. THIS CHAIN'S CONSTITUENTS ARE ALL RATED INFORMATIONAL - the tier below Low, which most programs never even render in the backlog. It still reaches the High band.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Dynamic_SQL_Queries` | Information | `/src/main/java/org/cysecurity/cspf/jvl/controller/LoginValidator.java:52` | `0XBp02QSHGEql4giNp73keCA3Es=` |
| L3 Amplifier | `Insufficient_Logging_of_Database_Actions` | Information | `/src/main/webapp/vulnerability/idor/change-email.jsp:32` | `12jj98OpDWTFsrU0lpG1XUagp/Y=` |
| L2 Bridge | `Pages_Without_Global_Error_Handler` | Information | `/src/main/webapp/admin/admin.jsp:1` | `0tZuTNbFjEN8ykwCCIAbRU3KNJA=` |
| L1 Signal | `Unchecked_Error_Condition` | Information | `/src/main/java/org/cysecurity/cspf/jvl/controller/Logout.java:42` | `3iWHH6gMkWJLKli9QiunyCCQIG0=` |
| L1 Signal | `Use_of_System_Output_Stream` | Information | `/src/main/webapp/vulnerability/DisplayMessage.jsp:35` | `0APbv9DRr/LUAZserU2/2fSPWus=` |

*Nexa Commerce reproduction:* `catalog-service/` — 0 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-107 — Agent Tool-Path Error Disclosure (AI framework)

**Chain CPS 9.78 (High).** Source: `AISC_openai_agents_python` scan `5797794c-4ea0-4553-a883-c908a6fec287`.

Full reconnaissance of an agent's tool and MCP surface, enabling targeted tool-poisoning and session replay. An object access violation in the tool definition layer (F1) exposes internal object state; error messages then disclose internals of the MCP transport (F2), the tool execution path (F3), the session persistence layer (F4) and the tracing provider (F5). Each disclosure is Low. Together they hand an attacker the agent's tool schema, its MCP wiring, its session storage semantics and its trace identifiers - everything needed to craft a tool-poisoning payload that the model itself will faithfully execute. Note the codebase is a widely used agent framework, not a deliberately vulnerable lab.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Object_Access_Violation` | Medium | `/src/agents/tool.py:1284` | `p9H+6K7MHD/gKWBQ699t5SEO4Pw=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/mcp/util.py:296` | `gPZSEBzeEMW5I9wlkSoHqZvh4eQ=` |
| L2 Bridge | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/run_internal/tool_actions.py:130` | `FRtCxgpOBDPuQtV+qNVxGbJ97BQ=` |
| L2 Bridge | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/run_internal/session_persistence.py:479` | `NwUJPu9T7HKfoPXIvLPqn011OpM=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `/src/agents/tracing/provider.py:95` | `32+Yo0mzZGU30FIJH3+Qi0oLngA=` |

*Nexa Commerce reproduction:* `assistant-service/src/agents/` — 0 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-108 — Defence-in-Depth Erosion to Credentialed Session Ride

**Chain CPS 9.24 (High).** Source: `cx-andy-schmit/dvwa` scan `c389b5e7-34fc-4be6-821b-59cd647c7f0b`.

An attacker rides an authenticated administrator session and reads back database internals. CSRF protection is absent on state-changing endpoints (F1), sensitive database information is reachable by an unauthorised actor (F2), HSTS is never set so the session can be observed after a downgrade (F3), exceptions are handled improperly on the login path (F4), and error messages return query-level detail (F5).

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `CSRF` | Medium | `/vulnerabilities/captcha/source/low.php:50` | `4BCo3G3gAni7aAzcVLnCbb++xpg=` |
| L2 Bridge | `Exposure of Sensitive Information to an Unauthorized Actor` | Medium | `/dvwa/includes/DBMS/MySQL.php:88` | `3/YbcHdUmUIGhxgUr09l+gcwZ+Q=` |
| L3 Amplifier | `Missing_HSTS_Header` | Medium | `/dvwa/includes/dvwaPage.inc.php:305` | `2W4LMHcT/vSld6tCtqrQExOCVcU=` |
| L1 Signal | `Improper_Exception_Handling` | Low | `/login.php:40` | `d77SUqnw0wzXqYjeIVARjEytQPI=` |
| L1 Signal | `Information_Exposure_Through_an_Error_Message` | Low | `/vulnerabilities/sqli/source/low.php:35` | `EdyXCoeD22Z/MViCkGTdzWwMps8=` |

*Nexa Commerce reproduction:* `storefront/public/` — 0 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-109 — Cloud Exfiltration Blindness (Terraform / AWS)

**Chain CPS 8.32 (High).** Source: `owasp-juice-lab` scan `b0b1dcd6-4cdc-4a3e-bb66-f689ec8e4999`.

Data exfiltration from managed data stores with no forensic trail and no clean recovery point. An IAM policy permits the exfiltration operations outright (F1); S3 access logging is disabled (F2) and RDS logging is disabled (F3), so neither the staging nor the extraction is recorded; RDS backups are disabled (F4), removing the recovery point that would bound the damage; and workloads run in an unrecommended namespace (F5), widening the blast radius of any compromised pod. Every finding is Medium. The composite is a breach that cannot be detected, reconstructed, or cleanly recovered from.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `IAM policy allows for data exfiltration` | Medium | `terraform` | `+cWUkE7MhVo3DkGLtob6BXUj170=` |
| L3 Amplifier | `S3 Bucket Logging Disabled` | Medium | `terraform` | `WJLKWg3/3bbFGgwtObNBALFUr80=` |
| L3 Amplifier | `RDS Without Logging` | Medium | `terraform` | `4ExYdis3eWtB5PiJRYcz0Tdyk84=` |
| L3 Amplifier | `RDS With Backup Disabled` | Medium | `terraform` | `h/70jVGCxBzxMlBzM360MISgzp4=` |
| L1 Signal | `Using Unrecommended Namespace` | Medium | `kubernetes` | `Ojwf0eSDnF/hKou1A1UO7S4L3/c=` |

*Nexa Commerce reproduction:* `deploy/terraform/ + deploy/k8s/` — 0 of 5 reproduced in scan `cc434dd7` (v1).

---

## CH-110 — API Auth Weakening to Token Forgery

**Chain CPS 8.01 (High).** Source: `cx-jeremy-polansky/authlab-canary` scan `2e83d245-5417-4076-a24e-34622e6fd073`.

Forgery of an authentication token accepted by the API. A hardcoded credential in the controller (F1) supplies key material, a weak client-side hash (F2) means the derived value is reproducible, and the JWT is accepted without validating its claims directives (F3) so a forged token with attacker-chosen claims passes verification. Two Mediums and a Low compose into authentication bypass.

| Role | Query | Severity | Location | Finding ID |
|---|---|---|---|---|
| L2 Bridge | `Use_of_Hardcoded_Password` | Medium | `/app/controllers/app.go:213` | `0Bq5qFb+uLA1haKPGSpCur2jTAM=` |
| L2 Bridge | `Client_Weak_Cryptographic_Hash` | Medium | `/public/js/clientside.js:113` | `dDFtmyvQUkjW8MvNhYJFe1jcEMI=` |
| L3 Amplifier | `JWT_No_Claims_Directives_Validation` | Low | `/app/controllers/app.go:396` | `d8VLX0/ssa9zVdKaddCJrd6Lklo=` |

*Nexa Commerce reproduction:* `auth-service/` — 1 of 3 reproduced in scan `cc434dd7` (v1).

---
## Method

1. **Survey.** Query inventory read live from the tenant across five language
   presets — PHP, Java, JavaScript, Go, Python — plus KICS and SCA, using the
   Checkmarx MCP against completed scans.
2. **Select.** Chains assembled only from findings that already existed, with
   the severity Checkmarx had already assigned. No prediction step, so no
   prediction to be wrong about.
3. **Score.** Each finding scored on the five CPS dimensions (Prevalence 0.15,
   Chain Utility 0.30, AI Leverage 0.25, Blast Radius 0.15, Impact Proximity
   0.15), then aggregated as `max(scores) + 0.1 × sum(remainder)`, capped at 10.
4. **Verify.** Each chain re-matched against its own scan's findings. A guard
   test fails the build if any High or Critical enters a chain. A negative
   control confirms each fixture assembles only its own chains and reports the
   other nine as NOT_ASSEMBLED — the matcher requires the declared composition,
   not mere co-occurrence.

36 automated tests cover parser shapes, scorer dispatch, chain assembly, path
scoping and the no-High guard.

---

## Reproduction in a single codebase

The ten chains were observed across five separate applications. **Nexa
Commerce** is a purpose-built polyglot e-commerce specimen that reproduces all
ten in one repository — five runnable services plus Terraform, Kubernetes and
Docker.

First scan (`cc434dd7`, 175 files, 4 engines, 3m17s) reproduced **9 of 48**
constituent findings, each at the predicted severity in the predicted file. It
also surfaced two genuine defects in the specimen — a Critical `Stored_XSS`
from streaming a template file to the response, and a High
`Plain_Text_Transport_Layer_in_Server` from a non-TLS Go listener. Both are
fixed in v2.

Three systematic causes explain the misses, all corrected in v2:

| Cause | Evidence | Correction |
|---|---|---|
| Python used `.format()` instead of f-strings | The real OpenAI Agents SDK interpolates the exception with f-strings; taint tracking follows those | All four CH-107 error paths rewritten to the SDK idiom |
| Java read input via `request.getAttribute()` | Not a taint source, so three servlets produced nothing | Switched to `request.getParameter()` |
| PHP patterns lived in `lib/` includes | The cookie findings fired at `cart.php`, never in `session.php` where the same code sits | CH-101 and CH-108 moved into entry-point pages |

That loop — lock the expectation, scan, diagnose the gap precisely — is the
method working, not failing.

---

## Observations for Checkmarx

Five findings from building this, offered as product feedback.

**1. Query severity is language-preset dependent.** `Use of Insufficiently
Random Values` is Medium in the PHP preset and Low in JavaScript. Both are
defensible, but any cross-language risk model must key severity on the pair
*(query, language)* rather than on the query alone.

**2. Query-name casing is not stable, even within one scan.** DVWA scan
`c389b5e7` emits both `Unsafe_Use_Of_Target_blank` and
`Unsafe_Use_Of_Target_Blank`. Go emits `Use_of_Hardcoded_Password` where
JavaScript emits `Use_Of_Hardcoded_Password`. Anything joining on query name
silently splits one rule into several without case-insensitive normalisation.

**3. Query names vary across presets for the same rule.**
`Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions` in one Java codebase,
`Creation_of_Temp_File_With_Insecure_Permissions` in another — same tenant.

**4. `listFindings` server-side filters are partly inert.** `engine_type`,
`query_name` and `language_name` are accepted but ignored server-side. Only
severity, state and status narrow results, so locating SAST findings inside a
large mixed scan is a paging exercise — in the NodeGoat scan the SAST Medium
block began at offset 4 of 13 pages, behind ~80 SCA rows. A working
`engine_type` filter would materially reduce agent round-trips.

**5. AISC results are not exposed through `listFindings`.** No `aisc`-typed
result appears at any severity tier, on any scan queried, including scans whose
engine list contains `aisc`. AI-BOM component detection appears reachable only
through the CycloneDX export path, so AI inventory cannot be correlated with
SAST/SCA/IaC findings in one API surface — which is exactly what chain-aware
analysis of AI systems needs.

---

## Reproducing

```bash
python -m cps_engine.cli sample_data/observed_dvwa_ch101.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_javavulnlab_ch102_ch103.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_nodegoat_ch104_ch105.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_javavulnlab_ch106.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_openai_agents_ch107.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_dvwa_ch108.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_juicelab_ch109.json \
    --catalog lab_app/chains_index.json --all
python -m cps_engine.cli sample_data/observed_authlab_ch110.json \
    --catalog lab_app/chains_index.json --all

python run_smoke_tests.py     # 36/36
```
