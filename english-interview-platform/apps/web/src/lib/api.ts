const apiBase =
  import.meta.env.VITE_API_BASE_URL?.trim() ||
  (import.meta.env.DEV ? "" : "http://localhost:8080");

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
    feedback: { summary: string; improvementTip: string };
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

async function parseError(response: Response, fallback: string) {
  if (!response.ok) {
    throw new Error(`${fallback}（${response.status}）`);
  }
}

export async function createSession(input: {
  roleId: string;
  missionId: string;
}): Promise<SessionBootstrap> {
  const response = await fetch(`${apiBase}/v1/mobile/session/bootstrap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input)
  });
  await parseError(response, "无法启动练习会话");
  return response.json();
}

export async function fetchSession(sessionId: string): Promise<SessionDetail> {
  const response = await fetch(`${apiBase}/v1/mobile/sessions/${sessionId}`);
  await parseError(response, "无法加载会话");
  return response.json();
}

export async function submitTurn(input: {
  sessionId: string;
  answer: string;
}): Promise<SessionDetail> {
  const response = await fetch(`${apiBase}/v1/mobile/sessions/${input.sessionId}/turns`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer: input.answer })
  });
  await parseError(response, "无法提交回答");
  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${apiBase}/healthz`, { method: "GET" });
    return response.ok;
  } catch {
    return false;
  }
}
