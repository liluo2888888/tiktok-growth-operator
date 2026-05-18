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
