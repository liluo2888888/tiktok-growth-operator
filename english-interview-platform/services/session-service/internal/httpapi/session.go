package httpapi

import (
	"encoding/json"
	"net/http"
	"strings"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/domain"
)

type CreateSessionRequest struct {
	RoleID    string `json:"roleId"`
	MissionID string `json:"missionId"`
}

type CreateSessionResponse struct {
	SessionID   string `json:"sessionId"`
	ClientToken string `json:"clientToken"`
	Status      string `json:"status"`
	RoleID      string `json:"roleId"`
	MissionID   string `json:"missionId"`
}

type GetSessionResponse struct {
	SessionID       string        `json:"sessionId"`
	Status          string        `json:"status"`
	Stage           string        `json:"stage"`
	CurrentQuestion string        `json:"currentQuestion"`
	RoleID          string        `json:"roleId"`
	MissionID       string        `json:"missionId"`
	Turns           []domain.Turn `json:"turns"`
	Transcript      []string      `json:"transcript"`
	Scores          domain.Scores `json:"scores"`
}

type SubmitTurnRequest struct {
	Answer string `json:"answer"`
}

func RegisterRoutes(mux *http.ServeMux, service application.SessionService) {
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})

	mux.HandleFunc("/v1/sessions", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		var input CreateSessionRequest
		if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
			http.Error(w, `{"error":"invalid_json"}`, http.StatusBadRequest)
			return
		}
		if input.RoleID == "" || input.MissionID == "" {
			http.Error(w, `{"error":"missing_role_or_mission"}`, http.StatusBadRequest)
			return
		}

		session, err := service.CreateSession(r.Context(), input.RoleID, input.MissionID)
		if err != nil {
			http.Error(w, `{"error":"session_create_failed"}`, http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		_ = json.NewEncoder(w).Encode(CreateSessionResponse{
			SessionID:   session.ID,
			ClientToken: session.ClientToken,
			Status:      session.Status,
			RoleID:      session.RoleID,
			MissionID:   session.MissionID,
		})
	})

	mux.HandleFunc("/v1/sessions/", func(w http.ResponseWriter, r *http.Request) {
		id := strings.TrimPrefix(r.URL.Path, "/v1/sessions/")
		if id == "" {
			http.Error(w, `{"error":"missing_session_id"}`, http.StatusBadRequest)
			return
		}

		if strings.HasSuffix(id, "/turns") {
			if r.Method != http.MethodPost {
				w.WriteHeader(http.StatusMethodNotAllowed)
				return
			}

			sessionID := strings.TrimSuffix(id, "/turns")
			var input SubmitTurnRequest
			if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
				http.Error(w, `{"error":"invalid_json"}`, http.StatusBadRequest)
				return
			}
			if strings.TrimSpace(input.Answer) == "" {
				http.Error(w, `{"error":"missing_answer"}`, http.StatusBadRequest)
				return
			}

			session, err := service.SubmitAnswer(r.Context(), sessionID, input.Answer)
			if err != nil {
				if err == application.ErrSessionNotFound {
					http.Error(w, `{"error":"session_not_found"}`, http.StatusNotFound)
					return
				}

				http.Error(w, `{"error":"session_update_failed"}`, http.StatusInternalServerError)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(GetSessionResponse{
				SessionID:       session.ID,
				Status:          session.Status,
				Stage:           session.Stage,
				CurrentQuestion: session.CurrentQuestion,
				RoleID:          session.RoleID,
				MissionID:       session.MissionID,
				Turns:           session.Turns,
				Transcript:      transcriptFromTurns(session.Turns),
				Scores:          session.Scores,
			})
			return
		}

		if r.Method != http.MethodGet {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		session, err := service.GetSession(r.Context(), id)
		if err != nil {
			if err == application.ErrSessionNotFound {
				http.Error(w, `{"error":"session_not_found"}`, http.StatusNotFound)
				return
			}

			http.Error(w, `{"error":"session_lookup_failed"}`, http.StatusInternalServerError)
			return
		}

		if session.ID == "" {
			http.Error(w, `{"error":"session_not_found"}`, http.StatusNotFound)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(GetSessionResponse{
			SessionID:       session.ID,
			Status:          session.Status,
			Stage:           session.Stage,
			CurrentQuestion: session.CurrentQuestion,
			RoleID:          session.RoleID,
			MissionID:       session.MissionID,
			Turns:           session.Turns,
			Transcript:      transcriptFromTurns(session.Turns),
			Scores:          session.Scores,
		})
	})
}

func transcriptFromTurns(turns []domain.Turn) []string {
	lines := make([]string, 0, len(turns)*2)
	for _, turn := range turns {
		lines = append(lines, turn.Question)
		lines = append(lines, turn.Answer)
	}

	return lines
}
