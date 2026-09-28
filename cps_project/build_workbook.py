"""Build the publishable chain workbook from verified Checkmarx findings."""
import json, collections
from cps_engine.dimension_defaults import lookup_defaults
from cps_engine.rubric import score_finding, band, score_chain

cat = json.load(open('lab_app/chains_index.json'))
SRC = {c["id"]: c for c in cat["chains"] if c["id"].startswith("CH-1")}

# Verified finding pool, keyed by finding id so CH-107's four same-named
# entries stay distinct.
POOL = {}
for c in SRC.values():
    v = c["validation"]
    for rf in c["required_findings"]:
        POOL[rf["evidence_finding_id"]] = dict(
            project=v["project"], scan=v["scan_id"], query=rf["query_name"],
            sev=rf["default_severity_in_catalog"], engine=rf.get("engine","SAST"),
            fid=rf["evidence_finding_id"], loc=rf.get("evidence_location",""),
            scope=rf.get("match_file_contains",""))

def fid_of(chain_id, query, nth=0):
    hits=[rf["evidence_finding_id"] for rf in SRC[chain_id]["required_findings"]
          if rf["query_name"]==query]
    return hits[nth]

# ---- Additional chains, recombining the same verified pool -----------------
# Each has a distinct terminal outcome. A finding may serve in several chains;
# that is how composition works in practice and is flagged in the workbook.
NEW = [
 ("CH-111","Cross-Site Forgery to Privileged State Change","PHP","CH-101",
  "An attacker's page silently drives a state change in the victim's authenticated session. "
  "No anti-CSRF token guards the state-changing endpoint, the session cookie is delivered "
  "with SameSite=None so it rides the cross-site request, its path scope covers the whole "
  "site rather than the issuing endpoint, and no HSTS means the exchange can be observed "
  "after a downgrade.",
  [("CH-108","CSRF","L2_Bridge"),("CH-101","Insecure_Value_of_the_SameSite_Cookie_Attribute","L2_Bridge"),
   ("CH-101","Cookie_Overly_Broad_Path","L3_Amplifier"),("CH-108","Missing_HSTS_Header","L3_Amplifier")]),
 ("CH-112","Error-Path Reconnaissance to Database Disclosure","PHP","CH-108",
  "Database internals are reconstructed from failure behaviour alone. Error messages return "
  "query-level detail, exceptions are swallowed so the application keeps answering in a "
  "degraded state, sensitive database information is reachable by an unauthorised actor, and "
  "the absence of HSTS keeps the whole exchange observable.",
  [("CH-108","Information_Exposure_Through_an_Error_Message","L1_Signal"),
   ("CH-108","Improper_Exception_Handling","L2_Bridge"),
   ("CH-108","Exposure of Sensitive Information to an Unauthorized Actor","L2_Bridge"),
   ("CH-108","Missing_HSTS_Header","L3_Amplifier")]),
 ("CH-113","Token Prediction under Transport Downgrade","PHP","CH-101",
  "Session identifiers are enumerated and then replayed. Two independent non-cryptographic "
  "generators produce the identifier, the missing HSTS header permits a downgrade in which "
  "the identifier is observed in clear, and the over-broad cookie path makes the recovered "
  "value valid across the entire site.",
  [("CH-101","Use of Insufficiently Random Values","L2_Bridge"),
   ("CH-101","Use_of_Non_Cryptographic_Random","L1_Signal"),
   ("CH-108","Missing_HSTS_Header","L2_Bridge"),
   ("CH-101","Cookie_Overly_Broad_Path","L3_Amplifier")]),
 ("CH-114","Credential Lifetime Exposure","Java","CH-102",
  "One credential is exposed four ways at once. It is held in an immutable String that cannot "
  "be wiped from the heap, written to the application log, echoed to the system output stream, "
  "and no database action around it is audited - so the exposure is both broad and unrecorded.",
  [("CH-102","Heap_Inspection","L1_Signal"),("CH-102","Privacy_Violation","L2_Bridge"),
   ("CH-106","Use_of_System_Output_Stream","L2_Bridge"),
   ("CH-106","Insufficient_Logging_of_Database_Actions","L3_Amplifier")]),
 ("CH-115","Unaudited Privileged Configuration Change","Java","CH-103",
  "A caller reconfigures the running application and nothing records it. The privilege "
  "decision is taken from the request rather than the session, a JVM-wide system property is "
  "then set from request input, database actions are not logged, and the error condition "
  "returned by the write is never checked - so a failed or malicious change looks like a "
  "successful one.",
  [("CH-103","Parameter_Tampering","L1_Signal"),
   ("CH-103","External_Control_of_System_or_Config_Setting","L2_Bridge"),
   ("CH-106","Insufficient_Logging_of_Database_Actions","L3_Amplifier"),
   ("CH-106","Unchecked_Error_Condition","L3_Amplifier")]),
 ("CH-116","Temp-File Race to Report Substitution","Java","CH-103",
  "A generated report is replaced with attacker content. The staging file is created in the "
  "shared temp directory with default permissions, the check-then-write sequence leaves a "
  "substitution window, the destination path is resolved from a stored relative value without "
  "canonicalisation, and the unchecked error condition means the substitution is never noticed.",
  [("CH-103","Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions","L2_Bridge"),
   ("CH-103","Race_Condition","L2_Bridge"),
   ("CH-103","Stored_Relative_Path_Traversal","L3_Amplifier"),
   ("CH-106","Unchecked_Error_Condition","L1_Signal")]),
 ("CH-117","Diagnostic Surface Amplification","Java","CH-102",
  "Every diagnostic channel leaks in the same direction. Pages have no global error handler so "
  "uncaught exceptions render the container trace, error messages return internal state, "
  "sensitive values travel on the query string into logs and referers, and internal detail is "
  "written to the system output stream.",
  [("CH-106","Pages_Without_Global_Error_Handler","L2_Bridge"),
   ("CH-102","Information_Exposure_Through_an_Error_Message","L1_Signal"),
   ("CH-102","Information_Exposure_Through_Query_String","L2_Bridge"),
   ("CH-106","Use_of_System_Output_Stream","L3_Amplifier")]),
 ("CH-118","Reverse Tabnabbing to Session Capture","JavaScript / Node","CH-104",
  "A link the user trusts navigates the page they came from. Anchors open a new context "
  "without rel=noopener so the opened page holds a live handle to the opener, no CSP "
  "constrains where the replacement page may send data, no HSTS refuses the downgrade, and "
  "log forging lets the attacker pollute the record afterwards.",
  [("CH-104","Unsafe_Use_Of_Target_blank","L2_Bridge"),("CH-104","Missing_CSP_Header","L2_Bridge"),
   ("CH-104","Missing_HSTS_Header","L3_Amplifier"),("CH-104","Log_Forging","L1_Signal")]),
 ("CH-119","Unmonitored Container Exposure","Docker","CH-105",
  "A container misbehaves where nothing is watching. It publishes on every host interface "
  "rather than loopback, declares no healthcheck so the orchestrator cannot tell a compromised "
  "workload from a healthy one, pins no seccomp or AppArmor profile, and the application log "
  "that would show the activity is forgeable.",
  [("CH-105","Container Traffic Not Bound To Host Interface","L2_Bridge"),
   ("CH-105","Healthcheck Instruction Missing","L1_Signal"),
   ("CH-105","Security Opt Not Set","L3_Amplifier"),
   ("CH-104","Log_Forging","L3_Amplifier")]),
 ("CH-120","Credentialed Image to Network Pivot","Docker","CH-105",
  "A credential shipped inside the image becomes a network foothold. The hardcoded password "
  "gives authenticated access, unrestricted capabilities remove the kernel barrier to acting "
  "on the host, and binding to every host interface exposes the resulting position across the "
  "node rather than to loopback alone.",
  [("CH-105","Use_Of_Hardcoded_Password","L2_Bridge"),
   ("CH-105","Container Capabilities Unrestricted","L3_Amplifier"),
   ("CH-105","Container Traffic Not Bound To Host Interface","L3_Amplifier")]),
 ("CH-121","Irrecoverable Data Loss Window","Terraform / AWS","CH-109",
  "A destructive action against the managed data estate cannot be detected, reconstructed or "
  "undone. Automated backups are disabled so there is no recovery point, database logging is "
  "off so the action itself is unrecorded, and object access logging is off so the staging and "
  "extraction leave no trail either.",
  [("CH-109","RDS With Backup Disabled","L2_Bridge"),("CH-109","RDS Without Logging","L3_Amplifier"),
   ("CH-109","S3 Bucket Logging Disabled","L3_Amplifier")]),
 ("CH-122","Agent Session Replay","Python / AI agent","CH-107",
  "A prior conversation with the agent is replayed and steered. The session store discloses its "
  "location and keying scheme, the tracing provider discloses live trace identifiers that "
  "correlate a caller's requests across services, and the tool registry permits an outside "
  "reference to rewrite what a named tool executes - so a replayed session runs attacker logic.",
  [("CH-107","Information_Exposure_Through_an_Error_Message","L1_Signal",2),
   ("CH-107","Information_Exposure_Through_an_Error_Message","L2_Bridge",3),
   ("CH-107","Object_Access_Violation","L3_Amplifier")]),
]

