"""Nexa Commerce chain definitions - every finding originates in code we wrote."""

SCAN_V1 = "cc434dd7-3e6b-4df0-8ccf-b43ac3ec7678"

# (ref, engine, query, severity, file, line, result_id or "", status)
CONFIRMED = "Confirmed in scan cc434dd7"
PENDING   = "Pending v2 re-scan"

CHAINS = [
 dict(id="NX-01", name="Predictable Session to Account Takeover", service="storefront",
   stack="PHP 8.3", cps=9.55,
   outcome="Full takeover of any customer session without stealing a credential.",
   findings=[
     ("F1","SAST","Use of Insufficiently Random Values","Medium","storefront/public/login.php","30-33","",PENDING),
     ("F2","SAST","Broken_or_Risky_Hashing_Function","Medium","storefront/public/login.php","40","",PENDING),
     ("F3","SAST","Insecure_Value_of_the_SameSite_Cookie_Attribute","Medium","storefront/public/login.php","49-60","LP9LVOzghsVbI1vYCJxrCHR23n4=",CONFIRMED),
     ("F4","SAST","Cookie_Overly_Broad_Path","Low","storefront/public/login.php","49-60","LrfnsakFDfvvkYiwdzwMVCVT8Fc=",CONFIRMED),
   ],
   path=[
     ("Observe the clock","Request any storefront page and read the HTTP Date header. login.php seeds the generator with mt_srand(time()), so the Date header hands the attacker the seed to within one second.","F1"),
     ("Enumerate the identifier","For each candidate second, replay mt_srand(seed) locally and generate the two mt_rand(100000,999999) values. The session id is base36(time) + '.' + A + B, so the whole space for a one-minute window is 60 candidates, not 10^12.","F1"),
     ("Forge the signature","The cookie pair is (nexa_sid, nexa_sig) where nexa_sig = md5(sid + ':' + secret). MD5 is not an HMAC and offers no key separation, so once the secret is recovered - by length-extension, by offline brute force, or from any of the disclosure findings in NX-02 - the attacker computes a valid signature for any forged sid.","F2"),
     ("Deliver the cookie cross-site","The cookie is written with SameSite=None, so it is transmitted on requests initiated from an attacker-controlled origin. The victim does not need to be phished onto a lookalike domain; a hidden request from any page they visit carries it.","F3"),
     ("Ride the session site-wide","Path=/ means the forged pair authenticates against every endpoint, not just the issuing one - /cart.php, /checkout.php and any future admin route inherit it.","F4"),
     ("Outcome","The attacker acts as the victim for the cookie's full one-hour lifetime. No password was captured and no High-severity finding was involved.",""),
   ]),
 dict(id="NX-02", name="Defence-in-Depth Erosion to Checkout Fraud", service="storefront",
   stack="PHP 8.3", cps=7.62,
   outcome="Attacker-placed orders on a victim's account, plus database credentials for reuse.",
   findings=[
     ("F1","SAST","CSRF","Medium","storefront/public/checkout.php","61-70","",PENDING),
     ("F2","SAST","Missing_HSTS_Header","Medium","storefront/public/checkout.php","22-30","",PENDING),
     ("F3","SAST","Improper_Exception_Handling","Low","storefront/public/checkout.php","72-78","",PENDING),
     ("F4","SAST","Information_Exposure_Through_an_Error_Message","Low","storefront/public/checkout.php","40-48","",PENDING),
   ],
   path=[
     ("Force the connection down","No Strict-Transport-Security header is ever written, so a network-positioned attacker can strip TLS on the first navigation and the browser will not refuse it.","F2"),
     ("Read the session cookie in clear","Over the downgraded channel the nexa_sid / nexa_sig pair is visible, which also feeds NX-01.","F2"),
     ("Provoke the failure path","Point the storefront at an unreachable database, or simply race it during a restart. checkout.php catches PDOException and echoes the DSN, the account name and the raw driver message straight to the response body.","F4"),
     ("Harvest the credentials","The response now contains the connection string and the database account name - reusable against any other service sharing that account.","F4"),
     ("Submit the forged order","The order form performs a state-changing POST with no anti-CSRF token and no origin check. A form auto-submitted from an attacker page places an order on the victim's session.","F1"),
     ("Ensure it looks successful","The insert is wrapped in a catch that discards the exception, so the customer receives an order-placed confirmation whether or not the row was written - the discrepancy surfaces only in reconciliation, days later.","F3"),
   ]),
 dict(id="NX-03", name="Error-Leak to Credential Disclosure", service="catalog-service",
   stack="Java 17 / Jakarta Servlet", cps=9.48,
   outcome="Customer credentials and billing identifiers reconstructed without any injection flaw.",
   findings=[
     ("F1","SAST","Information_Exposure_Through_Query_String","Medium","catalog-service/.../CatalogServlet.java","48-52","",PENDING),
     ("F2","SAST","Exposure of Sensitive Information to an Unauthorized Actor","Medium","catalog-service/.../AccountServlet.java","62-72","",PENDING),
     ("F3","SAST","Privacy_Violation","Medium","catalog-service/.../AccountServlet.java","48-51","",PENDING),
     ("F4","SAST","Information_Exposure_Through_an_Error_Message","Low","catalog-service/.../CatalogServlet.java","34","UHUxxVQtJ43G2rAPTE/+et6h+v0=",CONFIRMED),
     ("F5","SAST","Heap_Inspection","Low","catalog-service/.../AccountServlet.java","36","",PENDING),
   ],
   path=[
     ("Map the stack","Request /api/catalog with a malformed parameter. The catch block writes the exception and a full printStackTrace into the response body, disclosing framework, version, package layout and internal class names.","F4"),
     ("Capture tokens from the URL","/api/catalog issues a redirect to /checkout?session_token=...&customer_email=... The token and the email now sit in the query string, which means they land in proxy logs, browser history and the Referer header of every onward request to third-party assets.","F1"),
     ("Pull the billing record","POST /api/account with the customer_ref learned above. The servlet returns internal_key, stored_card_last4 and billing_account with no authorisation check between the caller and the record.","F2"),
     ("Recover the passphrase from logs","The same request writes 'account update ref=... email=... password=...' to the application log. Anyone with log-read access - an SRE, a log-shipping vendor, a compromised aggregator - now holds the plaintext credential.","F3"),
     ("Recover it from memory too","The passphrase is retained in a String field on the servlet instance. Strings are immutable and cannot be wiped, so it persists in the heap and appears in any crash dump or heap snapshot taken later.","F5"),
     ("Outcome","Email, passphrase, internal key and billing identifiers - assembled purely from disclosure. No injection, no traversal, nothing above Medium.",""),
   ]),
 dict(id="NX-04", name="Config Tamper to Arbitrary File Write", service="catalog-service",
   stack="Java 17 / Jakarta Servlet", cps=9.96,
   outcome="Attacker-controlled file written outside the report directory, leading to code execution.",
   findings=[
     ("F1","SAST","External_Control_of_System_or_Config_Setting","Medium","catalog-service/.../ConfigServlet.java","44","I/7OE/sSBnmbSNHMJiMcWr6utmU=",CONFIRMED),
     ("F2","SAST","Parameter_Tampering","Medium","catalog-service/.../ConfigServlet.java","32-40","",PENDING),
     ("F3","SAST","Stored_Relative_Path_Traversal","Medium","catalog-service/.../ReportBuilder.java","48-52","",PENDING),
     ("F4","SAST","Creation_of_Temp_File_With_Insecure_Permissions","Low","catalog-service/.../ReportBuilder.java","59","sE+dyQtToO+tPv4lx2b4meetWLU=",CONFIRMED),
     ("F5","SAST","Race_Condition","Low","catalog-service/.../ReportBuilder.java","61-66","",PENDING),
   ],
   path=[
     ("Grant yourself the role","POST /api/ops/config?role=merchandiser. The privilege decision reads the role straight from the request rather than the authenticated session, so the caller declares their own authorisation level.","F2"),
     ("Reach the configuration","With the role accepted, the same request writes request parameters into JVM-wide system properties via System.setProperty - state shared by every thread in the container.","F1"),
     ("Point the report elsewhere","The report directory is read from the settings table and joined with plain string concatenation, no canonicalisation. A stored value of '../../../usr/local/tomcat/webapps/ROOT' escapes the intended directory.","F3"),
     ("Win the staging race","writeReport creates its staging file in the shared system temp directory with default permissions, then does exists() / delete() / write. Any local process can replace that path between the check and the write, substituting its own content.","F4,F5"),
     ("Land the payload","renameTo moves the substituted file to the traversed destination. A .jsp written under the webapp root is compiled and served by the container on next request.","F3"),
     ("Outcome","Remote code execution assembled from three Mediums and two Lows. No single finding is rated High.",""),
   ]),
 dict(id="NX-05", name="Informational-Only Chain to Silent Data Exfiltration", service="catalog-service",
   stack="Java 17 / Jakarta Servlet", cps=9.14,
   outcome="Data extraction that leaves no audit trail - built entirely from Informational findings.",
   findings=[
     ("F1","SAST","Dynamic_SQL_Queries","Informational","catalog-service/.../InventoryDao.java","41-45","",PENDING),
     ("F2","SAST","Insufficient_Logging_of_Database_Actions","Informational","catalog-service/.../InventoryDao.java","47-58","",PENDING),
     ("F3","SAST","Pages_Without_Global_Error_Handler","Informational","catalog-service/.../webapp/admin/dashboard.jsp","1","",PENDING),
     ("F4","SAST","Unchecked_Error_Condition","Informational","catalog-service/.../InventoryDao.java","72-76","",PENDING),
     ("F5","SAST","Use_of_System_Output_Stream","Informational","catalog-service/.../InventoryDao.java","46","",PENDING),
   ],
   path=[
     ("Find the query surface","Statements are assembled by string concatenation rather than prepared. Today the concatenated values are constants, but the pattern means any future maintainer who substitutes a request value creates injection with no structural barrier in the way - and the analyser will still rate the construction Informational.","F1"),
     ("Confirm nothing is recorded","No audit record is written for the read or its result set. The only trace is a line on the system output stream, which in a container goes to stdout and is rotated or discarded rather than retained as an audit log.","F2,F5"),
     ("Trigger the trace","Hit /admin/dashboard.jsp while the database is unavailable. The JSP declares no errorPage and web.xml declares no error-page, so the container's default trace is rendered to the caller, disclosing SQL text, driver internals and file paths.","F3"),
     ("Operate undetected","Writes call execute() and getUpdateCount() and discard both return values, so a statement that silently affected nothing is indistinguishable from one that succeeded. Tampering does not surface as an error.","F4"),
     ("Outcome","A functioning extraction and tamper path where every constituent finding is Informational - the tier below Low, which most programmes never render in a backlog at all.",""),
   ]),
 dict(id="NX-06", name="Redirect to Token Theft", service="web-gateway",
   stack="Node 22", cps=9.13,
   outcome="Session handle delivered to an attacker-controlled origin, with the audit trail poisoned.",
   findings=[
     ("F1","SAST","Open_Redirect","Medium","web-gateway/src/server.js","86","JC8IH8Ezh474NyadGwbv+sAebck=",CONFIRMED),
     ("F2","SAST","Missing_HSTS_Header","Medium","web-gateway/src/server.js","68-78","",PENDING),
     ("F3","SAST","Missing_CSP_Header","Low","web-gateway/src/server.js","68-78","",PENDING),
     ("F4","SAST","Unsafe_Use_Of_Target_blank","Low","web-gateway/src/views/product.html","-","",PENDING),
     ("F5","SAST","Log_Forging","Low","web-gateway/src/server.js","69, 85","n6Ek0rV+jtRmdWCufmCtVqcK5dw=",CONFIRMED),
   ],
   path=[
     ("Send the victim a legitimate link","/signin/complete?return_to=https://attacker.example/callback - the host and path are the real storefront, so the link survives inspection and link-preview scanners.","F1"),
     ("Collect the handle","completeSignIn appends the freshly minted session handle to the attacker's URL and issues a 302. The handle arrives at the attacker's server as a query parameter, in the clear, with no allow-list ever consulted.","F1"),
     ("Alternative route - reverse tabnabbing","If the victim instead opens one of the partner links, the anchor has target=_blank with no rel=noopener, so the opened page holds a live window.opener handle and can navigate the storefront tab to a credential-harvesting clone.","F4"),
     ("Nothing blocks the outbound request","No Content-Security-Policy is set, so no policy constrains where the page may send data or which origins may frame it.","F3"),
     ("Nothing refuses the downgrade","No Strict-Transport-Security means the whole exchange can be observed after a TLS strip.","F2"),
     ("Erase the trail","auditRequest writes the raw actor query parameter into the log. A value containing CR/LF injects fabricated log lines, so the responder reconstructing the incident sees plausible entries that never happened.","F5"),
   ]),
 dict(id="NX-07", name="API Auth Weakening to Token Forgery", service="auth-service",
   stack="Go 1.22", cps=8.18,
   outcome="Forged bearer token accepted with attacker-chosen claims and no expiry.",
   findings=[
     ("F1","SAST","Use_of_Hardcoded_Password","Medium","auth-service/main.go","27","",PENDING),
     ("F2","SAST","Client_Weak_Cryptographic_Hash","Medium","auth-service/public/js/checkout.js","54","",CONFIRMED),
     ("F3","SAST","JWT_No_Claims_Directives_Validation","Low","auth-service/main.go","48-61","",PENDING),
   ],
   path=[
     ("Extract the key from the artefact","serviceAccountPassword is compiled into the binary and is also the JWT signing key. Anyone who can pull the image, read the registry, or run 'strings' on the binary holds it.","F1"),
     ("Confirm the derivation client-side","public/js/checkout.js reproduces the order digest with SHA-1 over the same value, so the derivation can be verified in a browser before any server request is made. SHA-1 is collision-broken, so the digest proves nothing about who computed it.","F2"),
     ("Mint a token","Sign a JWT with the recovered key carrying sub=<victim> and role=admin.","F1"),
     ("Bypass every claim check","parseJWTClaims constructs jwt.NewParser() with no claims directives - no expiry check, no issuer check, no audience check. The forged token is accepted, and because exp is never evaluated it never stops being accepted.","F3"),
     ("Outcome","Persistent authentication bypass against the API from two Mediums and one Low.",""),
   ]),
 dict(id="NX-08", name="Agent Tool-Path Disclosure to Tool Poisoning", service="assistant-service",
   stack="Python 3.12 + OpenAI", cps=9.04,
   outcome="Complete map of the agent's tool and MCP surface, enabling a tool-poisoning payload the model executes.",
   findings=[
     ("F1","SAST","Object_Access_Violation","Medium","assistant-service/src/agents/tool.py","apply_overrides","",PENDING),
     ("F2","SAST","Information_Exposure_Through_an_Error_Message","Low","assistant-service/src/agents/mcp/util.py","decode_envelope","",PENDING),
     ("F3","SAST","Information_Exposure_Through_an_Error_Message","Low","assistant-service/src/agents/run_internal/tool_actions.py","execute","",PENDING),
     ("F4","SAST","Information_Exposure_Through_an_Error_Message","Low","assistant-service/src/agents/run_internal/session_persistence.py","load_turns","",PENDING),
     ("F5","SAST","Information_Exposure_Through_an_Error_Message","Low","assistant-service/src/agents/tracing/provider.py","export","",PENDING),
   ],
   path=[
     ("Make one tool call fail","Ask the assistant something that drives a tool call with a malformed argument. ToolExecutionError returns the tool's description, its internals and the full list of registered tool names - the agent's entire tool schema from a single failed request.","F3"),
     ("Map the MCP transport","Provoke an envelope decode failure. McpTransportError returns the MCP endpoint, the transport version and the negotiated capabilities, describing exactly how the agent reaches the catalogue tools.","F2"),
     ("Learn how sessions are keyed","A session load failure returns the absolute store path and the table schema, which is enough to know how a conversation is addressed and therefore how one could be replayed.","F4"),
     ("Correlate across services","A trace export failure returns the collector URL and the live trace id, which correlates the attacker's requests with the victim's across every downstream service the assistant touches.","F5"),
     ("Rewrite what a tool does","apply_overrides walks the target object's __dict__ and writes each attribute back with setattr, bypassing the class's own accessors. Anything holding a reference to the registry can replace a named tool's _handler, so the tool the model believes it is calling is no longer the tool that runs.","F1"),
     ("Outcome","The model faithfully executes the poisoned tool. One Medium and four Lows, in a production agent framework layout.",""),
   ]),
 dict(id="NX-09", name="Container Escape Surface", service="ops/seed + compose",
   stack="Docker / Compose", cps=9.46,
   outcome="Escape from container to host, then lateral movement across the node.",
   findings=[
     ("F1","SAST","Use_Of_Hardcoded_Password","Medium","ops/seed/seed.js","15","tHYT8FVsSDsnAHGCwgpL/SEZZBI=",CONFIRMED),
     ("F2","IaC (KICS)","Container Capabilities Unrestricted","Medium","docker-compose.yml","cap_add","",PENDING),
     ("F3","IaC (KICS)","Security Opt Not Set","Medium","docker-compose.yml","services","",PENDING),
     ("F4","IaC (KICS)","Container Traffic Not Bound To Host Interface","Medium","docker-compose.yml","ports","",PENDING),
     ("F5","IaC (KICS)","Healthcheck Instruction Missing","Low","ops/seed/Dockerfile","-","",PENDING),
   ],
   path=[
     ("Pull the credential out of the image","seed.js carries the operational database password as a literal. Anyone who can pull the seed image - or read the registry, or inspect a layer - has an authenticated foothold with no exploitation required.","F1"),
     ("Reach the service from off-host","Services publish as '8080:8080' rather than '127.0.0.1:8080:8080', so every container port is bound to all host interfaces and reachable from the network rather than from loopback alone.","F4"),
     ("Act with kernel privileges","The storefront adds NET_ADMIN and the catalog service adds SYS_PTRACE on top of the default capability set, with no cap_drop: ALL. SYS_PTRACE permits attaching to and reading the memory of other processes; NET_ADMIN permits reconfiguring the container's networking.","F2"),
     ("Cross the last barrier","No security_opt is declared, so neither seccomp nor AppArmor is pinned and only the daemon default applies. Combined with the added capabilities, the syscall surface needed for a container escape is available.","F3"),
     ("Stay unnoticed","The seed container declares no HEALTHCHECK, so the orchestrator has no signal distinguishing a container doing its one-shot job from one that has been repurposed and is still running.","F5"),
     ("Outcome","Host compromise. The SAST finding and the IaC findings are owned by different teams, which is precisely why neither is escalated alone.",""),
   ]),
 dict(id="NX-10", name="Cloud Exfiltration Blindness", service="deploy/terraform + k8s",
   stack="Terraform / AWS / Kubernetes", cps=8.32,
   outcome="Data extraction that is permitted by policy, invisible to telemetry and unrecoverable.",
   findings=[
     ("F1","IaC (KICS)","IAM policy allows for data exfiltration","Medium","deploy/terraform/iam.tf","aws_iam_role_policy","",PENDING),
     ("F2","IaC (KICS)","S3 Bucket Logging Disabled","Medium","deploy/terraform/s3.tf","order_documents","",PENDING),
     ("F3","IaC (KICS)","RDS Without Logging","Medium","deploy/terraform/rds.tf","orders","",PENDING),
     ("F4","IaC (KICS)","RDS With Backup Disabled","Medium","deploy/terraform/rds.tf","backup_retention_period","",PENDING),
     ("F5","IaC (KICS)","Using Unrecommended Namespace","Medium","deploy/k8s/deployment.yaml","namespace: default","",PENDING),
   ],
   path=[
     ("Take the pod","The workload runs in the default namespace, so anything else with default-namespace access can reach it and no namespace-scoped policy isolates it. Compromise of any neighbouring workload reaches this one.","F5"),
     ("Assume the role","The pod carries the order-service role, whose policy grants s3:GetObject, s3:ListBucket, s3:PutObject and s3:PutObjectAcl on Resource '*', plus rds:CreateDBSnapshot, rds:CopyDBSnapshot and rds:ModifyDBSnapshotAttribute.","F1"),
     ("Stage and extract","Read every object in the order-document bucket and write it to a bucket the attacker controls - both operations are permitted outright. Snapshot the order database and share the snapshot to an external account with ModifyDBSnapshotAttribute. Nothing here is an exploit; it is the policy working as written.","F1"),
     ("Leave no object trail","No aws_s3_bucket_logging resource targets the bucket, so object-level reads produce no server access log. What left the bucket cannot be reconstructed.","F2"),
     ("Leave no database trail","enabled_cloudwatch_logs_exports is unset, so no postgresql log reaches CloudWatch and the snapshot activity is unrecorded.","F3"),
     ("Remove the recovery point","backup_retention_period is 0, disabling automated backups outright. There is no point-in-time recovery to bound the damage or to diff against for proof of what changed.","F4"),
     ("Outcome","A breach that cannot be detected, reconstructed or recovered from - assembled from five Medium misconfigurations and zero exploits.",""),
   ]),
]

