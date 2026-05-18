package main

import (
	"log"
	"net/http"
	"os"

	"english-interview/services/api-gateway/internal/httpserver"
)

func main() {
	server := httpserver.New()

	addr := os.Getenv("API_GATEWAY_ADDR")
	if addr == "" {
		addr = ":8080"
	}

	log.Printf("api-gateway listening on %s", addr)
	if err := http.ListenAndServe(addr, server); err != nil {
		log.Fatal(err)
	}
}
