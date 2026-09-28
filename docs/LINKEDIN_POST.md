# LinkedIn post — CPS thought leadership (leader-level)

**Your scanner says you have zero critical vulnerabilities. That may be the most dangerous thing it tells you.**

Most AppSec programs triage by severity. Fix the Criticals, then the Highs, and get to the Mediums when there's time. The Lows and Informational findings? They sit in the backlog forever. Everyone knows this. Most of us built it on purpose.

Here's the problem I've been researching: attackers don't work down a severity list. They compose.

A predictable session ID (Medium). A cookie set with the wrong flag (Medium). A verbose error message (Low). On their own, none of these earns a sprint. Chained together, they're an account takeover — and no single finding in that chain would ever have been prioritized.

I wanted to know how far this goes, so I built a scoring model I call the **Chain Potential Score (CPS)** — it grades a *chain* of findings, not each finding alone — and then I stress-tested it against real scans.

The result that stopped me: I assembled a working exploit chain rated **High-impact** using findings a scanner had classified as **Informational**. Not Low. Informational — the tier below Low, the one most programs never even render in the backlog. Five findings a team would need to clear 554 higher-rated issues just to *see*, composing into silent data exfiltration.

Two things make this urgent now:

→ **AI collapses the cost of composition.** The hard part of chaining was never spotting the gaps — it was the patient work of wiring them together. That's exactly the work AI is now cheap at. The exploit that took a skilled attacker a week is getting faster.

→ **Severity is not risk.** A queue sorted by severity is a queue sorted by how easy each finding is to explain in isolation — not by what an attacker can actually do with your codebase.

To make this concrete and reproducible, I built a full specimen application — a working polyglot e-commerce app — that reproduces ten of these chains in one codebase, with **zero High or Critical findings anywhere in it.** Every chain reaches the High band purely by composition. It's open, it's scannable, and the full catalogue with attack paths is in the repo.

This isn't an argument to stop fixing Criticals. It's an argument to stop assuming the bottom of your backlog is safe just because each line item looks harmless.

The whole point of a chain is that it's built from parts nobody thought were worth fixing.

Repo, methodology, and the ten validated chains: **github.com/cxsmtp/CPS-DEMO**

*What's the lowest-severity finding you've ever seen turn into a real breach? I'd like to hear it.*

#ApplicationSecurity #AppSec #DevSecOps #AISecurity #VulnerabilityManagement
