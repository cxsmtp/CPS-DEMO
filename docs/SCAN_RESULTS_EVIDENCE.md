# Scan Results — Evidence Pack for CH-101 to CH-110

Tenant `checkmarx-global-services-internal`. Every finding below was read out of a
completed Checkmarx One scan on 2026-08-01 via the Checkmarx MCP. Finding IDs are
re-checkable with `getFindingDetails(scan_id, finding_id)`.

Two things to read in each section:

1. **Triage context** — where the chain's findings sat in the real queue. This is the
   argument: a severity-ordered backlog reaches these findings only after everything
   above them is closed, which in practice is never.
2. **Engine output** — the per-finding CPS scores and the chain assembly verdict,
   reproduced verbatim from the CLI.

---

## Summary

| Chain | Stack | Composition | Top severity | Ranked ahead in queue | Chain CPS |
|---|---|---|---|---|---|
| CH-101 | PHP | 3 Med + 2 Low | Medium | 163 (59 C + 104 H) | **10.00** |
| CH-102 | Java | 3 Med + 2 Low | Medium | 243 (124 C + 119 H) | **9.49** |
| CH-103 | Java | 3 Med + 2 Low | Medium | 243 (124 C + 119 H) | **9.96** |
| CH-104 | JavaScript | 2 Med + 3 Low | Medium | 384 (84 C + 300 H) | **9.14** |
| CH-105 | Docker / K8s | 4 Med + 1 Low | Medium | 384 (84 C + 300 H) | **9.25** |
| CH-106 | Java | **5 Informational** | **Information** | **554 (all C/H/M/L)** | **9.15** |
| CH-107 | Python / OpenAI Agents SDK | 1 Med + 4 Low | Medium | 23 (16 C + 7 H) | **9.78** |
| CH-108 | PHP | 3 Med + 2 Low | Medium | 163 (59 C + 104 H) | **9.24** |
| CH-109 | Terraform / AWS | 5 Med | Medium | 15 (3 C + 12 H) | **8.32** |
| CH-110 | Go | 2 Med + 1 Low | Medium | 36 (12 C + 24 H) | **8.01** |

**48 findings across 10 chains. Zero High. Zero Critical. Every chain in the High band.**

The fifth column is the argument. In every case a severity-ordered backlog reaches the
chain only after clearing everything above it. For CH-106 that means clearing 554
findings — every Critical, High, Medium and Low in the scan — before the first
constituent is even displayed. The chain scores 9.15.

---
## CH-101

| | |
|---|---|
| Project | `cx-andy-schmit/dvwa` |
| Scan ID | `c389b5e7-34fc-4be6-821b-59cd647c7f0b` |
| Stack | PHP |
| Scan totals | 410 findings — 59 Critical, 104 High, 86 Medium, 45 Low, 116 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **163 findings (59 Critical + 104 High)** |

```
Top 5 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.75  High        Medium         Use of Insufficiently Random Values  ::  /vulnerabilities/weak_id/index.php:17
  7.75  High        Low            Use_of_Non_Cryptographic_Random  ::  /vulnerabilities/weak_id/source/impossible.php:6
  7.12  Moderate    Medium         Broken_or_Risky_Hashing_Function  ::  /vulnerabilities/brute/source/impossible.php:16
  6.12  Moderate    Medium         Insecure_Value_of_the_SameSite_Cookie_Attribute  ::  /vulnerabilities/weak_id/source/low.php:11
  4.75  Low         Low            Cookie_Overly_Broad_Path  ::  /vulnerabilities/weak_id/source/low.php:11


================================================================================
CH-101 — Predictable Session to Account Takeover (PHP)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        5 of 5 present (100%)
Chain CPS:       10.00  (High)
Real-world anchor: Session-prediction chains of the class seen repeatedly in PHP applications that roll their own session identifiers rather than using the platform session handler.
Terminal outcome:  Full account takeover with no credential theft. A non-cryptographic PRNG generates the session identifier (F1, F5), the verifier over it uses a broken hash (F2), the cookie is delivered without SameSite protection (F3), and its path scope is broader than the issuing endpoint (F4). Enumerate the PRNG, forge the verifier, deliver the cookie cross-site, and the session is valid site-wide. Highest-severity constituent is Medium.

Required findings:
  [ok]  Use of Insufficiently Random Values (L2_Bridge)  matched: 1
  [ok]  Broken_or_Risky_Hashing_Function (L2_Bridge)  matched: 1
  [ok]  Insecure_Value_of_the_SameSite_Cookie_Attribute (L3_Amplifier)  matched: 1
  [ok]  Cookie_Overly_Broad_Path (L3_Amplifier)  matched: 1
  [ok]  Use_of_Non_Cryptographic_Random (L1_Signal)  matched: 1
```

