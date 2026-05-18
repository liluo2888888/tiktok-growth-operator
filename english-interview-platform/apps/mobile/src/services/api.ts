export const apiBaseUrl =
  process.env.EXPO_PUBLIC_API_BASE_URL?.trim() || "http://localhost:8080";

export type SessionBootstrap = {
  sessionId: string;
  clientToken: string;
  status: string;
  roleId: string;
  missionId: string;
};

export type SessionDetail = {
  sessionId: string;
  status: string;
  stage: string;
  currentQuestion: string;
  roleId: string;
  missionId: string;
  turns: {
    id: string;
    speaker: string;
    createdAt: string;
    question: string;
    answer: string;
    feedback: {
      summary: string;
      improvementTip: string;
    };
  }[];
  transcript: string[];
  scores: {
    clarity: number;
    structure: number;
    confidence: number;
    relevance: number;
    readiness: number;
  };
};

export async function createInterviewSession(input: {
  roleId: string;
  missionId: string;
}): Promise<SessionBootstrap> {
  const response = await fetch(`${apiBaseUrl}/v1/mobile/session/bootstrap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });

  if (!response.ok) {
    throw new Error(
      `Failed to bootstrap session (${response.status}) at ${apiBaseUrl}. Check device-debug panel / scripts/device-debug.ps1.`
    );
  }

  return response.json();
}

export async function fetchSessionDetail(sessionId: string): Promise<SessionDetail> {
  const response = await fetch(`${apiBaseUrl}/v1/mobile/sessions/${sessionId}`);

  if (!response.ok) {
    throw new Error(`Failed to load session detail: ${response.status}`);
  }

  return response.json();
}

export async function submitInterviewTurn(input: {
  sessionId: string;
  answer: string;
}): Promise<SessionDetail> {
  const response = await fetch(`${apiBaseUrl}/v1/mobile/sessions/${input.sessionId}/turns`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      answer: input.answer
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to submit turn: ${response.status}`);
  }

  return response.json();
}