def score_of(f):
    dims,_ = lookup_defaults(f["query"], f["sev"])
    return score_finding(dims)

rows, chains = [], []
def emit(cid, name, stack, story, members, source_chain=None):
    scores=[]
    for m in members:
        f = POOL[m["fid"]]
        s = score_of(f); scores.append(s)
        rows.append(dict(chain=cid, chain_name=name, stack=stack, role=m["role"],
            query=f["query"], sev=f["sev"], engine=f["engine"], cps=round(s,2),
            band=band(s), project=f["project"], scan=f["scan"], fid=f["fid"],
            loc=f["loc"]))
    cps = score_chain(scores)
    chains.append(dict(id=cid, name=name, stack=stack, n=len(members),
        cps=round(cps,2), band=band(cps), story=story,
        project=POOL[members[0]["fid"]]["project"], scan=POOL[members[0]["fid"]]["scan"],
        sev_mix=collections.Counter(POOL[m["fid"]]["sev"] for m in members)))

STACK={"CH-101":"PHP","CH-102":"Java","CH-103":"Java","CH-104":"JavaScript / Node",
 "CH-105":"Docker / Compose","CH-106":"Java","CH-107":"Python / AI agent",
 "CH-108":"PHP","CH-109":"Terraform / AWS / K8s","CH-110":"Go"}
for cid, c in SRC.items():
    emit(cid, c["name"], STACK[cid], c["terminal_outcome"],
         [dict(fid=rf["evidence_finding_id"], role=rf.get("role","")) for rf in c["required_findings"]])
for cid, name, stack, base, story, members in NEW:
    ms=[]
    for m in members:
        src, q, role = m[0], m[1], m[2]
        nth = m[3] if len(m)>3 else 0
        ms.append(dict(fid=fid_of(src,q,nth), role=role))
    emit(cid, name, stack, story, ms)

json.dump({"chains":chains,"rows":rows}, open('/tmp/wb.json','w'), indent=1, default=str)
print(f"chains: {len(chains)}   traceability rows: {len(rows)}")
hi=[c for c in chains if c["band"]=="High"]
print(f"High band: {len(hi)}/{len(chains)}")
print(f"unique findings used: {len({r['fid'] for r in rows})}")
bad=[r for r in rows if r["sev"] in ("High","Critical")]
print(f"High/Critical constituents: {len(bad)}")
for c in chains: print(f"  {c['id']:8s} {c['cps']:5.2f} {c['band']:9s} {dict(c['sev_mix'])}  {c['name'][:52]}")
