package httpserver

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

type createSessionRequest struct {
	RoleID    string `json:"roleId"`
	MissionID string `json:"missionId"`
}

type createSessionResponse struct {
	SessionID   string `json:"sessionId"`
	ClientToken string `json:"clientToken"`
	Status      string `json:"status"`
	RoleID      string `json:"roleId"`
	MissionID   string `json:"missionId"`
}

type getSessionResponse struct {
	SessionID  string   `json:"sessionId"`
	Status     string   `json:"status"`
	RoleID     string   `json:"roleId"`
	MissionID  string   `json:"missionId"`
	Transcript []string `json:"transcript"`
	Scores     struct {
		Clarity    int `json:"clarity"`
		Structure  int `json:"structure"`
		Confidence int `json:"confidence"`
		Relevance  int `json:"relevance"`
		Readiness  int `json:"readiness"`
	} `json:"scores"`
}

type submitTurnRequest struct {
	Answer string `json:"answer"`
}

func New() http.Handler {
	mux := http.NewServeMux()
	client := &http.Client{Timeout: 5 * time.Second}
	sessionServiceBaseURL := os.Getenv("SESSION_SERVICE_BASE_URL")
	if sessionServiceBaseURL == "" {
		sessionServiceBaseURL = "http://localhost:8082"
	}

	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	mux.HandleFunc("/v1/mobile/session/bootstrap", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		var input createSessionRequest
		if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
			http.Error(w, `{"error":"invalid_json"}`, http.StatusBadRequest)
			return
		}

		body, err := json.Marshal(input)
		if err != nil {
			http.Error(w, `{"error":"encode_failed"}`, http.StatusInternalServerError)
			return
		}

		req, err := http.NewRequest(http.MethodPost, sessionServiceBaseURL+"/v1/sessions", bytes.NewReader(body))
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}
		req.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(req)
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(resp.StatusCode)
		_, _ = io.Copy(w, resp.Body)
	})
	mux.HandleFunc("/v1/mobile/sessions/", func(w http.ResponseWriter, r *http.Request) {
		id := strings.TrimPrefix(r.URL.Path, "/v1/mobile/sessions/")
		if strings.HasSuffix(id, "/turns") {
			if r.Method != http.MethodPost {
				w.WriteHeader(http.StatusMethodNotAllowed)
				return
			}

			var input submitTurnRequest
			if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
				http.Error(w, `{"error":"invalid_json"}`, http.StatusBadRequest)
				return
			}

			body, err := json.Marshal(input)
			if err != nil {
				http.Error(w, `{"error":"encode_failed"}`, http.StatusInternalServerError)
				return
			}

			req, err := http.NewRequest(http.MethodPost, sessionServiceBaseURL+"/v1/sessions/"+id, bytes.NewReader(body))
			if err != nil {
				http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
				return
			}
			req.Header.Set("Content-Type", "application/json")

			resp, err := client.Do(req)
			if err != nil {
				http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
				return
			}
			defer resp.Body.Close()

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(resp.StatusCode)
			_, _ = io.Copy(w, resp.Body)
			return
		}

		if r.Method != http.MethodGet {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		req, err := http.NewRequest(http.MethodGet, sessionServiceBaseURL+"/v1/sessions/"+id, nil)
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}

		resp, err := client.Do(req)
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(resp.StatusCode)
		_, _ = io.Copy(w, resp.Body)
	})
	mux.HandleFunc("/v1/mobile/passport/stamps", func(w http.ResponseWriter, r *http.Request) {
		deviceID := r.Header.Get("X-Device-Id")
		if deviceID == "" {
			http.Error(w, `{"error":"missing_device_id"}`, http.StatusBadRequest)
			return
		}

		url := sessionServiceBaseURL + "/v1/passport/stamps"
		var req *http.Request
		var err error

		switch r.Method {
		case http.MethodGet:
			req, err = http.NewRequest(http.MethodGet, url, nil)
		case http.MethodPost:
			body, readErr := io.ReadAll(r.Body)
			if readErr != nil {
				http.Error(w, `{"error":"invalid_body"}`, http.StatusBadRequest)
				return
			}
			req, err = http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("X-Device-Id", deviceID)

		resp, err := client.Do(req)
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(resp.StatusCode)
		_, _ = io.Copy(w, resp.Body)
	})

	mux.HandleFunc("/v1/mobile/analytics/events", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		deviceID := r.Header.Get("X-Device-Id")
		if deviceID == "" {
			http.Error(w, `{"error":"missing_device_id"}`, http.StatusBadRequest)
			return
		}

		body, readErr := io.ReadAll(r.Body)
		if readErr != nil {
			http.Error(w, `{"error":"invalid_body"}`, http.StatusBadRequest)
			return
		}

		req, err := http.NewRequest(http.MethodPost, sessionServiceBaseURL+"/v1/analytics/events", bytes.NewReader(body))
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("X-Device-Id", deviceID)

		resp, err := client.Do(req)
		if err != nil {
			http.Error(w, `{"error":"session_service_unavailable"}`, http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(resp.StatusCode)
		_, _ = io.Copy(w, resp.Body)
	})

	mux.HandleFunc("/v1/mobile/interview/options", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"roles": []map[string]string{
				{"id": "frontend", "label": "Frontend Engineer"},
				{"id": "product", "label": "Product Manager"},
				{"id": "sales", "label": "Global Sales"},
			},
			"missions": []map[string]string{
				{"id": "self_intro", "label": "Self Introduction"},
				{"id": "behavioral", "label": "Behavioral Interview"},
				{"id": "case_round", "label": "Case / Problem Solving"},
			},
		})
	})

	return mux
}
