package application

import (
	"context"
	"errors"
	"fmt"
	"time"

	"english-interview/services/session-service/internal/domain"
)

var (
	ErrStampNotFound      = errors.New("stamp not found")
	ErrStampInvalidInput  = errors.New("stamp invalid input")
	ErrSessionHasNoTurns  = errors.New("session has no turns")
)

type StampRepository interface {
	Save(ctx context.Context, stamp domain.PassportStamp) error
	ListByDeviceID(ctx context.Context, deviceID string) ([]domain.PassportStamp, error)
	FindByDeviceAndSession(ctx context.Context, deviceID, sessionID string) (domain.PassportStamp, error)
}

type StampService struct {
	stamps   StampRepository
	sessions SessionRepository
}

func NewStampService(stamps StampRepository, sessions SessionRepository) StampService {
	return StampService{stamps: stamps, sessions: sessions}
}

type IssueStampInput struct {
	SessionID    string
	MissionLabel string
	RoleLabel    string
}

func (s StampService) IssueStamp(ctx context.Context, deviceID string, input IssueStampInput) (domain.PassportStamp, bool, error) {
	if deviceID == "" || input.SessionID == "" {
		return domain.PassportStamp{}, false, ErrStampInvalidInput
	}

	existing, err := s.stamps.FindByDeviceAndSession(ctx, deviceID, input.SessionID)
	if err == nil {
		return existing, false, nil
	}
	if !errors.Is(err, ErrStampNotFound) {
		return domain.PassportStamp{}, false, err
	}

	session, err := s.sessions.GetByID(ctx, input.SessionID)
	if err != nil {
		return domain.PassportStamp{}, false, err
	}
	if len(session.Turns) == 0 {
		return domain.PassportStamp{}, false, ErrSessionHasNoTurns
	}

	missionLabel := input.MissionLabel
	if missionLabel == "" {
		missionLabel = session.MissionID
	}
	roleLabel := input.RoleLabel
	if roleLabel == "" {
		roleLabel = session.RoleID
	}

	stamp := domain.PassportStamp{
		ID:           fmt.Sprintf("stamp_%s", input.SessionID),
		DeviceID:     deviceID,
		SessionID:    input.SessionID,
		MissionID:    session.MissionID,
		MissionLabel: missionLabel,
		RoleID:       session.RoleID,
		RoleLabel:    roleLabel,
		Readiness:    session.Scores.Readiness,
		Scores:       session.Scores,
		EarnedAt:     time.Now().UTC(),
	}

	if err := s.stamps.Save(ctx, stamp); err != nil {
		return domain.PassportStamp{}, false, err
	}

	return stamp, true, nil
}

func (s StampService) ListStamps(ctx context.Context, deviceID string) ([]domain.PassportStamp, error) {
	if deviceID == "" {
		return nil, ErrStampInvalidInput
	}

	return s.stamps.ListByDeviceID(ctx, deviceID)
}