---

## CH-102

| | |
|---|---|
| Project | `cx-carolyn-yates/JavaVulnerableLab` |
| Scan ID | `382c4fa6-5687-4b5a-8205-6ca91269c0fa` |
| Stack | Java |
| Scan totals | 860 findings — 124 Critical, 119 High, 178 Medium, 133 Low, 306 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **243 findings (124 Critical + 119 High)** |

```
Top 10 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.50  Moderate    Medium         External_Control_of_System_or_Config_Setting  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:57
  7.12  Moderate    Medium         Information_Exposure_Through_Query_String  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:57
  7.12  Moderate    Medium         Exposure of Sensitive Information to an Unauthorized Actor  ::  /src/main/webapp/ForgotPassword.jsp:10
  7.12  Moderate    Medium         Stored_Relative_Path_Traversal  ::  /src/main/webapp/vulnerability/sqli/download_id_union.jsp:24
  6.75  Moderate    Medium         Parameter_Tampering  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/EmailCheck.java:42
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/EmailCheck.java:60
  5.75  Moderate    Medium         Privacy_Violation  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/XPathQuery.java:50
  5.75  Moderate    Low            Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/AddPage.java:45
  5.00  Low         Low            Race_Condition  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:59
  4.75  Low         Low            Heap_Inspection  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/LoginValidator.java:44


================================================================================
CH-102 — Error-Leak to Credential Disclosure (Java)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        5 of 5 present (100%)
Chain CPS:       9.49  (High)
Real-world anchor: Incremental-disclosure chains, where several individually minor leaks are combined to reconstruct credentials or PII without ever exploiting a memory-safety or injection flaw.
Terminal outcome:  Reconstruction of user credentials and PII from disclosure alone. Query strings carry sensitive values into logs and referers (F1), an unauthorised actor can reach sensitive responses (F2), PII flows into sinks that were never meant to hold it (F3), error messages return internal state (F4), and credentials sit unscrubbed in heap-resident objects (F5). No injection, no traversal, no High-rated finding.

Required findings:
  [ok]  Information_Exposure_Through_Query_String (L2_Bridge)  matched: 1
  [ok]  Exposure of Sensitive Information to an Unauthorized Actor (L2_Bridge)  matched: 1
  [ok]  Privacy_Violation (L3_Amplifier)  matched: 1
  [ok]  Information_Exposure_Through_an_Error_Message (L1_Signal)  matched: 1
  [ok]  Heap_Inspection (L1_Signal)  matched: 1
```

---

## CH-103

| | |
|---|---|
| Project | `cx-carolyn-yates/JavaVulnerableLab` |
| Scan ID | `382c4fa6-5687-4b5a-8205-6ca91269c0fa` |
| Stack | Java |
| Scan totals | 860 findings — 124 Critical, 119 High, 178 Medium, 133 Low, 306 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **243 findings (124 Critical + 119 High)** |

```
Top 10 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.50  Moderate    Medium         External_Control_of_System_or_Config_Setting  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:57
  7.12  Moderate    Medium         Information_Exposure_Through_Query_String  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:57
  7.12  Moderate    Medium         Exposure of Sensitive Information to an Unauthorized Actor  ::  /src/main/webapp/ForgotPassword.jsp:10
  7.12  Moderate    Medium         Stored_Relative_Path_Traversal  ::  /src/main/webapp/vulnerability/sqli/download_id_union.jsp:24
  6.75  Moderate    Medium         Parameter_Tampering  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/EmailCheck.java:42
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/EmailCheck.java:60
  5.75  Moderate    Medium         Privacy_Violation  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/XPathQuery.java:50
  5.75  Moderate    Low            Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/AddPage.java:45
  5.00  Low         Low            Race_Condition  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Install.java:59
  4.75  Low         Low            Heap_Inspection  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/LoginValidator.java:44


================================================================================
CH-103 — Config Tamper to Arbitrary File Write (Java)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        5 of 5 present (100%)
Chain CPS:       9.96  (High)
Real-world anchor: Configuration-tampering chains where an attacker steers application behaviour through settings rather than through a direct injection sink.
Terminal outcome:  Arbitrary file write leading to code execution. Attacker-controlled input reaches a system or config setting (F1), request parameters are trusted for authorisation-relevant decisions (F2), and a stored relative path is resolved without canonicalisation (F3). A temp file created with permissive permissions (F4) plus a race window on the write (F5) turn the traversal into a reliable write primitive.

Required findings:
  [ok]  External_Control_of_System_or_Config_Setting (L2_Bridge)  matched: 1
  [ok]  Parameter_Tampering (L2_Bridge)  matched: 1
  [ok]  Stored_Relative_Path_Traversal (L2_Bridge)  matched: 1
  [ok]  Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions (L3_Amplifier)  matched: 1
  [ok]  Race_Condition (L3_Amplifier)  matched: 1
```

