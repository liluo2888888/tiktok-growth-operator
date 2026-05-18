import { useEffect, useState } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { createSession, fetchSession, submitTurn } from "@/lib/api";
import { ui } from "@/lib/copy";
import { getMission, getRole } from "@/lib/quests";
import { getProfile, recordQuestCompletion, setMissionStatus } from "@/lib/storage";

const MIN_WORDS = 3;

export function InterviewPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const profile = getProfile();

  const roleId = params.get("roleId") ?? profile?.roleId ?? "product";
  const roleFromQuest = getRole(roleId);
  const roleLabel = params.get("roleLabel") ?? profile?.roleLabel ?? roleFromQuest?.label ?? "产品经理";
  const missionId = params.get("missionId") ?? "self_intro";
  const missionFromQuest = getMission(missionId);
  const missionLabel = params.get("missionLabel") ?? missionFromQuest?.label ?? "自我介绍";

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState("正在加载题目…");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      setLoading(true);
      setError(null);
      try {
        const boot = await createSession({ roleId, missionId });
        if (cancelled) return;
        setSessionId(boot.sessionId);
        const detail = await fetchSession(boot.sessionId);
        if (cancelled) return;
        setQuestion(detail.currentQuestion);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : ui.errors.startSession);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void boot();
    return () => {
      cancelled = true;
    };
  }, [roleId, missionId]);

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }

  const wordCount = answer.trim().split(/\s+/).filter(Boolean).length;
  const canSubmit = wordCount >= MIN_WORDS && !submitting && !!sessionId;

  async function handleSubmit() {
    if (!sessionId || !canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitTurn({ sessionId, answer: answer.trim() });
      setMissionStatus(missionId as "self_intro" | "behavioral", "completed");
      recordQuestCompletion();
      navigate(
        `/feedback?sessionId=${sessionId}&roleLabel=${encodeURIComponent(roleLabel)}&missionLabel=${encodeURIComponent(missionLabel)}`
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : ui.errors.submit);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <PageHero
        kicker="面试间"
        title="大声说出来，在这里打字"
        lead={`${roleLabel} · ${missionLabel}`}
        aside={
          <span className="interview-focus-badge">
            <Icon name="mic" size={14} />
            专注模式
          </span>
        }
      />

      {loading && (
        <div className="loading-block panel panel-inset">
          <span className="spinner" />
          正在启动会话…
        </div>
      )}

      {error && (
        <div className="error-banner" style={{ marginBottom: "var(--space-md)" }}>
          <h3>{ui.errors.generic}</h3>
          <p>{error}</p>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            {ui.common.retry}
          </Button>
        </div>
      )}

      {!loading && (
        <div className="interview-layout">
          <div className="question-block">
            <p className="panel-title">面试问题（英文）</p>
            <p className="question-text">{question}</p>
            {sessionId && <p className="word-count">{ui.common.session(sessionId)}</p>}
          </div>

          <Panel title="你的回答（英文）" className="answer-panel-accent">
            <label htmlFor="interview-answer" className="textarea-label">
              按你说话的方式写英文
            </label>
            <textarea
              id="interview-answer"
              className="textarea"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="I am a product manager with five years of experience…"
              aria-describedby="word-count-hint"
            />
            <p
              id="word-count-hint"
              className={`word-count ${wordCount >= MIN_WORDS ? "ok" : ""}`.trim()}
            >
              {ui.common.words(wordCount)} · {ui.common.minWords(MIN_WORDS)}
            </p>
            <Button
              style={{ marginTop: "1rem" }}
              disabled={!canSubmit}
              onClick={() => void handleSubmit()}
            >
              {submitting ? "提交中…" : "提交并查看反馈"}
            </Button>
          </Panel>
        </div>
      )}

      {submitting && (
        <div className="overlay" role="status">
          <div className="overlay-card">
            <span className="spinner" style={{ margin: "0 auto 12px" }} />
            正在提交你的回答…
          </div>
        </div>
      )}
    </>
  );
}
