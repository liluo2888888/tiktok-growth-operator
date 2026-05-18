import { MISSIONS } from "@/lib/quests";
import { getStreakWeekMarks, isStreakAtRisk, utcDateKey } from "@/lib/streakLogic";
import { getMissionStatus, getProfile, getStreakHistory, getStreakSummary } from "@/lib/storage";

export type DailyQuestSuggestion = {
  missionId: string;
  missionLabel: string;
  reason: string;
};

export function getDailyQuestSuggestion(): DailyQuestSuggestion {
  for (const mission of MISSIONS) {
    const status = getMissionStatus(mission.id);
    if (status !== "completed") {
      return {
        missionId: mission.id,
        missionLabel: mission.label,
        reason:
          status === "in_progress" ? "从上次进度继续。" : "开始今天的面试任务。"
      };
    }
  }

  const fallback = MISSIONS[0];
  return {
    missionId: fallback.id,
    missionLabel: fallback.label,
    reason: "再练一轮，保持连续练习节奏。"
  };
}

export function buildStreakPanelModel() {
  const profile = getProfile();
  const summary = getStreakSummary();
  const today = utcDateKey();
  const suggestion = getDailyQuestSuggestion();
  const weekMarks = getStreakWeekMarks(getStreakHistory(), today);
  const atRisk = isStreakAtRisk(summary, today);

  const taskTitle = summary.todayCompleted ? "今日练习已完成" : "今日推荐任务";
  const taskBody = summary.todayCompleted
    ? "明天再来，延续你的连续练习记录。"
    : `${suggestion.missionLabel} — ${suggestion.reason}`;

  const ctaTo = summary.todayCompleted
    ? undefined
    : profile
      ? `/quest-start?missionId=${suggestion.missionId}&roleId=${profile.roleId}&roleLabel=${encodeURIComponent(profile.roleLabel)}`
      : undefined;

  return {
    summary,
    suggestion,
    weekMarks,
    atRisk,
    taskTitle,
    taskBody,
    ctaLabel: summary.todayCompleted ? undefined : "继续今日任务",
    ctaTo
  };
}

export type StreakPanelModel = ReturnType<typeof buildStreakPanelModel>;
