package file

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"sync"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/domain"
)

type SessionRepository struct {
	path string
	mu   sync.Mutex
}

func NewSessionRepository(path string) SessionRepository {
	return SessionRepository{path: path}
}

func (r SessionRepository) Save(_ context.Context, session domain.Session) error {
	return r.Upsert(context.Background(), session)
}

func (r SessionRepository) Upsert(_ context.Context, session domain.Session) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	store, err := r.readAll()
	if err != nil {
		return err
	}

	store[session.ID] = session
	return r.writeAll(store)
}

func (r SessionRepository) GetByID(_ context.Context, id string) (domain.Session, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	store, err := r.readAll()
	if err != nil {
		return domain.Session{}, err
	}

	session, ok := store[id]
	if !ok {
		return domain.Session{}, application.ErrSessionNotFound
	}

	return session, nil
}

func (r SessionRepository) readAll() (map[string]domain.Session, error) {
	if err := os.MkdirAll(filepath.Dir(r.path), 0o755); err != nil {
		return nil, err
	}

	if _, err := os.Stat(r.path); os.IsNotExist(err) {
		return map[string]domain.Session{}, nil
	}

	payload, err := os.ReadFile(r.path)
	if err != nil {
		return nil, err
	}

	if len(payload) == 0 {
		return map[string]domain.Session{}, nil
	}

	var store map[string]domain.Session
	if err := json.Unmarshal(payload, &store); err != nil {
		return nil, err
	}

	if store == nil {
		store = map[string]domain.Session{}
	}

	return store, nil
}

func (r SessionRepository) writeAll(store map[string]domain.Session) error {
	payload, err := json.MarshalIndent(store, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(r.path, payload, 0o644)
}
