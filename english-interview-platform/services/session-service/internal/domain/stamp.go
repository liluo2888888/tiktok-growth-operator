package domain

import "time"

type PassportStamp struct {
	ID           string    `json:"id"`
	DeviceID     string    `json:"deviceId"`
	SessionID    string    `json:"sessionId"`
	MissionID    string    `json:"missionId"`
	MissionLabel string    `json:"missionLabel"`
	RoleID       string    `json:"roleId"`
	RoleLabel    string    `json:"roleLabel"`
	Readiness    int       `json:"readiness"`
	Scores       Scores    `json:"scores"`
	EarnedAt     time.Time `json:"earnedAt"`
}