CHAINS += [
 dict(id="NX-11", name="AI-BOM Model Surface Disclosure to Prompt-Path Targeting", service="assistant-service",
   stack="Python 3.12 + OpenAI (AI-BOM)", cps=8.04,
   outcome="An attacker enumerates the exact AI models and tool transport the agent depends on, then targets the weakest one.",
   findings=[
     ("F1","AISC (AI-BOM)","AI model component: OpenAI gpt-4o","Medium","assistant-service/ai-bom.cdx.json","components[0]","",PENDING),
     ("F2","AISC (AI-BOM)","AI model component: OpenAI gpt-4o-mini","Low","assistant-service/ai-bom.cdx.json","components[1]","",PENDING),
     ("F3","AISC (AI-BOM)","AI library component: Model Context Protocol","Medium","assistant-service/ai-bom.cdx.json","components[2]","",PENDING),
     ("F4","SAST","Information_Exposure_Through_an_Error_Message","Low","assistant-service/src/agents/mcp/util.py","decode_envelope","",PENDING),
   ],
   path=[
     ("Enumerate the model inventory","AISC parses ai-bom.cdx.json and enumerates the declared AI components. An attacker who reads the AI-BOM - or reconstructs it from the disclosure findings - learns the agent runs gpt-4o as primary and gpt-4o-mini as a pre-filter classifier.","F1,F2"),
     ("Identify the weakest link","The classifier (gpt-4o-mini) runs first and is cheaper and less capable. Knowing the two-model topology, the attacker crafts input that passes the classifier's intent check but carries a payload for the primary model.","F2"),
     ("Map the tool transport","The AI-BOM declares the MCP client and its internal endpoint. This tells the attacker the agent reaches catalogue tools over MCP at a named internal host - the surface to target for tool poisoning (see NX-08).","F3"),
     ("Confirm the wiring at runtime","An MCP envelope decode failure returns the endpoint and negotiated capabilities, corroborating the AI-BOM declaration and confirming the transport is live.","F4"),
     ("Outcome","The AI-BOM, meant for supply-chain transparency, doubles as a targeting map: exact models, their roles, and the tool transport between them. Note: AISC findings are readable only via CycloneDX export, not the listFindings API.",""),
   ]),
 dict(id="NX-12", name="Committed Secrets to Multi-Service Credential Compromise", service="assistant-service",
   stack="Python 3.12 / config", cps=8.18,
   outcome="Four live-shaped credentials in version control give an attacker AWS, JWT-signing, database and API access at once.",
   findings=[
     ("F1","Secret Detection","Hardcoded AWS access key","Medium","assistant-service/config/agent.env","8-9","",PENDING),
     ("F2","Secret Detection","Hardcoded JWT signing secret","Medium","assistant-service/config/agent.env","12","",PENDING),
     ("F3","Secret Detection","Database URL with inline credentials","Medium","assistant-service/config/agent.env","15","",PENDING),
     ("F4","Secret Detection","Hardcoded API token","Low","assistant-service/config/agent.env","18","",PENDING),
   ],
   path=[
     ("Clone the repository","agent.env is committed to version control. Anyone with read access to the repo - a contractor, a leaked mirror, a fork - has the file. Secret-detection flags exactly this: credentials living in source control.","F1,F2,F3,F4"),
     ("Assume the AWS identity","The AWS access key pair grants whatever the IAM principal allows. Combined with NX-10's over-broad IAM policy, this is a direct path to the order-document bucket and RDS snapshots.","F1"),
     ("Forge auth tokens","The JWT signing secret is the same key the Go auth service uses (NX-07). With it, an attacker mints valid tokens with any claims - this secret in the repo is a second, easier route to the NX-07 outcome.","F2"),
     ("Connect to the database directly","The database URL carries inline username and password, so the attacker connects to catalog-db without going through the application at all.","F3"),
     ("Call internal APIs","The API token authenticates to the catalogue API, rounding out access across every tier.","F4"),
     ("Outcome","One committed file compromises four independent trust boundaries. Each secret is Medium or Low individually; together they are total credential compromise, and they bridge into NX-07 and NX-10.",""),
   ]),
 dict(id="NX-13", name="Vulnerable Dependencies to Assistant Compromise", service="assistant-service",
   stack="Python 3.12 (SCA)", cps=7.54,
   outcome="Two Medium-rated dependency advisories combine into template escape plus silent TLS downgrade in the AI assistant.",
   findings=[
     ("F1","SCA","CVE-2024-56326 (Jinja2 3.0.1 sandbox escape)","Medium","assistant-service/requirements.txt","Jinja2==3.0.1","",PENDING),
     ("F2","SCA","CVE-2024-35195 (requests 2.25.1 sticky verify=False)","Medium","assistant-service/requirements.txt","requests==2.25.1","",PENDING),
     ("F3","SAST","Information_Exposure_Through_an_Error_Message","Low","assistant-service/src/agents/mcp/util.py","decode_envelope","",PENDING),
   ],
   path=[
     ("Identify the pinned versions","SCA reports Jinja2 3.0.1 and requests 2.25.1 in requirements.txt, both with public advisories. An attacker reads the same manifest from the repo.","F1,F2"),
     ("Escape the template sandbox","render.py uses Jinja2 3.0.1 to render assistant replies. CVE-2024-56326 lets an attacker who controls template content store a reference to a malicious str.format and escape the sandbox to arbitrary Python. If any reply-template fragment ever derives from user input, this is remote code execution in the assistant.","F1"),
     ("Poison the enrichment channel","fetch_enrichment uses requests 2.25.1. CVE-2024-35195 means one early verify=False call makes the pooled connection ignore certificate verification for its whole lifetime, so a network attacker can MITM the assistant's outbound catalogue fetches silently.","F2"),
     ("Confirm the internal topology","An MCP decode error discloses the internal endpoint the assistant talks to, helping the attacker position the MITM.","F3"),
     ("Outcome","Two Medium dependency advisories - not our code - compose into template RCE plus silent transport downgrade in the AI assistant. Neither rates High alone.",""),
   ]),
]

