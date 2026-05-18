package postgres

import (
	"context"
	"database/sql"
	"encoding/json"

	"english-interview/services/session-service/internal/domain"
)

type AnalyticsRepository struct {
	db *sql.DB
}

func NewAnalyticsRepository(db *sql.DB) AnalyticsRepository {
	return AnalyticsRepository{db: db}
}

func ensureAnalyticsSchema(db *sql.DB) error {
	_, err := db.Exec(`
CREATE TABLE IF NOT EXISTS analytics_events (
    id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    event_name TEXT NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    client_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_device_recorded
    ON analytics_events (device_id, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_analytics_events_event_name
    ON analytics_events (event_name, recorded_at DESC);
`)
	return err
}

func (r AnalyticsRepository) Append(ctx context.Context, events []domain.AnalyticsEvent) error {
	for _, event := range events {
		propertiesJSON, err := json.Marshal(event.Properties)
		if err != nil {
			return err
		}

		_, err = r.db.ExecContext(ctx, `
INSERT INTO analytics_events (id, device_id, event_name, properties, client_at, recorded_at)
VALUES ($1, $2, $3, $4::jsonb, $5, $6)
ON CONFLICT (id) DO NOTHING`,
			event.ID,
			event.DeviceID,
			event.Event,
			propertiesJSON,
			event.ClientAt,
			event.RecordedAt,
		)
		if err != nil {
			return err
		}
	}

	return nil
}
