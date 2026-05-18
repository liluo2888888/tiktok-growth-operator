import { Navigate, useParams } from "react-router-dom";

import { ButtonLink } from "@/components/ui/Button";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { ReadinessHero } from "@/components/ui/ReadinessHero";
import { ScoreList } from "@/components/ui/ScoreList";
import { ui } from "@/lib/copy";
import { getProfile, getStamp } from "@/lib/storage";

export function PassportDetailPage() {
  const { id } = useParams();
  const profile = getProfile();
  const stamp = id ? getStamp(id) : null;

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }

  if (!stamp) {
    return (
      <>
        <h1 className="page-title">未找到该印章</h1>
        <ButtonLink to="/passport">返回护照</ButtonLink>
      </>
    );
  }

  const earnedDate = new Date(stamp.earnedAt).toLocaleDateString("zh-CN");

  return (
    <>
      <PageHero
        kicker="印章详情"
        title={stamp.missionLabel}
        lead={ui.common.earnedAt(earnedDate) + ` · ${stamp.roleLabel}`}
        aside={<ReadinessHero readiness={stamp.readiness} />}
      />

      <Panel title={ui.scores.breakdown}>
        <ScoreList scores={stamp.scores} />
      </Panel>

      <div className="row" style={{ marginTop: "var(--space-md)" }}>
        <ButtonLink to="/passport" variant="secondary">
          {ui.common.back}
        </ButtonLink>
        <ButtonLink to="/quest-map" variant="primary">
          再练一轮
        </ButtonLink>
      </div>
    </>
  );
}
