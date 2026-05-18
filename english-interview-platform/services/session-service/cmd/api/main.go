package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/httpapi"
	"english-interview/services/session-service/internal/infrastructure/file"
	"english-interview/services/session-service/internal/infrastructure/postgres"

	_ "github.com/lib/pq"
)

func main() {
	sessionRepository, stampRepository, analyticsRepository, cleanup, err := buildRepositories()
	if err != nil {
		log.Fatal(err)
	}
	defer cleanup()

	sessionService := application.NewSessionService(sessionRepository)
	stampService := application.NewStampService(stampRepository, sessionRepository)
	analyticsService := application.NewAnalyticsService(analyticsRepository)

	mux := http.NewServeMux()
	httpapi.RegisterRoutes(mux, sessionService)
	httpapi.RegisterPassportRoutes(mux, stampService)
	httpapi.RegisterAnalyticsRoutes(mux, analyticsService)

	addr := os.Getenv("SESSION_SERVICE_ADDR")
	if addr == "" {
		addr = ":8082"
	}

	log.Printf("session-service listening on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatal(err)
	}
}

func buildRepositories() (
	application.SessionRepository,
	application.StampRepository,
	application.AnalyticsRepository,
	func(),
	error,
) {
	backend := os.Getenv("SESSION_REPOSITORY_BACKEND")
	if backend == "" {
		backend = "postgres"
	}

	switch backend {
	case "postgres":
		databaseURL := os.Getenv("DATABASE_URL")
		if databaseURL == "" {
			databaseURL = "postgres://app:app@localhost:5432/english_interview?sslmode=disable"
		}

		db, err := sql.Open("postgres", databaseURL)
		if err != nil {
			return nil, nil, nil, nil, err
		}

		if err := db.Ping(); err != nil {
			_ = db.Close()
			return nil, nil, nil, nil, err
		}

		if err := postgres.EnsureSchema(db); err != nil {
			_ = db.Close()
			return nil, nil, nil, nil, err
		}

		return postgres.NewSessionRepository(db), postgres.NewStampRepository(db), postgres.NewAnalyticsRepository(db), func() { _ = db.Close() }, nil
	case "file":
		dataDir := filepath.Join("data")
		sessionPath := os.Getenv("SESSION_FILE_PATH")
		if sessionPath == "" {
			sessionPath = filepath.Join(dataDir, "sessions.json")
		}
		stampPath := os.Getenv("PASSPORT_STAMPS_FILE_PATH")
		if stampPath == "" {
			stampPath = filepath.Join(dataDir, "passport_stamps.json")
		}

		analyticsPath := os.Getenv("ANALYTICS_EVENTS_FILE_PATH")
		if analyticsPath == "" {
			analyticsPath = filepath.Join(dataDir, "analytics_events.json")
		}

		return file.NewSessionRepository(sessionPath), file.NewStampRepository(stampPath), file.NewAnalyticsRepository(analyticsPath), func() {}, nil
	default:
		return nil, nil, nil, nil, fmt.Errorf("unsupported session repository backend: %s", backend)
	}
}
