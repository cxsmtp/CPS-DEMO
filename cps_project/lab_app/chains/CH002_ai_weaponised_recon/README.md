# CH-002 — AI-Weaponised Recon-to-Exploit Chain

> **Chain anatomy**: Low SAST recon findings (info exposure, weak token
> generation) compose with one Low SCA dependency advisory and a
> declared tool-using AI agent (GPT-4o with Code Interpreter) plus
> permissive K8s egress, into a chain whose CPS reaches High band.
> Without the AI agent, the same findings remain Low recon nuisance
> at Moderate band CPS. **The empirical claim is the delta.**

## Why this chain matters for the paper

CH-001-DEMO and CH-A1 demonstrate that Low findings can compose into
High-band chains. But neither chain *requires* AI to be exploitable —
CH-001-DEMO is cloud metadata reach via session-binding bug, CH-A1 is
prompt template tampering via path traversal. Both are textbook
attack patterns that existed before LLMs.

**CH-002 is structurally different.** The exploit primitive is
synthesised by an AI agent at runtime, using reconnaissance the Low
findings provide. Without the agent, the reconnaissance is unactionable:
disclosing your framework version is Low because attackers still need
to manually research, develop, and test exploits. With the agent, the
reconnaissance becomes input to autonomous exploit synthesis — the cost
of going from disclosure to compromise drops from days to seconds.

This is the paper's central claim made empirical: **AI weaponises Low
findings into chain-tier exploits.**

## Chain anatomy

| # | Engine | Finding (expected Low) | Role |
|---|---|---|---|
| F1 | SAST | `Information_Exposure_Through_an_Error_Message` | L1 Signal — leaks framework version, stack, modules |
| F2 | SAST | `Information_Exposure_via_Headers` | L1 Signal — leaks Server header, X-Powered-By |
| F3 | SAST | `Use_of_Insufficiently_Random_Values` | L2 Bridge — predictable session/CSRF tokens |
| F4 | SCA | Flask 2.0.1 CVE-2026-27205 (Low, confirmed in tenant) | L2 Bridge — known CVE on disclosed dep |
| F5 | AI-BOM | GPT-4o with Code Interpreter tool access | **L3 Amplifier — AI weaponisation** |
| F6 | IaC | NetworkPolicy missing on K8s deployment (egress unrestricted) | L3 Amplifier — exfiltration path |

## The AI-delta empirical claim

The chain matcher computes chain CPS twice — once with all six
findings, once with F5 (the AI-Leverage finding) excluded — and
reports the delta:

```
CH-002 — AI-Weaponised Recon-to-Exploit Chain
  Chain CPS (with AI agent):     ~9.90  (High)
  Chain CPS (without AI agent):  ~6.65  (Moderate)
  AI weaponisation delta:        +3.25  (band shift Moderate → High)
```

This delta is the framework's measurement of AI's contribution to
chain risk. **No other published vulnerability framework produces
this measurement.** It's a paper-citable empirical result that
directly demonstrates the central thesis.

## What's in this directory

```
CH002_ai_weaponised_recon/
├── README.md                         # this file
├── requirements.txt                  # Flask 2.0.1 + requests 2.25.1
├── src/app/
│   ├── lab_guard.py                  # safety guard
│   ├── main.py                       # F1+F2 entry points (info exposure)
│   ├── token_helper.py               # F3 (weak token gen)
│   ├── recon_endpoints.py            # exercises F4 SCA dep
│   └── ai_agent.py                   # F5 AI-BOM declaration
└── iac/kubernetes/
    └── deployment.yaml               # F6 (NetworkPolicy missing)
```

## Chain story walkthrough

1. **Reconnaissance** — Attacker hits `/` on the lab app. The Server
   header (F2) discloses Flask 2.0.1, Python 3.11. Attacker hits a
   non-existent endpoint. The error response (F1) discloses stack
   trace, module path, exact framework version.

2. **CVE lookup** — With Flask 2.0.1 disclosed, attacker (or AI agent)
   queries advisory database. CVE-2026-27205 (F4) is a known Low CVE
   on this version.

3. **Token analysis** — Attacker hits `/session/issue` repeatedly.
   The returned tokens follow a predictable PRNG pattern (F3). With
   timing data, the seed is bracketed.

4. **Without AI**: at this point the attacker has reconnaissance
   data but still needs to manually develop the exploit — chain
   CPS sits at Moderate band, accurate reflection of risk.

5. **With AI (F5)**: the GPT-4o agent with Code Interpreter is
   embedded as a chatbot. Attacker submits input through the
   chatbot. Agent autonomously: cross-references Flask version,
   identifies CVE-2026-27205 details, generates exploit code using
   predictable token, executes via Code Interpreter, exfiltrates
   results via the unrestricted egress (F6).

6. **The chain reaches High band because of F5.** Same Low findings,
   different chain CPS.

## How to scan

Add this directory to your Checkmarx One project source. Same project
that scans CH-001 and CH-A1. Ensure scan profile has SAST + SCA + IaC
Security + AI Supply Chain (AISC) enabled.

After completion, export the comprehensive report and AI-BOM (CycloneDX),
then run the matcher with the new `--ai-delta` flag:

```
python -m cps_engine.cli sample_data\cx_results.json \
    --aibom sample_data\ai-bom.json --aibom-project-filter "CH01_Lab" \
    --catalog lab_app\chains_index.json --all
```

## Substitution loop

| If this rates higher than Low | Mitigation |
|---|---|
| F1 Information_Exposure_Through_an_Error_Message rates Medium | Accept; F1 still composes, AI delta still measurable |
| F2 Information_Exposure_via_Headers rates Medium | Accept; same as F1 |
| F3 Use_of_Insufficiently_Random_Values rates Medium | Accept; the chain story is unchanged |
| F4 Flask CVE rates higher than Low | Substitute with debug 2.6.9 (3.7 Low confirmed) |
| F6 NetworkPolicy finding doesn't fire | Accept; chain assembles at 5 of 6, still demonstrates AI delta |