---

## CH-104

| | |
|---|---|
| Project | `OWASP/NodeGoat Demo` |
| Scan ID | `b0fa38ca-d352-483a-9197-41f5e1dc0dec` |
| Stack | JavaScript / Node + Docker |
| Scan totals | 687 findings — 84 Critical, 300 High, 246 Medium, 55 Low, 2 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **384 findings (84 Critical + 300 High)** |

```
Top 10 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.25  Moderate    Medium         Container Capabilities Unrestricted  ::  /NodeGoat-master/Dockerfile:0
  7.12  Moderate    Medium         Open_Redirect  ::  /NodeGoat-master/app/routes/index.js:72
  6.50  Moderate    Medium         Use_Of_Hardcoded_Password  ::  /NodeGoat-master/artifacts/db-reset.js:27
  6.50  Moderate    Medium         Container Traffic Not Bound To Host Interface  ::  /NodeGoat-master/Dockerfile:0
  5.87  Moderate    Medium         Security Opt Not Set  ::  /NodeGoat-master/Dockerfile:0
  5.75  Moderate    Low            Missing_CSP_Header  ::  /NodeGoat-master/app/routes/allocations.js:25
  5.25  Moderate    Low            Log_Forging  ::  /NodeGoat-master/app/routes/session.js:57
  4.75  Low         Low            Unsafe_Use_Of_Target_blank  ::  /NodeGoat-master/app/views/tutorial/a7.html:31
  4.37  Low         Medium         Missing_HSTS_Header  ::  /NodeGoat-master/app/routes/allocations.js:25
  1.12  Negligible  Low            Healthcheck Instruction Missing  ::  /NodeGoat-master/Dockerfile:0


================================================================================
CH-104 — Redirect to Token Theft (JavaScript / Node)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        5 of 5 present (100%)
Chain CPS:       9.14  (High)
Real-world anchor: OAuth and session-token theft via redirect abuse, the pattern behind multiple identity-integration incidents where the redirect finding alone was triaged as low priority.
Terminal outcome:  Third-party capture of a session or access token. An unvalidated redirect hands control to an attacker-chosen destination (F1), no HSTS means a downgrade to plaintext is not refused (F2), no CSP means no policy blocks the outbound request (F3), reverse tabnabbing gives the opened page a handle back to the opener (F4), and log forging lets the attacker pollute the audit trail that would otherwise reconstruct the sequence (F5).

Required findings:
  [ok]  Open_Redirect (L2_Bridge)  matched: 1
  [ok]  Missing_HSTS_Header (L3_Amplifier)  matched: 1
  [ok]  Missing_CSP_Header (L3_Amplifier)  matched: 1
  [ok]  Unsafe_Use_Of_Target_blank (L2_Bridge)  matched: 1
  [ok]  Log_Forging (L1_Signal)  matched: 1
```

---

## CH-105

| | |
|---|---|
| Project | `OWASP/NodeGoat Demo` |
| Scan ID | `b0fa38ca-d352-483a-9197-41f5e1dc0dec` |
| Stack | JavaScript / Node + Docker |
| Scan totals | 687 findings — 84 Critical, 300 High, 246 Medium, 55 Low, 2 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **384 findings (84 Critical + 300 High)** |

