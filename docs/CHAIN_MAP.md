# Nexa Commerce — chain map

Ten vulnerability chains, one codebase. Every constituent finding is expected
at **Medium, Low or Informational**. Nothing in application code or IaC is
intended to rate High or Critical.

Severities below are not guesses — each query was observed at that severity in
a completed Checkmarx One scan before this repository was written. Provenance
(project, scan ID, finding ID) is recorded in `chains_index.json` in the CPS
project.

| Chain | Service | Stack | Findings | Expected chain CPS |
|---|---|---|---|---|
| CH-101 Predictable Session → Account Takeover | `storefront/` | PHP | 3 Med + 2 Low | 10.00 |
| CH-102 Error-Leak → Credential Disclosure | `catalog-service/` | Java | 3 Med + 2 Low | 9.49 |
| CH-103 Config Tamper → Arbitrary File Write | `catalog-service/` | Java | 3 Med + 2 Low | 9.96 |
| CH-104 Redirect → Token Theft | `web-gateway/` | Node | 2 Med + 3 Low | 9.14 |
| CH-105 Container Escape Surface | `docker-compose.yml`, `ops/seed/` | Docker | 4 Med + 1 Low | 9.25 |
| CH-106 Informational-Only → Silent Exfiltration | `catalog-service/` | Java | **5 Informational** | 9.15 |
| CH-107 Agent Tool-Path Disclosure | `assistant-service/` | Python + AI-BOM | 1 Med + 4 Low | 9.78 |
| CH-108 Defence-in-Depth Erosion | `storefront/` | PHP | 3 Med + 2 Low | 9.24 |
| CH-109 Cloud Exfiltration Blindness | `deploy/terraform/`, `deploy/k8s/` | Terraform / K8s | 5 Med | 8.32 |
| CH-110 API Auth Weakening → Token Forgery | `auth-service/` | Go | 2 Med + 1 Low | 8.01 |

---

## CH-101 — Predictable Session to Account Takeover (PHP)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Use of Insufficiently Random Values` | Medium | `storefront/public/lib/session.php` → `nexa_new_session_id()` |
| F2 | `Broken_or_Risky_Hashing_Function` | Medium | `storefront/public/lib/session.php` → `nexa_sign_session()` |
| F3 | `Insecure_Value_of_the_SameSite_Cookie_Attribute` | Medium | `storefront/public/lib/session.php` → `nexa_issue_session()` |
| F4 | `Cookie_Overly_Broad_Path` | Low | `storefront/public/lib/session.php` → `nexa_issue_session()` |
| F5 | `Use_of_Non_Cryptographic_Random` | Low | `storefront/public/lib/session.php` → `nexa_new_session_id()` |

Mersenne Twister seeded from `time()` produces the session id; md5 signs it;
the cookie ships `SameSite=None` with `Path=/`. Enumerate, forge, deliver
cross-site, ride the session site-wide.

## CH-102 — Error-Leak to Credential Disclosure (Java)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Information_Exposure_Through_Query_String` | Medium | `CatalogServlet.java` → `buildContinueUrl()` |
| F2 | `Exposure of Sensitive Information to an Unauthorized Actor` | Medium | `AccountServlet.java` → `billingSummary()` |
| F3 | `Privacy_Violation` | Medium | `AccountServlet.java` → `doPost()` log line |
| F4 | `Information_Exposure_Through_an_Error_Message` | Low | `CatalogServlet.java` → `printStackTrace(out)` |
| F5 | `Heap_Inspection` | Low | `AccountServlet.java` → `lastPassphrase` field |

## CH-103 — Config Tamper to Arbitrary File Write (Java)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `External_Control_of_System_or_Config_Setting` | Medium | `ConfigServlet.java` → `System.setProperty()` |
| F2 | `Parameter_Tampering` | Medium | `ConfigServlet.java` → role from request |
| F3 | `Stored_Relative_Path_Traversal` | Medium | `ReportBuilder.java` → `reportTarget()` |
| F4 | `Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions` | Low | `ReportBuilder.java` → `createTempFile()` |
| F5 | `Race_Condition` | Low | `ReportBuilder.java` → exists/delete/write |

The traversal source is `catalog-settings.properties`, not the request. That
is deliberate: the stored variant is Medium, direct request traversal is High.

## CH-104 — Redirect to Token Theft (Node)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Open_Redirect` | Medium | `web-gateway/src/server.js` → `completeSignIn()` |
| F2 | `Missing_HSTS_Header` | Medium | `web-gateway/src/server.js` → `applySecurityHeaders()` |
| F3 | `Missing_CSP_Header` | Low | `web-gateway/src/server.js` → `applySecurityHeaders()` |
| F4 | `Unsafe_Use_Of_Target_blank` | Low | `web-gateway/src/views/product.html` |
| F5 | `Log_Forging` | Low | `web-gateway/src/server.js` → `auditRequest()` |

