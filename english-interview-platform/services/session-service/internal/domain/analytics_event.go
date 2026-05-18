package domain

import "time"

func NewAnalyticsEventID() string {
	return "evt_" + randomHex(8)
}

type AnalyticsEvent struct {
	ID         string
	DeviceID   string
	Event      string
	Properties map[string]any
	ClientAt   time.Time
	RecordedAt time.Time
}