```
Top 10 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.25  Moderate    Medium         Container Capabilities Unrestricted  ::  /NodeGoat-master/Dockerfile:0
  7.12  Moderate    Medium         Open_Redirect  ::  /NodeGoat-master/app/routes/index.js:72
  6.50  Moderate    Medium         Use_Of_Hardcoded_Password  ::  /NodeGoat-master/artifacts/db-reset.js:27
  6.50  Moderate    Medium         Container Traffic Not Bound To Host Interface  ::  /NodeGoat-master/Dockerfile:0
  5.87  Moderate    Medium         Security Opt Not Set  ::  /NodeGoat-master/Dockerfile:0
  5.75  Moderate    Low            Missing_CSP_Header  ::  /NodeGoat-master/app/routes/allocations.js:25
  5.25  Moderate    Low            Log_Forging  ::  /NodeGoat-master/app/routes/session.js:57
  4.75  Low         Low            Unsafe_Use_Of_Target_blank  ::  /NodeGoat-master/app/views/tutorial/a7.html:31
  4.37  Low         Medium         Missing_HSTS_Header  ::  /NodeGoat-master/app/routes/allocations.js:25
  1.12  Negligible  Low            Healthcheck Instruction Missing  ::  /NodeGoat-master/Dockerfile:0


================================================================================
CH-105 — Container Escape Surface (cross-engine: SAST + IaC)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST, IaC
Required:        5 of 5 present (100%)
Chain CPS:       9.25  (High)
Real-world anchor: Credential-plus-runtime chains of the class documented in container-escape research, where the application finding and the orchestration finding are owned by different teams and neither is escalated alone.
Terminal outcome:  Escape from the container to the host, then lateral movement. A hardcoded credential in the image (F1) gives an authenticated foothold; unrestricted capabilities (F2) and no seccomp or AppArmor profile (F3) remove the kernel-level barriers to escape; unbound host interface binding (F4) exposes the escape path across the node; and no healthcheck (F5) means the orchestrator never notices the workload misbehaving. The SAST finding and the IaC findings are triaged by different teams, which is precisely why the chain survives.

Required findings:
  [ok]  Use_Of_Hardcoded_Password (L2_Bridge)  matched: 1
  [ok]  Container Capabilities Unrestricted (L3_Amplifier)  matched: 1
  [ok]  Security Opt Not Set (L3_Amplifier)  matched: 1
  [ok]  Container Traffic Not Bound To Host Interface (L3_Amplifier)  matched: 1
  [ok]  Healthcheck Instruction Missing (L1_Signal)  matched: 1
```

---

## CH-106

| | |
|---|---|
| Project | `cx-carolyn-yates/JavaVulnerableLab` |
| Scan ID | `382c4fa6-5687-4b5a-8205-6ca91269c0fa` |
| Stack | Java |
| Scan totals | 860 findings — 124 Critical, 119 High, 178 Medium, 133 Low, 306 Informational |
| Highest severity in this chain | **Information** |
| Ranked ahead of this chain in a severity-ordered queue | **554 findings (everything Critical through Low)** |

```
Top 5 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.12  Moderate    Information    Dynamic_SQL_Queries  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/LoginValidator.java:52
  5.75  Moderate    Information    Pages_Without_Global_Error_Handler  ::  /src/main/webapp/admin/admin.jsp:1
  5.12  Moderate    Information    Insufficient_Logging_of_Database_Actions  ::  /src/main/webapp/vulnerability/idor/change-email.jsp:32
  4.75  Low         Information    Unchecked_Error_Condition  ::  /src/main/java/org/cysecurity/cspf/jvl/controller/Logout.java:42
  4.62  Low         Information    Use_of_System_Output_Stream  ::  /src/main/webapp/vulnerability/DisplayMessage.jsp:35


================================================================================
CH-106 — Informational-Only Chain to Silent Data Exfiltration
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        5 of 5 present (100%)
Chain CPS:       9.15  (High)
Real-world anchor: The class of breach that is discovered months later by a third party rather than by the victim, because every control that would have caught it was rated as a code-quality nit.
Terminal outcome:  Undetected data exfiltration. Queries are assembled dynamically (F1) so the injection surface exists; database actions are not logged (F2) so exploitation leaves no trail; there is no global error handler (F3) so failures surface raw to the caller; error conditions are returned but never acted on (F4) so the application continues in a bad state; and internal detail is written to the system output stream (F5) where it lands in aggregated logs. THIS CHAIN'S CONSTITUENTS ARE ALL RATED INFORMATIONAL - the tier below Low, which most programs never even render in the backlog. It still reaches the High band.

Required findings:
  [ok]  Dynamic_SQL_Queries (L2_Bridge)  matched: 1
  [ok]  Insufficient_Logging_of_Database_Actions (L3_Amplifier)  matched: 1
  [ok]  Pages_Without_Global_Error_Handler (L2_Bridge)  matched: 1
  [ok]  Unchecked_Error_Condition (L1_Signal)  matched: 1
  [ok]  Use_of_System_Output_Stream (L1_Signal)  matched: 1
```