## CH-105 — Container Escape Surface (Docker)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Use_Of_Hardcoded_Password` | Medium | `ops/seed/seed.js` → `DB_PASSWORD` |
| F2 | `Container Capabilities Unrestricted` | Medium | `docker-compose.yml` → `cap_add` |
| F3 | `Security Opt Not Set` | Medium | `docker-compose.yml` → no `security_opt` |
| F4 | `Container Traffic Not Bound To Host Interface` | Medium | `docker-compose.yml` → `ports` |
| F5 | `Healthcheck Instruction Missing` | Low | `ops/seed/Dockerfile` |

Every other Dockerfile in the repo sets `USER` and `HEALTHCHECK` on purpose —
a missing `USER` rates **High** and would break the constraint.

## CH-106 — Informational-Only Chain (Java)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Dynamic_SQL_Queries` | Informational | `InventoryDao.java` → `lowStock()` |
| F2 | `Insufficient_Logging_of_Database_Actions` | Informational | `InventoryDao.java` |
| F3 | `Pages_Without_Global_Error_Handler` | Informational | `webapp/admin/dashboard.jsp` |
| F4 | `Unchecked_Error_Condition` | Informational | `InventoryDao.java` → `markCounted()` |
| F5 | `Use_of_System_Output_Stream` | Informational | `InventoryDao.java` |

The SQL is concatenated from compile-time constants, so it is Informational
"dynamic query" and never Injection. `web.xml` declares no `<error-page>` and
`dashboard.jsp` declares no `errorPage`.

## CH-107 — Agent Tool-Path Disclosure (Python + AI-BOM)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Object_Access_Violation` | Medium | `src/agents/tool.py` → `apply_overrides()` |
| F2 | `Information_Exposure_Through_an_Error_Message` | Low | `src/agents/mcp/util.py` |
| F3 | `Information_Exposure_Through_an_Error_Message` | Low | `src/agents/run_internal/tool_actions.py` |
| F4 | `Information_Exposure_Through_an_Error_Message` | Low | `src/agents/run_internal/session_persistence.py` |
| F5 | `Information_Exposure_Through_an_Error_Message` | Low | `src/agents/tracing/provider.py` |

F2–F5 are the same query in four different code paths, distinguished by
`match_file_contains`. AI-BOM surface is `src/agents/shop_assistant.py`:
GPT-4o, GPT-4o-mini, and the MCP transport.

## CH-108 — Defence-in-Depth Erosion (PHP)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `CSRF` | Medium | `storefront/public/checkout.php` |
| F2 | `Exposure of Sensitive Information to an Unauthorized Actor` | Medium | `storefront/public/lib/db.php` |
| F3 | `Missing_HSTS_Header` | Medium | `storefront/public/lib/page.php` |
| F4 | `Improper_Exception_Handling` | Low | `storefront/public/lib/db.php` |
| F5 | `Information_Exposure_Through_an_Error_Message` | Low | `storefront/public/lib/db.php` |

## CH-109 — Cloud Exfiltration Blindness (Terraform / K8s)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `IAM policy allows for data exfiltration` | Medium | `deploy/terraform/iam.tf` |
| F2 | `S3 Bucket Logging Disabled` | Medium | `deploy/terraform/s3.tf` |
| F3 | `RDS Without Logging` | Medium | `deploy/terraform/rds.tf` |
| F4 | `RDS With Backup Disabled` | Medium | `deploy/terraform/rds.tf` |
| F5 | `Using Unrecommended Namespace` | Medium | `deploy/k8s/deployment.yaml` |

Encryption, public-access blocking, versioning, `multi_az` and deletion
protection are all switched **on** — those omissions would rate High.

## CH-110 — API Auth Weakening to Token Forgery (Go)

| # | Query | Sev | File |
|---|---|---|---|
| F1 | `Use_of_Hardcoded_Password` | Medium | `auth-service/main.go` → `serviceAccountPassphrase` |
| F2 | `Client_Weak_Cryptographic_Hash` | Medium | `auth-service/public/js/checkout.js` → `sha1Hex()` |
| F3 | `JWT_No_Claims_Directives_Validation` | Low | `auth-service/main.go` → `parseJWTClaims()` |

---

## Why nothing here should rate High or Critical

| Avoided | How |
|---|---|
| SQL / command injection | No request data reaches any query or shell. SQL is parameter-bound or built from constants. |
| XSS | All user-derived output is escaped (`htmlspecialchars`, `escapeHtml`). |
| Path traversal (High) | The only traversal is the **stored** relative variant, sourced from a properties file. |
| Missing `USER` (High) | Every runtime Dockerfile sets `USER`. |
| Public S3 / open security groups | Public access blocked, encryption on, no `0.0.0.0/0` ingress. |
| Transitive CVEs | Node, Go and PHP services have **zero** third-party runtime dependencies. Java uses the servlet API at `provided` scope. Python uses one pinned current package. |
