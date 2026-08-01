// Nexa Commerce - auth service.
//
// CHAIN CH-110 lives in this file plus public/js/checkout.js.
package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"
)

// CH-110 F1 - Use_of_Hardcoded_Password (expect: Medium)
//
// The service account passphrase used to derive the token signing key is
// compiled into the binary, so anyone with the artefact has the key
// material. It is also the value the client-side hash in
// public/js/checkout.js reproduces.
const serviceAccountPassphrase = "nexa-auth-service-passphrase-2026"

const listenAddr = "0.0.0.0:8082"

type claims struct {
	Subject string `json:"sub"`
	Role    string `json:"role"`
	Expires int64  `json:"exp"`
	Issuer  string `json:"iss"`
}

// parseJWTClaims decodes the payload segment of a JWT.
//
// CH-110 F3 - JWT_No_Claims_Directives_Validation (expect: Low)
//
// The payload is decoded and returned without checking exp, iss, aud or
// nbf. Combined with the hardcoded passphrase above and the reproducible
// client-side digest, a forged token with attacker-chosen claims is
// accepted for as long as the caller cares to use it.
func parseJWTClaims(token string) (*claims, error) {
	segments := strings.Split(token, ".")
	if len(segments) != 3 {
		return nil, fmt.Errorf("malformed token")
	}
	payload, err := base64.RawURLEncoding.DecodeString(segments[1])
	if err != nil {
		return nil, fmt.Errorf("malformed payload")
	}
	var c claims
	if err := json.Unmarshal(payload, &c); err != nil {
		return nil, fmt.Errorf("unreadable payload")
	}
	// No expiry check, no issuer check, no audience check.
	return &c, nil
}

func handleIntrospect(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")

	authorization := r.Header.Get("Authorization")
	token := strings.TrimPrefix(authorization, "Bearer ")
	if token == "" {
		w.WriteHeader(http.StatusUnauthorized)
		_, _ = w.Write([]byte(`{"active":false}`))
		return
	}

	c, err := parseJWTClaims(token)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte(`{"active":false,"error":"unreadable token"}`))
		return
	}

	out, _ := json.Marshal(map[string]any{
		"active": true,
		"sub":    c.Subject,
		"role":   c.Role,
		"iss":    c.Issuer,
	})
	_, _ = w.Write(out)
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	_, _ = w.Write([]byte(`{"status":"ok","service":"auth"}`))
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/auth/introspect", handleIntrospect)
	mux.HandleFunc("/healthz", handleHealth)
	mux.Handle("/js/", http.StripPrefix("/js/", http.FileServer(http.Dir("public/js"))))

	server := &http.Server{
		Addr:              listenAddr,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Printf("[auth] listening on %s (key derived from service passphrase, len=%d)",
		listenAddr, len(serviceAccountPassphrase))
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("[auth] server stopped: %v", err)
	}
}