---

## CH-107

| | |
|---|---|
| Project | `AISC_openai_agents_python` |
| Scan ID | `5797794c-4ea0-4553-a883-c908a6fec287` |
| Stack | Python / OpenAI Agents SDK |
| Scan totals | 48 findings — 16 Critical, 7 High, 1 Medium, 23 Low, 1 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **23 findings (16 Critical + 7 High)** |

```
Top 5 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.38  Moderate    Medium         Object_Access_Violation  ::  /src/agents/tool.py:1284
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /src/agents/mcp/util.py:296
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /src/agents/run_internal/tool_actions.py:130
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /src/agents/run_internal/session_persistence.py:479
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /src/agents/tracing/provider.py:95


================================================================================
CH-107 — Agent Tool-Path Error Disclosure (AI framework)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST, AI-BOM
Required:        5 of 5 present (100%)
Chain CPS:       9.78  (High)
Real-world anchor: Reconnaissance against an autonomous agent's own runtime. Documented in 2025-2026 agent red-team work: the attacker does not need to jailbreak the model if the framework tells them how its tool layer, MCP transport and session store behave.
Terminal outcome:  Full reconnaissance of an agent's tool and MCP surface, enabling targeted tool-poisoning and session replay. An object access violation in the tool definition layer (F1) exposes internal object state; error messages then disclose internals of the MCP transport (F2), the tool execution path (F3), the session persistence layer (F4) and the tracing provider (F5). Each disclosure is Low. Together they hand an attacker the agent's tool schema, its MCP wiring, its session storage semantics and its trace identifiers - everything needed to craft a tool-poisoning payload that the model itself will faithfully execute. Note the codebase is a widely used agent framework, not a deliberately vulnerable lab.

Required findings:
  [ok]  Object_Access_Violation (L2_Bridge)  matched: 1
  [ok]  Information_Exposure_Through_an_Error_Message  [in /mcp/] (L1_Signal)  matched: 1
  [ok]  Information_Exposure_Through_an_Error_Message  [in tool_actions] (L2_Bridge)  matched: 1
  [ok]  Information_Exposure_Through_an_Error_Message  [in session_persistence] (L2_Bridge)  matched: 1
  [ok]  Information_Exposure_Through_an_Error_Message  [in tracing] (L1_Signal)  matched: 1

AI Inventory Context (0 of 2 components detected in scan):
  [--]  OpenAI Agents SDK (Python) (OpenAI library) (CHAIN TARGET)
  [--]  Model Context Protocol client (Anthropic library)
```

---

## CH-108

| | |
|---|---|
| Project | `cx-andy-schmit/dvwa` |
| Scan ID | `c389b5e7-34fc-4be6-821b-59cd647c7f0b` |
| Stack | PHP |
| Scan totals | 410 findings — 59 Critical, 104 High, 86 Medium, 45 Low, 116 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **163 findings (59 Critical + 104 High)** |

```
Top 5 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  7.12  Moderate    Medium         Exposure of Sensitive Information to an Unauthorized Actor  ::  /dvwa/includes/DBMS/MySQL.php:88
  6.12  Moderate    Medium         CSRF  ::  /vulnerabilities/captcha/source/low.php:50
  6.00  Moderate    Low            Information_Exposure_Through_an_Error_Message  ::  /vulnerabilities/sqli/source/low.php:35
  4.62  Low         Low            Improper_Exception_Handling  ::  /login.php:40
  4.37  Low         Medium         Missing_HSTS_Header  ::  /dvwa/includes/dvwaPage.inc.php:305


================================================================================
CH-108 — Defence-in-Depth Erosion to Credentialed Session Ride
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        5 of 5 present (100%)
Chain CPS:       9.24  (High)
Real-world anchor: The pattern behind long-lived compromise of admin interfaces, where no single control failure is dramatic but the combination leaves no barrier standing.
Terminal outcome:  An attacker rides an authenticated administrator session and reads back database internals. CSRF protection is absent on state-changing endpoints (F1), sensitive database information is reachable by an unauthorised actor (F2), HSTS is never set so the session can be observed after a downgrade (F3), exceptions are handled improperly on the login path (F4), and error messages return query-level detail (F5).

Required findings:
  [ok]  CSRF (L2_Bridge)  matched: 1
  [ok]  Exposure of Sensitive Information to an Unauthorized Actor (L2_Bridge)  matched: 1
  [ok]  Missing_HSTS_Header (L3_Amplifier)  matched: 1
  [ok]  Improper_Exception_Handling (L1_Signal)  matched: 1
  [ok]  Information_Exposure_Through_an_Error_Message (L1_Signal)  matched: 1
```

