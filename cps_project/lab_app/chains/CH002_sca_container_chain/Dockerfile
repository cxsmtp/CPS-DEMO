# =============================================================================
# CH-002 LAB DOCKERFILE — DELIBERATELY VULNERABLE
# =============================================================================
# This Dockerfile contains intentional misconfigurations and uses a pinned
# base image whose package CVE landscape is well-documented and skews Low.
# It is for Checkmarx Container Security validation only and must never be
# pushed to a production registry or used to build production images.
#
# Pinned base: python:3.11.4-slim (NOT python:3.11-slim, which is a moving
# tag whose CVE list shifts on each rebuild). This pin keeps F4
# reproducible across rescans.
#
# Each misconfiguration carries a LAB-DOCKER-VULN-CHA2-N marker.
# =============================================================================

# F4 (base-image): pinned older slim Python — Debian package CVEs from
# 2023-era are predominantly Low-rated info-disclosure / DoS class.
FROM python:3.11.4-slim

# LAB-DOCKER-VULN-CHA2-1 (KICS Low: Use of Add Instead of Copy)
# ADD has implicit URL-fetch and tar-extraction behavior that COPY does
# not. KICS flags ADD as Low when used for plain file copying.
ADD requirements.txt /app/requirements.txt

WORKDIR /app

# Install dependencies. We don't use --no-install-recommends, which is a
# documented Dockerfile hardening best practice that Checkmarx may flag.
RUN apt-get update && \
    apt-get install -y curl && \
    pip install --no-cache-dir -r /app/requirements.txt

# LAB-DOCKER-VULN-CHA2-2 (KICS Low: Missing User Instruction)
# Container runs as root because no USER directive is set.
# KICS flags this at Low or Medium depending on rule configuration.
# (No "USER appuser" line here — that's the deliberate omission.)

# LAB-DOCKER-VULN-CHA2-3 (KICS Low: Healthcheck Instruction Missing)
# No HEALTHCHECK directive — orchestrator can't tell if the container
# is responsive. KICS flags this at Low.

# LAB-DOCKER-VULN-CHA2-4 (KICS Low: APT Get Install Lists Were Not Deleted)
# /var/lib/apt/lists/* was not cleaned after apt-get install — this
# unnecessarily extends the image and retains package metadata that
# could leak version info on container introspection.
# (No "rm -rf /var/lib/apt/lists/*" — that's the deliberate omission.)

# LAB-DOCKER-VULN-CHA2-5 (KICS Low: APT Get Install Pin Version)
# apt-get install lacks --no-install-recommends and pins.

ADD src /app/src

EXPOSE 5060

CMD ["python", "-m", "app.main"]
