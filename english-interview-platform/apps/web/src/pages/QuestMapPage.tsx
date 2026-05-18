import { Navigate } from "react-router-dom";

import { MissionTile } from "@/components/ui/MissionTile";
import { PageHero } from "@/components/ui/PageHero";
import { Reveal } from "@/components/ui/Reveal";
import { StreakPanel } from "@/components/ui/StreakPanel";
import { buildStreakPanelModel } from "@/lib/streak";
import { ui } from "@/lib/copy";
import { MISSIONS, QUEST_PACK } from "@/lib/quests";
import { getMissionStatus, getProfile } from "@/lib/storage";
import type { MissionStatus } from "@/lib/quests";

function statusLabel(status: MissionStatus) {
  if (status === "completed") return ui.status.completed;
  if (status === "in_progress") return ui.status.inProgress;
  return ui.status.notStarted;
}

export function QuestMapPage() {
  const profile = getProfile();
  const streakModel = buildStreakPanelModel();

  if (!profile?.completedOnboarding) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <>
      <PageHero
        kicker="任务地图"
        title={QUEST_PACK.title}
        lead={`${QUEST_PACK.description} ${ui.common.track(profile.roleLabel)}`}
      />

      <StreakPanel
        compact
        streakCount={streakModel.summary.streakCount}
        todayCompleted={streakModel.summary.todayCompleted}
        atRisk={streakModel.atRisk}
        taskTitle={streakModel.taskTitle}
        taskBody={streakModel.taskBody}
        weekMarks={streakModel.weekMarks}
        ctaLabel={streakModel.ctaLabel}
        ctaTo={streakModel.ctaTo}
      />

      <Reveal stagger className="stack">
        {MISSIONS.map((mission, index) => (
          <MissionTile
            key={mission.id}
            index={index}
            to={`/quest-start?missionId=${mission.id}&roleId=${profile.roleId}`}
            label={mission.label}
            subtitle={mission.subtitle}
            durationMinutes={mission.durationMinutes}
            statusLabel={statusLabel(getMissionStatus(mission.id))}
          />
        ))}
      </Reveal>
    </>
  );
}
