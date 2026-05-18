package application

import (
	"context"
	"errors"

	"english-interview/services/session-service/internal/domain"
)

var ErrSessionNotFound = errors.New("session_not_found")

type SessionRepository interface {
	Save(context.Context, domain.Session) error
	Upsert(context.Context, domain.Session) error
	GetByID(context.Context, string) (domain.Session, error)
}

type SessionService struct {
	repository SessionRepository
}

func NewSessionService(repository SessionRepository) SessionService {
	return SessionService{repository: repository}
}

func (s SessionService) CreateSession(ctx context.Context, roleID string, missionID string) (domain.Session, error) {
	session := domain.NewSession(roleID, missionID)
	if err := s.repository.Save(ctx, session); err != nil {
		return domain.Session{}, err
	}

	return session, nil
}

func (s SessionService) GetSession(ctx context.Context, id string) (domain.Session, error) {
	return s.repository.GetByID(ctx, id)
}

func (s SessionService) SubmitAnswer(ctx context.Context, id string, answer string) (domain.Session, error) {
	session, err := s.repository.GetByID(ctx, id)
	if err != nil {
		return domain.Session{}, err
	}

	session.AddTurn(answer)
	if err := s.repository.Upsert(ctx, session); err != nil {
		return domain.Session{}, err
	}

	return session, nil
}
