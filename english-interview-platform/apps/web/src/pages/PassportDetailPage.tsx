import { useState } from "react";
import { Navigate, useParams } from "react-router-dom";

import { Button, ButtonLink } from "@/components/ui/Button";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { ReadinessHero } from "@/components/ui/ReadinessHero";
import { ScoreList } from "@/components/ui/ScoreList";
import { ui } from "@/lib/copy";
import { sharePassportStamp } from "@/lib/shareStamp";
import { getProfile, getStamp } from "@/lib/storage";

export function PassportDetailPage() {
  const { id } = useParams();
  const profile = getProfile();
  const stamp = id ? getStamp(id) : null;
  const [shareHint, setShareHint] = useState<string | null>(null);
  const [sharing, setSharing] = useState(false);

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
        <Button
          variant="secondary"
          disabled={sharing}
          onClick={() => {
            setSharing(true);
            setShareHint(null);
            void sharePassportStamp(stamp)
              .then((channel) => {
                if (channel === "text_fallback") setShareHint(ui.passport.shareCopied);
              })
              .catch((err) => {
                if (err instanceof Error && err.name === "AbortError") return;
                setShareHint(err instanceof Error ? err.message : ui.passport.shareFailed);
              })
              .finally(() => setSharing(false));
          }}
        >
          {sharing ? "分享中…" : ui.passport.share}
        </Button>
        <ButtonLink to="/quest-map" variant="primary">
          再练一轮
        </ButtonLink>
      </div>
      {shareHint && <p className="word-count ok">{shareHint}</p>}
    </>
  );
}