---

## CH-109

| | |
|---|---|
| Project | `owasp-juice-lab` |
| Scan ID | `b0b1dcd6-4cdc-4a3e-bb66-f689ec8e4999` |
| Stack | Terraform / AWS / K8s |
| Scan totals | 55 findings — 3 Critical, 12 High, 16 Medium, 15 Low, 9 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **15 findings (3 Critical + 12 High)** |

```
Top 5 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  6.50  Moderate    Medium         IAM policy allows for data exfiltration  ::  /terraform/iam.tf:0
  5.12  Moderate    Medium         RDS With Backup Disabled  ::  /terraform/rds.tf:0
  4.37  Low         Medium         S3 Bucket Logging Disabled  ::  /terraform/s3.tf:0
  4.37  Low         Medium         RDS Without Logging  ::  /terraform/rds.tf:0
  4.37  Low         Medium         Using Unrecommended Namespace  ::  /kubernetes/deployment.yaml:0


================================================================================
CH-109 — Cloud Exfiltration Blindness (Terraform / AWS)
================================================================================
State:           FULLY_ASSEMBLED
Engines:         IaC
Required:        5 of 5 present (100%)
Chain CPS:       8.32  (High)
Real-world anchor: Cloud data-theft incidents where the exfiltration itself was permitted by policy and no telemetry existed to reconstruct it afterwards.
Terminal outcome:  Data exfiltration from managed data stores with no forensic trail and no clean recovery point. An IAM policy permits the exfiltration operations outright (F1); S3 access logging is disabled (F2) and RDS logging is disabled (F3), so neither the staging nor the extraction is recorded; RDS backups are disabled (F4), removing the recovery point that would bound the damage; and workloads run in an unrecommended namespace (F5), widening the blast radius of any compromised pod. Every finding is Medium. The composite is a breach that cannot be detected, reconstructed, or cleanly recovered from.

Required findings:
  [ok]  IAM policy allows for data exfiltration (L2_Bridge)  matched: 1
  [ok]  S3 Bucket Logging Disabled (L3_Amplifier)  matched: 1
  [ok]  RDS Without Logging (L3_Amplifier)  matched: 1
  [ok]  RDS With Backup Disabled (L3_Amplifier)  matched: 1
  [ok]  Using Unrecommended Namespace (L1_Signal)  matched: 1
```

---

## CH-110

| | |
|---|---|
| Project | `cx-jeremy-polansky/authlab-canary` |
| Scan ID | `2e83d245-5417-4076-a24e-34622e6fd073` |
| Stack | Go |
| Scan totals | 57 findings — 12 Critical, 24 High, 17 Medium, 4 Low, 0 Informational |
| Highest severity in this chain | **Medium** |
| Ranked ahead of this chain in a severity-ordered queue | **36 findings (12 Critical + 24 High)** |

```
Top 3 findings by individual CPS:
   CPS  Band        Severity       Query  ::  Source
------------------------------------------------------------------------------
  6.75  Moderate    Medium         Client_Weak_Cryptographic_Hash  ::  /public/js/clientside.js:113
  6.50  Moderate    Medium         Use_of_Hardcoded_Password  ::  /app/controllers/app.go:213
  6.12  Moderate    Low            JWT_No_Claims_Directives_Validation  ::  /app/controllers/app.go:396


================================================================================
CH-110 — API Auth Weakening to Token Forgery
================================================================================
State:           FULLY_ASSEMBLED
Engines:         SAST
Required:        3 of 3 present (100%)
Chain CPS:       8.01  (High)
Real-world anchor: Token-forgery chains against API gateways and auth services, where the signing weakness and the validation gap are separately triaged and separately deferred.
Terminal outcome:  Forgery of an authentication token accepted by the API. A hardcoded credential in the controller (F1) supplies key material, a weak client-side hash (F2) means the derived value is reproducible, and the JWT is accepted without validating its claims directives (F3) so a forged token with attacker-chosen claims passes verification. Two Mediums and a Low compose into authentication bypass.

Required findings:
  [ok]  Use_of_Hardcoded_Password (L2_Bridge)  matched: 1
  [ok]  Client_Weak_Cryptographic_Hash (L2_Bridge)  matched: 1
  [ok]  JWT_No_Claims_Directives_Validation (L3_Amplifier)  matched: 1
```

---

