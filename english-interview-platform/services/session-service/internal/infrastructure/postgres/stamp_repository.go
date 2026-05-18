package postgres

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"time"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/domain"
)

type StampRepository struct {
	db *sql.DB
}

func NewStampRepository(db *sql.DB) StampRepository {
	return StampRepository{db: db}
}

func ensureStampSchema(db *sql.DB) error {
	_, err := db.Exec(`
CREATE TABLE IF NOT EXISTS passport_stamps (
    id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    mission_id TEXT NOT NULL,
    mission_label TEXT NOT NULL,
    role_id TEXT NOT NULL,
    role_label TEXT NOT NULL,
    readiness INT NOT NULL,
    scores JSONB NOT NULL,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (device_id, session_id)
);

CREATE INDEX IF NOT EXISTS idx_passport_stamps_device_earned
    ON passport_stamps (device_id, earned_at DESC);
`)
	return err
}

func (r StampRepository) Save(ctx context.Context, stamp domain.PassportStamp) error {
	scoresJSON, err := json.Marshal(stamp.Scores)
	if err != nil {
		return err
	}

	_, err = r.db.ExecContext(ctx, `
INSERT INTO passport_stamps (
    id, device_id, session_id, mission_id, mission_label,
    role_id, role_label, readiness, scores, earned_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
ON CONFLICT (device_id, session_id) DO UPDATE SET
    mission_label = EXCLUDED.mission_label,
    role_label = EXCLUDED.role_label,
    readiness = EXCLUDED.readiness,
    scores = EXCLUDED.scores,
    earned_at = EXCLUDED.earned_at
`, stamp.ID, stamp.DeviceID, stamp.SessionID, stamp.MissionID, stamp.MissionLabel,
		stamp.RoleID, stamp.RoleLabel, stamp.Readiness, scoresJSON, stamp.EarnedAt)

	return err
}

func (r StampRepository) ListByDeviceID(ctx context.Context, deviceID string) ([]domain.PassportStamp, error) {
	rows, err := r.db.QueryContext(ctx, `
SELECT id, device_id, session_id, mission_id, mission_label,
       role_id, role_label, readiness, scores, earned_at
FROM passport_stamps
WHERE device_id = $1
ORDER BY earned_at DESC
`, deviceID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanStampRows(rows)
}

func (r StampRepository) FindByDeviceAndSession(ctx context.Context, deviceID, sessionID string) (domain.PassportStamp, error) {
	row := r.db.QueryRowContext(ctx, `
SELECT id, device_id, session_id, mission_id, mission_label,
       role_id, role_label, readiness, scores, earned_at
FROM passport_stamps
WHERE device_id = $1 AND session_id = $2
`, deviceID, sessionID)

	stamp, err := scanStampRow(row)
	if errors.Is(err, sql.ErrNoRows) {
		return domain.PassportStamp{}, application.ErrStampNotFound
	}

	return stamp, err
}

func scanStampRows(rows *sql.Rows) ([]domain.PassportStamp, error) {
	stamps := make([]domain.PassportStamp, 0)
	for rows.Next() {
		stamp, err := scanStampFromRows(rows)
		if err != nil {
			return nil, err
		}
		stamps = append(stamps, stamp)
	}

	return stamps, rows.Err()
}

func scanStampRow(row *sql.Row) (domain.PassportStamp, error) {
	var (
		stamp      domain.PassportStamp
		scoresJSON []byte
		earnedAt   time.Time
	)

	err := row.Scan(
		&stamp.ID,
		&stamp.DeviceID,
		&stamp.SessionID,
		&stamp.MissionID,
		&stamp.MissionLabel,
		&stamp.RoleID,
		&stamp.RoleLabel,
		&stamp.Readiness,
		&scoresJSON,
		&earnedAt,
	)
	if err != nil {
		return domain.PassportStamp{}, err
	}

	if err := json.Unmarshal(scoresJSON, &stamp.Scores); err != nil {
		return domain.PassportStamp{}, err
	}
	stamp.EarnedAt = earnedAt

	return stamp, nil
}

func scanStampFromRows(rows *sql.Rows) (domain.PassportStamp, error) {
	var (
		stamp      domain.PassportStamp
		scoresJSON []byte
		earnedAt   time.Time
	)

	err := rows.Scan(
		&stamp.ID,
		&stamp.DeviceID,
		&stamp.SessionID,
		&stamp.MissionID,
		&stamp.MissionLabel,
		&stamp.RoleID,
		&stamp.RoleLabel,
		&stamp.Readiness,
		&scoresJSON,
		&earnedAt,
	)
	if err != nil {
		return domain.PassportStamp{}, err
	}

	if err := json.Unmarshal(scoresJSON, &stamp.Scores); err != nil {
		return domain.PassportStamp{}, err
	}
	stamp.EarnedAt = earnedAt

	return stamp, nil
}
