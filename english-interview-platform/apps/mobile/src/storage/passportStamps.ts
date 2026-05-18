import AsyncStorage from "@react-native-async-storage/async-storage";

import {
  fetchPassportStampsFromApi,
  issuePassportStampOnApi
} from "@/services/passportApi";
import type { SessionDetail } from "@/services/api";

const STAMPS_KEY = "quest.passportStamps";

export type PassportScores = SessionDetail["scores"];

export type PassportStamp = {
  id: string;
  sessionId: string;
  missionId: string;
  missionLabel: string;
  roleId: string;
  roleLabel: string;
  readiness: number;
  scores: PassportScores;
  earnedAt: string;
};

async function saveLocalStamps(stamps: PassportStamp[]): Promise<void> {
  await AsyncStorage.setItem(STAMPS_KEY, JSON.stringify(stamps));
}

export async function listPassportStamps(): Promise<PassportStamp[]> {
  const remote = await fetchPassportStampsFromApi();
  if (remote) {
    await saveLocalStamps(remote);
    return remote;
  }

  const raw = await AsyncStorage.getItem(STAMPS_KEY);
  if (!raw) {
    return [];
  }

  const stamps = JSON.parse(raw) as PassportStamp[];
  return stamps.sort(
    (a, b) => new Date(b.earnedAt).getTime() - new Date(a.earnedAt).getTime()
  );
}

export async function getPassportStamp(id: string): Promise<PassportStamp | null> {
  const stamps = await listPassportStamps();
  return stamps.find((stamp) => stamp.id === id) ?? null;
}

export async function issueStampFromSession(input: {
  sessionId: string;
  missionId: string;
  missionLabel: string;
  roleId: string;
  roleLabel: string;
  detail: SessionDetail;
}): Promise<{ stamp: PassportStamp | null; isNew: boolean }> {
  if (!input.detail.turns.length) {
    return { stamp: null, isNew: false };
  }

  const remote = await issuePassportStampOnApi({
    sessionId: input.sessionId,
    missionLabel: input.missionLabel,
    roleLabel: input.roleLabel
  });
  if (remote) {
    const stamps = await listPassportStamps();
    const merged = [remote.stamp, ...stamps.filter((s) => s.id !== remote.stamp.id)];
    await saveLocalStamps(merged);
    return remote;
  }

  const stamps = await listPassportStamps();
  const existing = stamps.find((stamp) => stamp.sessionId === input.sessionId);
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
    readiness: input.detail.scores.readiness,
    scores: input.detail.scores,
    earnedAt: new Date().toISOString()
  };

  stamps.unshift(stamp);
  await saveLocalStamps(stamps);

  return { stamp, isNew: true };
}

export async function clearPassportStamps(): Promise<void> {
  await AsyncStorage.removeItem(STAMPS_KEY);
}
