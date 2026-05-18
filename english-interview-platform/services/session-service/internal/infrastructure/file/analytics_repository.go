package file

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"sync"
	"time"

	"english-interview/services/session-service/internal/domain"
)

type analyticsRecord struct {
	ID         string         `json:"id"`
	DeviceID   string         `json:"deviceId"`
	Event      string         `json:"event"`
	Properties map[string]any `json:"properties"`
	ClientAt   time.Time      `json:"clientAt"`
	RecordedAt time.Time      `json:"recordedAt"`
}

type AnalyticsRepository struct {
	path string
	mu   sync.Mutex
}

func NewAnalyticsRepository(path string) AnalyticsRepository {
	return AnalyticsRepository{path: path}
}

func (r AnalyticsRepository) Append(_ context.Context, events []domain.AnalyticsEvent) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	records, err := r.readAll()
	if err != nil {
		return err
	}

	for _, event := range events {
		records = append(records, analyticsRecord{
			ID:         event.ID,
			DeviceID:   event.DeviceID,
			Event:      event.Event,
			Properties: event.Properties,
			ClientAt:   event.ClientAt,
			RecordedAt: event.RecordedAt,
		})
	}

	return r.writeAll(records)
}

func (r AnalyticsRepository) readAll() ([]analyticsRecord, error) {
	if err := os.MkdirAll(filepath.Dir(r.path), 0o755); err != nil {
		return nil, err
	}

	raw, err := os.ReadFile(r.path)
	if err != nil {
		if os.IsNotExist(err) {
			return []analyticsRecord{}, nil
		}
		return nil, err
	}

	if len(raw) == 0 {
		return []analyticsRecord{}, nil
	}

	var records []analyticsRecord
	if err := json.Unmarshal(raw, &records); err != nil {
		return nil, err
	}

	return records, nil
}

func (r AnalyticsRepository) writeAll(records []analyticsRecord) error {
	if err := os.MkdirAll(filepath.Dir(r.path), 0o755); err != nil {
		return err
	}

	raw, err := json.MarshalIndent(records, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(r.path, raw, 0o644)
}
