# Nexa Commerce

A small, working e-commerce platform built as a research artefact for the
Chain Potential Score (CPS) framework.

It is a real application — you can run it and buy a ceramic mug — and it is
also a controlled specimen. It reproduces **ten distinct vulnerability chains**
across seven technology stacks, and it is built so that **no application-code or
IaC finding rates High or Critical**. Every constituent of every chain sits at
Medium, Low or Informational: the tiers a severity-ordered backlog defers.

That is the whole point. Each chain, taken finding by finding, is something a
security programme would close as "won't fix this sprint". Composed, each one
reaches the High band on chain risk.

See [`CHAIN_MAP.md`](CHAIN_MAP.md) for the chain-by-chain map of every finding
to its file and expected severity.

## Architecture

| Service | Stack | Port | Chains |
|---|---|---|---|
| `storefront/` | PHP 8.3 | 8080 | CH-101, CH-108 |
| `catalog-service/` | Java 17 / Jakarta Servlet | 8084 | CH-102, CH-103, CH-106 |
| `web-gateway/` | Node 22 | 8081 | CH-104 |
| `auth-service/` | Go 1.22 | 8082 | CH-110 |
| `assistant-service/` | Python 3.12 + OpenAI | 8083 | CH-107 |
| `ops/seed/`, `docker-compose.yml` | Docker | — | CH-105 |
| `deploy/terraform/`, `deploy/k8s/` | Terraform / Kubernetes | — | CH-109 |

Dependency posture is deliberate: the Node, Go and PHP services have **zero**
third-party runtime dependencies, Java uses only the servlet API at `provided`
scope, and Python pins a single current package. This keeps the SCA surface
empty so no transitive CVE can push a finding above Medium.

## Running it

Everything at once:

```bash
docker compose up --build
```

Then:

- Storefront — http://localhost:8080/index.php
- Gateway — http://localhost:8081/
- Auth introspection — `curl localhost:8082/healthz`
- Assistant — `curl 'localhost:8083/api/assistant/ask?q=lamp'`
- Catalog service — http://localhost:8084/catalog/

Individually, without Docker:

```bash
# storefront
php -S localhost:8080 -t storefront/public

# gateway
node web-gateway/src/server.js

# auth service
cd auth-service && go run .

# assistant (works offline; set OPENAI_API_KEY for live model calls)
python3 assistant-service/src/server.py

# catalog service
cd catalog-service && mvn package && deploy target/catalog.war to Tomcat 10
```

## Scanning it

```bash
./scan.sh Nexa-Commerce main
```

The scan runs SAST, SCA, IaC Security, Container Security and API Security.
`node_modules`, `target` and `.git` are excluded.

## Verifying the chains

Export the results and run the verifier:

```bash
cx results show --scan-id <SCAN_ID> --report-format json --output-name nexa-results
PYTHONPATH=/path/to/cps_project python verify_chains.py nexa-results.json
```

It prints, per chain, which required findings fired and at what severity, flags
any severity drift from what was expected, and fails if any High or Critical
finding is present.

## A warning that should not need saying

Every weakness in this repository is intentional. Do not deploy it, do not
lift code from it, and do not point it at anything you care about. It exists
to be scanned.
