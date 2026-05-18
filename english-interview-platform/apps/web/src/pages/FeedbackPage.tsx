import { useEffect, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";

import { ButtonLink } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { ReadinessHero } from "@/components/ui/ReadinessHero";
import { ScoreList } from "@/components/ui/ScoreList";
import { fetchSession, type SessionDetail } from "@/lib/api";
import { stageLabel, ui } from "@/lib/copy";
import { getMission } from "@/lib/quests";
import { getProfile, issueStamp } from "@/lib/storage";

export function FeedbackPage() {
  const [params] = useSearchParams();
  const profile = getProfile();
  const sessionId = params.get("sessionId");
  const roleLabel = params.get("roleLabel") ?? profile?.roleLabel ?? "";
  const missionLabelParam = params.get("missionLabel") ?? "";

  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stampId, setStampId] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    const sid = sessionId;
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchSession(sid);
        if (cancelled) return;
        setDetail(result);
        const mission = getMission(result.missionId);
        const missionLabel = missionLabelParam || mission?.label || result.missionId;
        const { stamp, isNew } = issueStamp({
          sessionId: sid,
          missionId: result.missionId,
          missionLabel,
          roleId: result.roleId,
          roleLabel: roleLabel || profile?.roleLabel || result.roleId,
          scores: result.scores
        });
        if (isNew) setStampId(stamp.id);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : ui.errors.load);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [sessionId, roleLabel, missionLabelParam, profile?.roleLabel]);

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }
  if (!sessionId) {
    return <Navigate to="/quest-map" replace />;
  }

  const displayMission =
    missionLabelParam || (detail ? getMission(detail.missionId)?.label : "") || "";

  return (
    <>
      <PageHero
        kicker="反馈"
        title="本轮面试结果"
        lead={`${roleLabel} · ${displayMission}`}
      />

      {loading && (
        <div className="loading-block panel panel-inset">
          <span className="spinner" />
          正在加载结构化反馈…
        </div>
      )}

      {error && (
        <div className="error-banner">
          <h3>{ui.errors.loadFeedback}</h3>
          <p>{error}</p>
        </div>
      )}

      {detail && !loading && (
        <div className="page-grid page-grid-aside">
          <div className="stack">
            <ReadinessHero readiness={detail.scores.readiness} />
            <Panel title={ui.scores.breakdown}>
              <ScoreList scores={detail.scores} />
            </Panel>
            <Panel title={ui.common.stage(stageLabel(detail.stage))} variant="inset">
              <p className="card-body">{detail.currentQuestion}</p>
            </Panel>
          </div>

          <div className="stack">
            {detail.turns.map((turn, index) => (
              <Panel key={turn.id} title={ui.common.turn(index + 1)}>
                <p className="card-body" style={{ fontWeight: 600, color: "var(--ink)" }}>
                  {turn.question}
                </p>
                <p className="card-body" style={{ marginTop: "0.5rem" }}>
                  <strong>你的回答：</strong>
                  {turn.answer}
                </p>
                <p className="card-body" style={{ marginTop: "0.5rem" }}>
                  {turn.feedback.summary}
                </p>
                <p className="word-count">{turn.feedback.improvementTip}</p>
              </Panel>
            ))}

            {stampId && (
              <Panel title="获得护照印章" variant="highlight">
                <div className="stamp-earned">
                  <div className="stamp-earned-icon" aria-hidden>
                    <Icon name="sparkles" size={22} />
                  </div>
                  <div>
                    <p className="card-body">你为本轮练习解锁了一枚新印章。</p>
                    <ButtonLink to={`/passport/${stampId}`} style={{ marginTop: "0.75rem" }}>
                      查看印章
                    </ButtonLink>
                  </div>
                </div>
              </Panel>
            )}

            <div className="row">
              <ButtonLink to="/quest-map" variant="primary">
                {ui.nav.questMap}
              </ButtonLink>
              <ButtonLink to="/passport" variant="secondary">
                {ui.nav.passport}
              </ButtonLink>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
