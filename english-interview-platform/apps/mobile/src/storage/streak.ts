import AsyncStorage from "@react-native-async-storage/async-storage";

import { MISSIONS, getMissionById } from "@/content/quests";
import {
  applyQuestCompletion,
  readStreakSummary,
  utcDateKey,
  type StreakState,
  type StreakSummary
} from "@/features/streak/streakLogic";
import { getMissionStatus, getUserProfile } from "@/storage/userProfile";

const STREAK_KEY = "quest.streak";

export type DailyQuestSuggestion = {
  missionId: string;
  missionLabel: string;
  reason: string;
};

async function loadState(): Promise<StreakState> {
  const raw = await AsyncStorage.getItem(STREAK_KEY);
  if (!raw) {
    return { streakCount: 0, lastCompletedDate: null };
  }

  return JSON.parse(raw) as StreakState;
}

async function saveState(state: StreakState): Promise<void> {
  await AsyncStorage.setItem(STREAK_KEY, JSON.stringify(state));
}

export async function getStreakSummary(): Promise<StreakSummary> {
  const state = await loadState();
  return readStreakSummary(state, utcDateKey());
}

export async function recordQuestCompletion(): Promise<StreakSummary> {
  const today = utcDateKey();
  const next = applyQuestCompletion(await loadState(), today);
  await saveState({
    streakCount: next.streakCount,
    lastCompletedDate: next.lastCompletedDate
  });
  return next;
}

export async function getDailyQuestSuggestion(): Promise<DailyQuestSuggestion> {
  for (const mission of MISSIONS) {
    const status = await getMissionStatus(mission.id);
    if (status !== "completed") {
      return {
        missionId: mission.id,
        missionLabel: mission.label,
        reason:
          status === "in_progress"
            ? "Continue where you left off."
            : "Start today's interview quest."
      };
    }
  }

  const fallback = MISSIONS[0];
  return {
    missionId: fallback.id,
    missionLabel: fallback.label,
    reason: "Practice again to keep your streak."
  };
}

export async function openSuggestedQuest(): Promise<{
  pathname: "/quest-start";
  params: Record<string, string>;
}> {
  const profile = await getUserProfile();
  const suggestion = await getDailyQuestSuggestion();
  const mission = getMissionById(suggestion.missionId) ?? MISSIONS[0];

  return {
    pathname: "/quest-start",
    params: {
      roleId: profile?.roleId ?? "product",
      roleLabel: profile?.roleLabel ?? "Product Manager",
      missionId: mission.id,
      missionLabel: mission.label
    }
  };
}

export async function clearStreakData(): Promise<void> {
  await AsyncStorage.removeItem(STREAK_KEY);
}