# ---- Enrich existing chains with cross-engine participants ----
for _c in CHAINS:
    if _c["id"] == "NX-07":
        _c["findings"].append(
          ("F4","Secret Detection","Hardcoded JWT signing secret","Medium","assistant-service/config/agent.env","12","",PENDING))
        _c["path"].insert(1,
          ("Shortcut - read the key from the repo","The same signing secret is committed in config/agent.env and flagged by secret-detection (NX-12 F2). An attacker who has the repo skips key recovery entirely and proceeds straight to forging tokens.","F4"))
    if _c["id"] == "NX-08":
        _c["findings"].append(
          ("F6","AISC (AI-BOM)","AI library component: Model Context Protocol","Medium","assistant-service/ai-bom.cdx.json","components[2]","",PENDING))
        _c["path"].insert(1,
          ("Read the tool transport from the AI-BOM","ai-bom.cdx.json declares the MCP client and its internal endpoint (NX-11 F3), so the attacker knows the transport to target before provoking a single error.","F6"))
    if _c["id"] == "NX-09":
        _c["findings"].append(
          ("F6","Secret Detection","Database URL with inline credentials","Medium","assistant-service/config/agent.env","15","",PENDING))
        _c["path"].insert(1,
          ("Reuse the committed DB credential","The operational database URL is also committed in config/agent.env and flagged by secret-detection (NX-12 F3), a second source for the same foothold the hardcoded seed password provides.","F6"))
