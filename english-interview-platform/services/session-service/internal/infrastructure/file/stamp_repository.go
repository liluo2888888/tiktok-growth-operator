package file

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"sync"
	"time"

	"english-interview/services/session-service/internal/application"
	"english-interview/services/session-service/internal/domain"
)

type stampRecord struct {
	ID           string        `json:"id"`
	DeviceID     string        `json:"deviceId"`
	SessionID    string        `json:"sessionId"`
	MissionID    string        `json:"missionId"`
	MissionLabel string        `json:"missionLabel"`
	RoleID       string        `json:"roleId"`
	RoleLabel    string        `json:"roleLabel"`
	Readiness    int           `json:"readiness"`
	Scores       domain.Scores `json:"scores"`
	EarnedAt     time.Time     `json:"earnedAt"`
}

type StampRepository struct {
	path string
	mu   sync.Mutex
}

func NewStampRepository(path string) StampRepository {
	return StampRepository{path: path}
}

func (r StampRepository) Save(_ context.Context, stamp domain.PassportStamp) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	records, err := r.readAll()
	if err != nil {
		return err
	}

	for index, record := range records {
		if record.DeviceID == stamp.DeviceID && record.SessionID == stamp.SessionID {
			records[index] = toRecord(stamp)
			return r.writeAll(records)
		}
	}

	records = append(records, toRecord(stamp))
	return r.writeAll(records)
}

func (r StampRepository) ListByDeviceID(_ context.Context, deviceID string) ([]domain.PassportStamp, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	records, err := r.readAll()
	if err != nil {
		return nil, err
	}

	stamps := make([]domain.PassportStamp, 0)
	for _, record := range records {
		if record.DeviceID == deviceID {
			stamps = append(stamps, fromRecord(record))
		}
	}

	sort.Slice(stamps, func(i, j int) bool {
		return stamps[i].EarnedAt.After(stamps[j].EarnedAt)
	})

	return stamps, nil
}

func (r StampRepository) FindByDeviceAndSession(_ context.Context, deviceID, sessionID string) (domain.PassportStamp, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	records, err := r.readAll()
	if err != nil {
		return domain.PassportStamp{}, err
	}

	for _, record := range records {
		if record.DeviceID == deviceID && record.SessionID == sessionID {
			return fromRecord(record), nil
		}
	}

	return domain.PassportStamp{}, application.ErrStampNotFound
}

func (r StampRepository) readAll() ([]stampRecord, error) {
	if err := os.MkdirAll(filepath.Dir(r.path), 0o755); err != nil {
		return nil, err
	}

	if _, err := os.Stat(r.path); os.IsNotExist(err) {
		return []stampRecord{}, nil
	}

	payload, err := os.ReadFile(r.path)
	if err != nil {
		return nil, err
	}
	if len(payload) == 0 {
		return []stampRecord{}, nil
	}

	var records []stampRecord
	if err := json.Unmarshal(payload, &records); err != nil {
		return nil, err
	}

	return records, nil
}

func (r StampRepository) writeAll(records []stampRecord) error {
	payload, err := json.MarshalIndent(records, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(r.path, payload, 0o644)
}

func toRecord(stamp domain.PassportStamp) stampRecord {
	return stampRecord(stamp)
}

func fromRecord(record stampRecord) domain.PassportStamp {
	return domain.PassportStamp(record)
}
