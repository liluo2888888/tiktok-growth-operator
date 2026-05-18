package domain

import (
	"crypto/rand"
	"encoding/hex"
	"strings"
	"time"
)

type Session struct {
	ID          string
	RoleID      string
	MissionID   string
	ClientToken string
	Status      string
	Stage       string
	CurrentQuestion string
	Turns       []Turn
	Scores      Scores
}

type Turn struct {
	ID        string       `json:"id"`
	Speaker   string       `json:"speaker"`
	CreatedAt string       `json:"createdAt"`
	Question  string       `json:"question"`
	Answer    string       `json:"answer"`
	Feedback  TurnFeedback `json:"feedback"`
}

type TurnFeedback struct {
	Summary        string `json:"summary"`
	ImprovementTip string `json:"improvementTip"`
}

type Scores struct {
	Clarity    int `json:"clarity"`
	Structure  int `json:"structure"`
	Confidence int `json:"confidence"`
	Relevance  int `json:"relevance"`
	Readiness  int `json:"readiness"`
}

func (s *Session) AddTurn(answer string) {
	question := s.CurrentQuestion
	if question == "" {
		question = nextQuestionForMission(s.MissionID, len(s.Turns))
	}

	s.Turns = append(s.Turns, Turn{
		ID:        "turn_" + randomHex(6),
		Speaker:   "candidate",
		CreatedAt: nowTimestamp(),
		Question:  question,
		Answer:    answer,
		Feedback:  feedbackFromAnswer(answer),
	})
	s.Status = "in_progress"
	s.Stage = nextStage(s.MissionID, len(s.Turns))
	s.CurrentQuestion = nextQuestionForMission(s.MissionID, len(s.Turns))
	s.Scores = scoreFromTurns(s.Turns)
}

func NewSession(roleID string, missionID string) Session {
	initialQuestion := nextQuestionForMission(missionID, 0)
	seedTurns := []Turn{
		{
			ID:        "turn_" + randomHex(6),
			Speaker:   "candidate",
			CreatedAt: nowTimestamp(),
			Question:  initialQuestion,
			Answer:    "I have been preparing for an international interview process.",
			Feedback: TurnFeedback{
				Summary:        "Clear opening with direct context.",
				ImprovementTip: "Make the role target more specific in the first sentence.",
			},
		},
		{
			ID:        "turn_" + randomHex(6),
			Speaker:   "candidate",
			CreatedAt: nowTimestamp(),
			Question:  nextQuestionForMission(missionID, 1),
			Answer:    "I want this role because it combines product judgment and global execution.",
			Feedback: TurnFeedback{
				Summary:        "Strong motivation signal.",
				ImprovementTip: "Add one concrete example that proves this motivation.",
			},
		},
	}

	return Session{
		ID:          "sess_" + randomHex(8),
		RoleID:      roleID,
		MissionID:   missionID,
		ClientToken: "rt_demo_token",
		Status:      "ready",
		Stage:       nextStage(missionID, len(seedTurns)),
		CurrentQuestion: nextQuestionForMission(missionID, len(seedTurns)),
		Turns:       seedTurns,
		Scores: Scores{
			Clarity:    78,
			Structure:  74,
			Confidence: 69,
			Relevance:  81,
			Readiness:  73,
		},
	}
}

func scoreFromTurns(turns []Turn) Scores {
	answerCount := len(turns)
	if answerCount < 1 {
		answerCount = 1
	}

	readiness := 68 + min(answerCount*2, 14)
	clarity := 72 + min(answerCount, 10)
	structure := 70 + min(answerCount, 12)
	confidence := 66 + min(answerCount*2, 16)
	relevance := 78 + min(answerCount, 8)

	return Scores{
		Clarity:    min(clarity, 95),
		Structure:  min(structure, 95),
		Confidence: min(confidence, 95),
		Relevance:  min(relevance, 95),
		Readiness:  min(readiness, 96),
	}
}

func feedbackFromAnswer(answer string) TurnFeedback {
	answerLen := len(strings.Fields(answer))
	if answerLen < 12 {
		return TurnFeedback{
			Summary:        "Answer is concise but still thin on evidence.",
			ImprovementTip: "Expand with one concrete example and one measurable result.",
		}
	}

	return TurnFeedback{
		Summary:        "Answer has enough content to evaluate structure and intent.",
		ImprovementTip: "Tighten the structure into context, action, and result.",
	}
}

func nextQuestionForMission(missionID string, turnIndex int) string {
	questionSets := map[string][]string{
		"self_intro": {
			"Tell me about yourself.",
			"Why are you interested in this role?",
			"What is one strength you want us to remember?",
		},
		"behavioral": {
			"Tell me about a time you handled a difficult cross-functional situation.",
			"What was your specific contribution?",
			"What would you do differently next time?",
		},
		"case_round": {
			"How would you structure the problem first?",
			"What assumptions would you test early?",
			"How would you recommend a final decision?",
		},
	}

	questions, ok := questionSets[missionID]
	if !ok || len(questions) == 0 {
		questions = []string{
			"Tell me about yourself.",
			"Why are you a strong fit for this role?",
			"What would you improve in your answer?",
		}
	}

	if turnIndex < len(questions) {
		return questions[turnIndex]
	}

	return questions[len(questions)-1]
}

func nextStage(missionID string, completedTurns int) string {
	stageSets := map[string][]string{
		"self_intro": {"opening", "motivation", "positioning", "closing"},
		"behavioral": {"situation", "action", "reflection", "closing"},
		"case_round": {"framing", "analysis", "recommendation", "closing"},
	}

	stages, ok := stageSets[missionID]
	if !ok || len(stages) == 0 {
		stages = []string{"opening", "core", "reflection", "closing"}
	}

	if completedTurns < len(stages) {
		return stages[completedTurns]
	}

	return stages[len(stages)-1]
}

func min(a int, b int) int {
	if a < b {
		return a
	}

	return b
}

func randomHex(size int) string {
	buf := make([]byte, size)
	if _, err := rand.Read(buf); err != nil {
		return "fallback00000000"
	}

	return hex.EncodeToString(buf)
}

func nowTimestamp() string {
	return time.Now().UTC().Format(time.RFC3339)
}
