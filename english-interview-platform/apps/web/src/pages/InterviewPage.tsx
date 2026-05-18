import { useEffect, useState } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

import { VoiceAnswerPanel } from "@/components/interview/VoiceAnswerPanel";
import { Button } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { useVoiceAnswer } from "@/hooks/useVoiceAnswer";
import { track } from "@/lib/analytics";
import { createSession, fetchSession, submitTurn } from "@/lib/api";
import { ui } from "@/lib/copy";
import { getMission, getRole } from "@/lib/quests";
import { getProfile, recordQuestCompletion, setMissionStatus } from "@/lib/storage";
import { countWords } from "@/lib/voiceValidation";

const MIN_WORDS = 3;

export function InterviewPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const profile = getProfile();
  const voice = useVoiceAnswer();

  const roleId = params.get("roleId") ?? profile?.roleId ?? "product";
  const roleFromQuest = getRole(roleId);
  const roleLabel = params.get("roleLabel") ?? profile?.roleLabel ?? roleFromQuest?.label ?? "产品经理";
  const missionId = params.get("missionId") ?? "self_intro";
  const missionFromQuest = getMission(missionId);
  const missionLabel = params.get("missionLabel") ?? missionFromQuest?.label ?? "自我介绍";

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState("正在加载题目…");
  const [answerMode, setAnswerMode] = useState<"voice" | "manual">("voice");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void voice.prepare();
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      setLoading(true);
      setError(null);
      try {
        const boot = await createSession({ roleId, missionId });
        if (cancelled) return;
        setSessionId(boot.sessionId);
        void track("session_bootstrap", { sessionId: boot.sessionId, roleId, missionId });
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

  const manualWordCount = countWords(answer);
  const canSubmitManual = manualWordCount >= MIN_WORDS && !submitting && !!sessionId;

  async function submitAnswer(text: string) {
    if (!sessionId) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitTurn({ sessionId, answer: text.trim() });
      void track("turn_submit", { sessionId, missionId, roleId, mode: answerMode });
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

  function switchToManual() {
    if (voice.transcript.trim()) {
      setAnswer(voice.transcript);
    }
    setAnswerMode("manual");
  }

  return (
    <>
      <PageHero
        kicker="面试间"
        title={answerMode === "voice" ? "大声说出来" : "在这里手打英文"}
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

          {answerMode === "voice" ? (
            <Panel title={ui.interview.voiceTitle} className="answer-panel-accent">
              <VoiceAnswerPanel
                voice={voice}
                submitting={submitting}
                onSubmit={() => void submitAnswer(voice.transcript)}
                onUseManual={switchToManual}
              />
            </Panel>
          ) : (
            <Panel title={ui.interview.manualTitle} className="answer-panel-accent">
              <p className="card-body">{ui.interview.manualHint}</p>
              <Button
                type="button"
                variant="secondary"
                style={{ marginBottom: "1rem" }}
                onClick={() => setAnswerMode("voice")}
              >
                {ui.interview.useVoice}
              </Button>
              <label htmlFor="interview-answer" className="textarea-label">
                英文回答
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
                className={`word-count ${manualWordCount >= MIN_WORDS ? "ok" : ""}`.trim()}
              >
                {ui.common.words(manualWordCount)} · {ui.common.minWords(MIN_WORDS)}
              </p>
              <Button
                style={{ marginTop: "1rem" }}
                disabled={!canSubmitManual}
                onClick={() => void submitAnswer(answer)}
              >
                {submitting ? ui.interview.submitting : ui.interview.submit}
              </Button>
            </Panel>
          )}
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
