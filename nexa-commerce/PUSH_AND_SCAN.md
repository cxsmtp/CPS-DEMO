# Push v3 and re-scan — one-page runbook

This bundle contains the **v3 Nexa Commerce** codebase: all ten chains plus the
three engine surfaces that were missing from the v1 scan — **secrets, AI-BOM and
SCA** — with the earlier Critical XSS and High transport defects already fixed.

The code is complete. The only thing left is to get it into the GitHub repo
(`github.com/cxsmtp/CPS-DEMO`) so Checkmarx can scan it, because Checkmarx pulls
from the repo, not from any local copy.

Pick **one** of the two routes below.

---

## Route A — Claude Code (does the push AND the scan for you)

Run this from inside your local `CPS-DEMO` clone, with the v3 tarball present:

1. Make sure the Checkmarx MCP is connected once:

    ```bash
    claude mcp add --transport http checkmarx \
      https://deu.ast.checkmarx.net/api/security-mcp/mcp/checkmarx-global-services-internal
    ```

2. Start Claude Code in the repo and paste this prompt:

    > Extract nexa-commerce-v3-allengines.tar.gz over the nexa-commerce/ directory
    > (replace it entirely). Run `go mod tidy` in nexa-commerce/auth-service. Commit
    > everything and push to main. Then scan the repo with Checkmarx via the checkmarx
    > MCP, API mode, project CPS-DEMO (id d182f9ec-bb1e-40fb-9b79-12dbb96f7f1c), all
    > engines: sast, sca, kics, containers, secret-detection. Poll until complete, then
    > report which chains from nexa-commerce/CHAIN_MAP.md now assemble and list every
    > secret, AI-BOM and SCA finding with its file and severity. Do not fix anything —
    > just report.

That's the whole flow — push and scan, no manual git.

---

## Route B — three git commands, then tell me

Run these from inside your local `CPS-DEMO` clone:

```bash
rm -rf nexa-commerce
tar -xzf nexa-commerce-v3-allengines.tar.gz
cd nexa-commerce/auth-service && go mod tidy && cd ../..
git add -A
git commit -m "Nexa v3: secrets + AI-BOM + SCA surfaces, v2 fixes"
git push
```

Then come back to this chat and say **"pushed"**. I will immediately:

1. Trigger a scan via the Checkmarx MCP — all engines including secret-detection.
2. Poll it to completion.
3. Read SAST / SCA / KICS / secret findings via listFindings, and the AI-BOM
   components via CycloneDX export (AI-BOM is not exposed through listFindings).
4. Match every finding to its chain, flip the workbook's pending rows to
   confirmed with real finding IDs, and flag any severity drift.

---

## What a correct v3 scan should show (so you can sanity-check it)

The v1 scans kept coming back with these tells. After v3 is scanned, they should
change:

| Signal | v1 (wrong) | v3 (expected) |
|---|---|---|
| Engines in result | no secret-detection line | **secret-detection present** |
| Secret findings | 0 | **~6** (AWS key, JWT secret, DB URL, API token) |
| SCA in nexa-commerce/ | none (High CVEs are cps_project labs) | **2 Medium** (Jinja2 3.0.1, requests 2.25.1) |
| Gateway Stored_XSS | Critical at server.js:76 (readFileSync) | **gone** (no sendView/readFileSync in v3) |
| storefront/public/login.php | absent | **present** (CH-101 relocated) |

If the Stored_XSS at `server.js:76` is still there, the push didn't land — the
repo is still on v1.

---

## What's in this bundle

- `nexa-commerce/` — the full v3 codebase (this directory).
- `CHAIN_MAP.md` — every finding mapped to file and expected severity.
- `chains_index_nexa.json` — machine-readable chain catalogue.
- `verify_chains.py` — harness: prints per-chain assembly, fails on any High/Critical.
- `scan.sh` — cx CLI scan helper (Route B alternative if you prefer the CLI).

Repo: https://github.com/cxsmtp/CPS-DEMO  (project id d182f9ec-bb1e-40fb-9b79-12dbb96f7f1c)
