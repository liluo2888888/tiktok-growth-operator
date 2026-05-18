import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { ButtonLink } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { Reveal } from "@/components/ui/Reveal";
import { StreakPanel } from "@/components/ui/StreakPanel";
import { checkHealth } from "@/lib/api";
import { ui } from "@/lib/copy";
import { MISSIONS, QUEST_PACK } from "@/lib/quests";
import { getProfile, getStreakSummary, getSuggestedMissionId } from "@/lib/storage";

export function HomePage() {
  const profile = getProfile();
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const streak = getStreakSummary();
  const suggestionId = getSuggestedMissionId();

  useEffect(() => {
    void checkHealth().then(setApiOk);
  }, []);

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <>
      <PageHero
        kicker="首页"
        title={QUEST_PACK.title}
        lead={QUEST_PACK.description}
        aside={
          <span
            className={
              apiOk === null ? "api-pill" : apiOk ? "api-pill ok" : "api-pill err"
            }
            role="status"
          >
            {apiOk === null && ui.api.checking}
            {apiOk === true && ui.api.connected}
            {apiOk === false && ui.api.offline}
          </span>
        }
      />

      <p className="page-lead" style={{ marginTop: "-1rem" }}>
        {profile.roleLabel} · {ui.common.jobInterviewTrack}
      </p>

      <section className="home-manifesto" aria-label="Quest English 如何帮助你">
        <p>
          <strong>像真实面试一样练。</strong>
          短任务、打字作答、结构化反馈——每一轮结束都能带走可复用的英文表达，而不是空泛建议。
        </p>
        <div className="home-pillars">
          <div className="home-pillar">
            <Icon name="target" size={22} />
            <div>
              <strong>专注</strong>
              <p>3–5 分钟任务，模拟面试压力下的表达节奏。</p>
            </div>
          </div>
          <div className="home-pillar">
            <Icon name="mic" size={22} />
            <div>
              <strong>口语感</strong>
              <p>按你说话的方式打字——清晰优先，不必追求完美语法。</p>
            </div>
          </div>
          <div className="home-pillar">
            <Icon name="stamp" size={22} />
            <div>
              <strong>可验证</strong>
              <p>护照印章记录就绪度，看见自己的进步轨迹。</p>
            </div>
          </div>
        </div>
      </section>

      <Reveal stagger className="page-grid page-grid-aside">
        <StreakPanel
          streakCount={streak.streakCount}
          todayCompleted={streak.todayCompleted}
          hint={
            streak.todayCompleted
              ? "明天再来，延续你的连续练习记录。"
              : "今天完成一轮，保持练习节奏。"
          }
          ctaLabel="继续今日任务"
          ctaTo={`/quest-start?missionId=${suggestionId}&roleId=${profile.roleId}`}
        />

        <Panel title="你的任务包" variant="inset">
          <p className="card-body" style={{ marginBottom: "1rem" }}>
            {MISSIONS.length} 个任务 · Web 端打字作答 · 每轮结束后获得结构化反馈
          </p>
          <ButtonLink to="/quest-map" variant="primary">
            打开任务地图
          </ButtonLink>
        </Panel>
      </Reveal>

      <p className="footer-note">编辑感面试教练 · Quest English MVP</p>
    </>
  );
}
