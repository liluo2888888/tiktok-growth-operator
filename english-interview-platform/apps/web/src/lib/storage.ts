import type { MissionId, MissionStatus, QuestGoal, RoleId } from "./quests";

const PROFILE_KEY = "quest.profile";
const MISSION_PREFIX = "quest.mission.";
const STREAK_KEY = "quest.streak";
const DEVICE_KEY = "quest.deviceId";
const STAMPS_KEY = "quest.passport.stamps";

export type UserProfile = {
  goal: QuestGoal;
  roleId: RoleId;
  roleLabel: string;
  completedOnboarding: boolean;
};

export type PassportStamp = {
  id: string;
  sessionId: string;
  missionId: string;
  missionLabel: string;
  roleId: string;
  roleLabel: string;
  readiness: number;
  scores: SessionScores;
  earnedAt: string;
};

export type SessionScores = {
  clarity: number;
  structure: number;
  confidence: number;
  relevance: number;
  readiness: number;
};

type StreakState = {
  streakCount: number;
  lastCompletedDate: string | null;
};

function readJson<T>(key: string, fallback: T): T {
  const raw = localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getDeviceId(): string {
  const existing = localStorage.getItem(DEVICE_KEY);
  if (existing) return existing;
  const created = `web_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  localStorage.setItem(DEVICE_KEY, created);
  return created;
}

export function getProfile(): UserProfile | null {
  return readJson<UserProfile | null>(PROFILE_KEY, null);
}

export function saveProfile(input: { goal: QuestGoal; roleId: RoleId; roleLabel: string }) {
  const profile: UserProfile = {
    goal: input.goal,
    roleId: input.roleId,
    roleLabel: input.roleLabel,
    completedOnboarding: true
  };
  writeJson(PROFILE_KEY, profile);
  return profile;
}

export function getMissionStatus(missionId: MissionId): MissionStatus {
  return readJson<MissionStatus>(`${MISSION_PREFIX}${missionId}`, "not_started");
}

export function setMissionStatus(missionId: MissionId, status: MissionStatus) {
  writeJson(`${MISSION_PREFIX}${missionId}`, status);
}

function utcDateKey(date = new Date()) {
  return date.toISOString().slice(0, 10);
}

export function getStreakSummary() {
  const state = readJson<StreakState>(STREAK_KEY, { streakCount: 0, lastCompletedDate: null });
  const today = utcDateKey();
  const todayCompleted = state.lastCompletedDate === today;
  let streakCount = state.streakCount;

  if (!todayCompleted && state.lastCompletedDate) {
    const yesterday = new Date();
    yesterday.setUTCDate(yesterday.getUTCDate() - 1);
    if (state.lastCompletedDate !== utcDateKey(yesterday)) {
      streakCount = 0;
    }
  }

  return { streakCount, todayCompleted, lastCompletedDate: state.lastCompletedDate };
}

export function recordQuestCompletion() {
  const today = utcDateKey();
  const state = readJson<StreakState>(STREAK_KEY, { streakCount: 0, lastCompletedDate: null });
  if (state.lastCompletedDate === today) {
    return getStreakSummary();
  }

  const yesterday = new Date();
  yesterday.setUTCDate(yesterday.getUTCDate() - 1);
  let streakCount = 1;
  if (state.lastCompletedDate === utcDateKey(yesterday)) {
    streakCount = Math.max(1, state.streakCount + 1);
  }

  writeJson(STREAK_KEY, { streakCount, lastCompletedDate: today });
  return getStreakSummary();
}

export function listStamps(): PassportStamp[] {
  const stamps = readJson<PassportStamp[]>(STAMPS_KEY, []);
  return [...stamps].sort(
    (a, b) => new Date(b.earnedAt).getTime() - new Date(a.earnedAt).getTime()
  );
}

export function getStamp(id: string) {
  return listStamps().find((s) => s.id === id) ?? null;
}

export function issueStamp(input: {
  sessionId: string;
  missionId: string;
  missionLabel: string;
  roleId: string;
  roleLabel: string;
  scores: SessionScores;
}): { stamp: PassportStamp; isNew: boolean } {
  const stamps = listStamps();
  const existing = stamps.find((s) => s.sessionId === input.sessionId);
  if (existing) {
    return { stamp: existing, isNew: false };
  }

  const stamp: PassportStamp = {
    id: `stamp_${input.sessionId}`,
    sessionId: input.sessionId,
    missionId: input.missionId,
    missionLabel: input.missionLabel,
    roleId: input.roleId,
    roleLabel: input.roleLabel,
    readiness: input.scores.readiness,
    scores: input.scores,
    earnedAt: new Date().toISOString()
  };

  writeJson(STAMPS_KEY, [stamp, ...stamps]);
  return { stamp, isNew: true };
}

export function getSuggestedMissionId(): MissionId {
  for (const id of ["self_intro", "behavioral"] as MissionId[]) {
    if (getMissionStatus(id) !== "completed") return id;
  }
  return "self_intro";
}
