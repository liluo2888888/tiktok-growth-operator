package httpapi

import (
	"encoding/json"
	"net/http"
	"time"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/domain"
)

type issueStampRequest struct {
	SessionID    string `json:"sessionId"`
	MissionLabel string `json:"missionLabel"`
	RoleLabel    string `json:"roleLabel"`
}

type stampResponse struct {
	ID           string `json:"id"`
	DeviceID     string `json:"deviceId"`
	SessionID    string `json:"sessionId"`
	MissionID    string `json:"missionId"`
	MissionLabel string `json:"missionLabel"`
	RoleID       string `json:"roleId"`
	RoleLabel    string `json:"roleLabel"`
	Readiness    int    `json:"readiness"`
	Scores       any    `json:"scores"`
	EarnedAt     string `json:"earnedAt"`
	IsNew        bool   `json:"isNew"`
}

func RegisterPassportRoutes(mux *http.ServeMux, service application.StampService) {
	mux.HandleFunc("/v1/passport/stamps", func(w http.ResponseWriter, r *http.Request) {
		deviceID := r.Header.Get("X-Device-Id")
		if deviceID == "" {
			http.Error(w, `{"error":"missing_device_id"}`, http.StatusBadRequest)
			return
		}

		switch r.Method {
		case http.MethodGet:
			stamps, err := service.ListStamps(r.Context(), deviceID)
			if err != nil {
				http.Error(w, `{"error":"stamp_list_failed"}`, http.StatusInternalServerError)
				return
			}

			payload := make([]stampResponse, 0, len(stamps))
			for _, stamp := range stamps {
				payload = append(payload, toStampResponse(stamp, false))
			}

			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{"stamps": payload})
		case http.MethodPost:
			var input issueStampRequest
			if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
				http.Error(w, `{"error":"invalid_json"}`, http.StatusBadRequest)
				return
			}
			if input.SessionID == "" {
				http.Error(w, `{"error":"missing_session_id"}`, http.StatusBadRequest)
				return
			}

			stamp, isNew, err := service.IssueStamp(r.Context(), deviceID, application.IssueStampInput{
				SessionID:    input.SessionID,
				MissionLabel: input.MissionLabel,
				RoleLabel:    input.RoleLabel,
			})
			if err != nil {
				switch err {
				case application.ErrSessionNotFound:
					http.Error(w, `{"error":"session_not_found"}`, http.StatusNotFound)
				case application.ErrSessionHasNoTurns:
					http.Error(w, `{"error":"session_has_no_turns"}`, http.StatusBadRequest)
				case application.ErrStampInvalidInput:
					http.Error(w, `{"error":"invalid_stamp_input"}`, http.StatusBadRequest)
				default:
					http.Error(w, `{"error":"stamp_issue_failed"}`, http.StatusInternalServerError)
				}
				return
			}

			w.Header().Set("Content-Type", "application/json")
			if isNew {
				w.WriteHeader(http.StatusCreated)
			}
			_ = json.NewEncoder(w).Encode(toStampResponse(stamp, isNew))
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	})
}

func toStampResponse(stamp domain.PassportStamp, isNew bool) stampResponse {
	return stampResponse{
		ID:           stamp.ID,
		DeviceID:     stamp.DeviceID,
		SessionID:    stamp.SessionID,
		MissionID:    stamp.MissionID,
		MissionLabel: stamp.MissionLabel,
		RoleID:       stamp.RoleID,
		RoleLabel:    stamp.RoleLabel,
		Readiness:    stamp.Readiness,
		Scores:       stamp.Scores,
		EarnedAt:     stamp.EarnedAt.Format(time.RFC3339),
		IsNew:        isNew,
	}
}
