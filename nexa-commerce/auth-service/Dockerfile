# Nexa Commerce - auth service (Go).
FROM golang:1.22-alpine AS build
WORKDIR /build
COPY go.mod ./
COPY main.go ./
RUN CGO_ENABLED=0 go build -o /out/auth-service .

FROM alpine:3.20
WORKDIR /srv/auth
COPY --from=build /out/auth-service /usr/local/bin/auth-service
COPY public ./public
RUN adduser -D -u 10001 nexa
USER nexa
EXPOSE 8082
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8082/healthz || exit 1
CMD ["auth-service"]
