import AsyncStorage from "@react-native-async-storage/async-storage";

import { getRoleById, type QuestGoal } from "@/content/quests";
import { clearPassportStamps } from "@/storage/passportStamps";

const PROFILE_KEY = "quest.userProfile";
const MISSION_STATUS_PREFIX = "quest.missionStatus.";

export type UserProfile = {
  goal: QuestGoal;
  roleId: string;
  roleLabel: string;
  onboardingCompletedAt: string;
};

export type MissionStatus = "not_started" | "in_progress" | "completed";

export async function getUserProfile(): Promise<UserProfile | null> {
  const raw = await AsyncStorage.getItem(PROFILE_KEY);
  if (!raw) {
    return null;
  }

  return JSON.parse(raw) as UserProfile;
}

export async function hasCompletedOnboarding(): Promise<boolean> {
  const profile = await getUserProfile();
  return Boolean(profile?.onboardingCompletedAt);
}

export async function saveOnboardingProfile(input: {
  goal: QuestGoal;
  roleId: string;
}): Promise<UserProfile> {
  const role = getRoleById(input.roleId);
  const profile: UserProfile = {
    goal: input.goal,
    roleId: input.roleId,
    roleLabel: role?.label ?? input.roleId,
    onboardingCompletedAt: new Date().toISOString()
  };

  await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  return profile;
}

export async function getMissionStatus(missionId: string): Promise<MissionStatus> {
  const value = await AsyncStorage.getItem(MISSION_STATUS_PREFIX + missionId);
  if (value === "completed" || value === "in_progress") {
    return value;
  }

  return "not_started";
}

export async function setMissionStatus(
  missionId: string,
  status: MissionStatus
): Promise<void> {
  await AsyncStorage.setItem(MISSION_STATUS_PREFIX + missionId, status);
}

export async function markMissionInProgress(missionId: string): Promise<void> {
  const current = await getMissionStatus(missionId);
  if (current === "completed") {
    return;
  }

  await setMissionStatus(missionId, "in_progress");
}

export async function markMissionCompleted(missionId: string): Promise<void> {
  await setMissionStatus(missionId, "completed");
}

export async function clearUserData(): Promise<void> {
  const keys = await AsyncStorage.getAllKeys();
  const questKeys = keys.filter((key) => key.startsWith("quest."));
  await AsyncStorage.multiRemove(questKeys);
  await clearPassportStamps();
}
