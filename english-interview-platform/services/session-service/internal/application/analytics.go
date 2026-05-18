package application

import (
	"context"
	"errors"
	"time"

	"english-interview/services/session-service/internal/domain"
)

var (
	ErrAnalyticsInvalidInput = errors.New("invalid analytics input")
	ErrAnalyticsEmptyBatch   = errors.New("empty analytics batch")
)

type AnalyticsEventInput struct {
	Event      string
	Properties map[string]any
	ClientAt   time.Time
}

type AnalyticsRepository interface {
	Append(ctx context.Context, events []domain.AnalyticsEvent) error
}

type AnalyticsService struct {
	repo AnalyticsRepository
}

func NewAnalyticsService(repo AnalyticsRepository) AnalyticsService {
	return AnalyticsService{repo: repo}
}

func (s AnalyticsService) Ingest(
	ctx context.Context,
	deviceID string,
	inputs []AnalyticsEventInput,
) (int, error) {
	if deviceID == "" {
		return 0, ErrAnalyticsInvalidInput
	}
	if len(inputs) == 0 {
		return 0, ErrAnalyticsEmptyBatch
	}

	now := time.Now().UTC()
	events := make([]domain.AnalyticsEvent, 0, len(inputs))

	for _, input := range inputs {
		if input.Event == "" {
			return 0, ErrAnalyticsInvalidInput
		}

		clientAt := input.ClientAt
		if clientAt.IsZero() {
			clientAt = now
		}

		properties := input.Properties
		if properties == nil {
			properties = map[string]any{}
		}

		events = append(events, domain.AnalyticsEvent{
			ID:         domain.NewAnalyticsEventID(),
			DeviceID:   deviceID,
			Event:      input.Event,
			Properties: properties,
			ClientAt:   clientAt.UTC(),
			RecordedAt: now,
		})
	}

	if err := s.repo.Append(ctx, events); err != nil {
		return 0, err
	}

	return len(events), nil
}
