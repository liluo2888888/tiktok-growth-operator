package postgres

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/domain"
)

type SessionRepository struct {
	db *sql.DB
}

func NewSessionRepository(db *sql.DB) SessionRepository {
	return SessionRepository{db: db}
}

func EnsureSchema(db *sql.DB) error {
	_, err := db.Exec(`
CREATE TABLE IF NOT EXISTS interview_sessions (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    mission_id TEXT NOT NULL,
    client_token TEXT NOT NULL,
    status TEXT NOT NULL,
    stage TEXT NOT NULL DEFAULT '',
    current_question TEXT NOT NULL DEFAULT '',
    transcript JSONB NOT NULL,
    scores JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interview_sessions_created_at
    ON interview_sessions (created_at DESC);

ALTER TABLE interview_sessions
    ADD COLUMN IF NOT EXISTS stage TEXT NOT NULL DEFAULT '';

ALTER TABLE interview_sessions
    ADD COLUMN IF NOT EXISTS current_question TEXT NOT NULL DEFAULT '';
`)
	if err != nil {
		return err
	}

	if err := ensureStampSchema(db); err != nil {
		return err
	}

	return ensureAnalyticsSchema(db)
}

func (r SessionRepository) Save(ctx context.Context, session domain.Session) error {
	return r.Upsert(ctx, session)
}

func (r SessionRepository) Upsert(ctx context.Context, session domain.Session) error {
	turnsJSON, err := json.Marshal(session.Turns)
	if err != nil {
		return err
	}

	scoresJSON, err := json.Marshal(session.Scores)
	if err != nil {
		return err
	}

	_, err = r.db.ExecContext(
		ctx,
		`INSERT INTO interview_sessions
			(id, role_id, mission_id, client_token, status, stage, current_question, transcript, scores)
		VALUES
			($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb)
		ON CONFLICT (id) DO UPDATE SET
			role_id = EXCLUDED.role_id,
			mission_id = EXCLUDED.mission_id,
			client_token = EXCLUDED.client_token,
			status = EXCLUDED.status,
			stage = EXCLUDED.stage,
			current_question = EXCLUDED.current_question,
			transcript = EXCLUDED.transcript,
			scores = EXCLUDED.scores`,
		session.ID,
		session.RoleID,
		session.MissionID,
		session.ClientToken,
		session.Status,
		session.Stage,
		session.CurrentQuestion,
		string(turnsJSON),
		string(scoresJSON),
	)

	return err
}

func (r SessionRepository) GetByID(ctx context.Context, id string) (domain.Session, error) {
	var session domain.Session
	var turnsJSON []byte
	var scoresJSON []byte

	err := r.db.QueryRowContext(
		ctx,
		`SELECT id, role_id, mission_id, client_token, status, stage, current_question, transcript, scores
		FROM interview_sessions
		WHERE id = $1`,
		id,
	).Scan(
		&session.ID,
		&session.RoleID,
		&session.MissionID,
		&session.ClientToken,
		&session.Status,
		&session.Stage,
		&session.CurrentQuestion,
		&turnsJSON,
		&scoresJSON,
	)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return domain.Session{}, application.ErrSessionNotFound
		}

		return domain.Session{}, err
	}

	if err := json.Unmarshal(turnsJSON, &session.Turns); err != nil {
		return domain.Session{}, err
	}

	if err := json.Unmarshal(scoresJSON, &session.Scores); err != nil {
		return domain.Session{}, err
	}

	return session, nil
}
