import { Link, Navigate } from "react-router-dom";

import { ButtonLink } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { Reveal } from "@/components/ui/Reveal";
import { ui } from "@/lib/copy";
import { getProfile, listStamps } from "@/lib/storage";

export function PassportPage() {
  const profile = getProfile();
  const stamps = listStamps();

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <>
      <PageHero
        kicker="进度"
        title="护照"
        lead="每完成一轮练习即可获得一枚印章，附带就绪度分数——这是你坚持练习的证明。"
      />

      {stamps.length === 0 ? (
        <Panel className="empty-state">
          <div className="passport-empty-icon" aria-hidden>
            <Icon name="passport" size={32} />
          </div>
          <h2 className="panel-title">还没有印章</h2>
          <p className="card-body">完成第一轮面试练习即可解锁首枚印章。</p>
          <ButtonLink to="/quest-map" style={{ marginTop: "1.25rem" }}>
            开始第一个任务
          </ButtonLink>
        </Panel>
      ) : (
        <Reveal stagger className="stamp-list">
          {stamps.map((stamp) => (
            <Link key={stamp.id} to={`/passport/${stamp.id}`} className="stamp-card">
              <div
                className="stamp-readiness"
                aria-label={ui.scores.readinessOf(stamp.readiness)}
              >
                {stamp.readiness}
                <span>{ui.scores.ready}</span>
              </div>
              <div>
                <strong>{stamp.missionLabel}</strong>
                <p className="stamp-card-meta">
                  {stamp.roleLabel} ·{" "}
                  {new Date(stamp.earnedAt).toLocaleDateString("zh-CN")}
                </p>
              </div>
              <span className="mission-tile-arrow" aria-hidden>
                <Icon name="arrowRight" size={18} />
              </span>
            </Link>
          ))}
        </Reveal>
      )}
    </>
  );
}
