# Nexa Commerce - one-shot database seeder.
FROM node:22-slim

WORKDIR /srv/seed
COPY seed.js ./

# USER is set deliberately - a missing USER instruction rates High and
# every chain in this repository must stay at Medium or below.
USER node

# CH-105 F5 - Healthcheck Instruction Missing (expect: Low)
#
# No HEALTHCHECK is declared. This is a one-shot job container, so the
# omission looks reasonable in review - which is exactly why the
# orchestrator has no signal when the container is doing something other
# than seeding.

CMD ["node", "seed.js"]
