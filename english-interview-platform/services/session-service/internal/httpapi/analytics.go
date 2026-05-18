package httpapi

import (
	"encoding/json"
	"net/http"
	"time"

	"english-interview/services/session-service/internal/application"
)

type ingestAnalyticsEventRequest struct {
	Event      string         `json:"event"`
	Properties map[string]any `json:"properties"`
	At         string         `json:"at"`
}

type ingestAnalyticsRequest struct {
	Events []ingestAnalyticsEventRequest `json:"events"`
}

func RegisterAnalyticsRoutes(mux *http.ServeMux, service application.AnalyticsService) {
	mux.HandleFunc("/v1/analytics/events", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		deviceID := r.Header.Get("X-Device-Id")
		if deviceID == "" {
			http.Error(w, `{"error":"missing_device_id"}`, http.StatusBadRequest)
			return
		}

		var input ingestAnalyticsRequest
		if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
			http.Error(w, `{"error":"invalid_json"}`, http.StatusBadRequest)
			return
		}

		events := make([]application.AnalyticsEventInput, 0, len(input.Events))
		for _, item := range input.Events {
			clientAt := time.Now().UTC()
			if item.At != "" {
				parsed, err := time.Parse(time.RFC3339, item.At)
				if err == nil {
					clientAt = parsed.UTC()
				}
			}

			events = append(events, application.AnalyticsEventInput{
				Event:      item.Event,
				Properties: item.Properties,
				ClientAt:   clientAt,
			})
		}

		accepted, err := service.Ingest(r.Context(), deviceID, events)
		if err != nil {
			switch err {
			case application.ErrAnalyticsInvalidInput, application.ErrAnalyticsEmptyBatch:
				http.Error(w, `{"error":"invalid_analytics_batch"}`, http.StatusBadRequest)
			default:
				http.Error(w, `{"error":"analytics_ingest_failed"}`, http.StatusInternalServerError)
			}
			return
		}

		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"accepted": accepted,
		})
	})
}
