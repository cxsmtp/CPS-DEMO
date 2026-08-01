# Nexa Commerce - edge gateway (Node).
FROM node:22-slim

WORKDIR /srv/gateway
COPY package.json ./
COPY src ./src

# USER is set deliberately - a missing USER instruction rates High.
USER node

EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=3s CMD node -e "require('http').get('http://127.0.0.1:8081/healthz',r=>process.exit(r.statusCode===200?0:1))"
CMD ["node", "src/server.js"]
