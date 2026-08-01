# =============================================================================
# CH-002 LAB DOCKERFILE (Node) — DELIBERATELY VULNERABLE
# =============================================================================
# Pinned base: node:20-slim. The Dockerfile rule findings (KICS Low) are
# the load-bearing Container Security chain participants. The base-image
# package CVE is a bonus — it may produce zero findings on a current
# slim image, in which case the chain still assembles from the Dockerfile
# rules alone.
#
# Each misconfiguration carries a LAB-DOCKER-VULN-CHA2-NODE-N marker.
# =============================================================================

FROM node:20-slim

# LAB-DOCKER-VULN-CHA2-NODE-1 (KICS Low: Add Instead of Copy)
# ADD has implicit URL-fetch and tar-extraction behavior that COPY does
# not. KICS flags ADD as Low when used for plain file copying.
ADD package.json /app/package.json
ADD package-lock.json /app/package-lock.json

WORKDIR /app

# LAB-DOCKER-VULN-CHA2-NODE-2 (KICS Low: APT Get Install Pin Version Not Defined)
# Installing curl without --no-install-recommends and without pinning.
RUN apt-get update && \
    apt-get install -y curl && \
    npm install --omit=dev

# LAB-DOCKER-VULN-CHA2-NODE-3 (KICS Low: Missing User Instruction)
# Container runs as root because no USER directive is set.

# LAB-DOCKER-VULN-CHA2-NODE-4 (KICS Low: Healthcheck Instruction Missing)
# No HEALTHCHECK directive — orchestrator can't tell if the container
# is responsive.

# LAB-DOCKER-VULN-CHA2-NODE-5 (KICS Low: APT Get Install Lists Were Not Deleted)
# /var/lib/apt/lists/* not cleaned after apt-get install.

ADD src /app/src

EXPOSE 5070

CMD ["node", "src/app.js"]
