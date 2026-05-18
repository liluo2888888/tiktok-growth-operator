import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

import { Button, ButtonLink } from "@/components/ui/Button";
import { PageHero } from "@/components/ui/PageHero";
import { Panel } from "@/components/ui/Panel";
import { ui } from "@/lib/copy";
import { getMission, getRole } from "@/lib/quests";
import { getProfile, setMissionStatus } from "@/lib/storage";

export function QuestStartPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const profile = getProfile();
  const missionId = params.get("missionId") ?? "self_intro";
  const roleId = params.get("roleId") ?? profile?.roleId ?? "product";
  const mission = getMission(missionId);
  const role = getRole(roleId);

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }
  if (!mission || !role) {
    return <Navigate to="/quest-map" replace />;
  }

  function begin() {
    if (!mission || !role) return;
    setMissionStatus(mission.id, "in_progress");
    navigate(
      `/interview?missionId=${mission.id}&missionLabel=${encodeURIComponent(mission.label)}&roleId=${role.id}&roleLabel=${encodeURIComponent(role.label)}`
    );
  }

  return (
    <>
      <PageHero
        kicker="开始任务"
        title={mission.label}
        lead={ui.common.track(role.label)}
      />

      <div className="quest-brief-grid">
        <Panel title="本轮练习">
          <p className="card-body">{mission.subtitle}</p>
          <p className="word-count">
            {ui.common.minutes(mission.durationMinutes)} · Web 端打字作答
          </p>
        </Panel>
        <Panel title="面试官" variant="highlight">
          <p className="interviewer-quote">{mission.interviewerLine}</p>
        </Panel>
      </div>

      <div className="row" style={{ marginTop: "var(--space-md)" }}>
        <Button onClick={begin}>开始练习</Button>
        <ButtonLink to="/quest-map" variant="secondary">
          返回地图
        </ButtonLink>
      </div>
    </>
  );
}
