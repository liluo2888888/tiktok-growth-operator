import AsyncStorage from "@react-native-async-storage/async-storage";

import { ingestAnalyticsEvents } from "@/services/analyticsApi";

const ANALYTICS_LOG_KEY = "quest.analytics.log";
const ANALYTICS_PENDING_KEY = "quest.analytics.pending";
const MAX_LOG_ENTRIES = 50;

export const ANALYTICS_EVENTS = [
  "onboarding_complete",
  "quest_start",
  "session_bootstrap",
  "turn_submit",
  "feedback_view",
  "feedback_helpful",
  "passport_stamp_earned",
  "passport_share"
] as const;

export type AnalyticsEvent = (typeof ANALYTICS_EVENTS)[number];

export type AnalyticsPayload = Record<string, string | number | boolean | null | undefined>;

export type AnalyticsRecord = {
  event: AnalyticsEvent;
  properties: Record<string, string | number | boolean>;
  at: string;
};

function normalizePayload(payload: AnalyticsPayload): Record<string, string | number | boolean> {
  const normalized: Record<string, string | number | boolean> = {};
  for (const [key, value] of Object.entries(payload)) {
    if (value === undefined || value === null) {
      continue;
    }
    normalized[key] = value;
  }
  return normalized;
}

async function readPending(): Promise<AnalyticsRecord[]> {
  const raw = await AsyncStorage.getItem(ANALYTICS_PENDING_KEY);
  if (!raw) {
    return [];
  }
  return JSON.parse(raw) as AnalyticsRecord[];
}

async function writePending(records: AnalyticsRecord[]): Promise<void> {
  if (records.length === 0) {
    await AsyncStorage.removeItem(ANALYTICS_PENDING_KEY);
    return;
  }
  await AsyncStorage.setItem(ANALYTICS_PENDING_KEY, JSON.stringify(records));
}

async function appendLog(record: AnalyticsRecord): Promise<void> {
  const raw = await AsyncStorage.getItem(ANALYTICS_LOG_KEY);
  const existing = raw ? (JSON.parse(raw) as AnalyticsRecord[]) : [];
  const next = [record, ...existing].slice(0, MAX_LOG_ENTRIES);
  await AsyncStorage.setItem(ANALYTICS_LOG_KEY, JSON.stringify(next));
}

async function flushPending(): Promise<void> {
  const pending = await readPending();
  if (pending.length === 0) {
    return;
  }

  const ok = await ingestAnalyticsEvents(pending);
  if (ok) {
    await writePending([]);
  }
}

export async function track(event: AnalyticsEvent, properties: AnalyticsPayload = {}): Promise<void> {
  const record: AnalyticsRecord = {
    event,
    properties: normalizePayload(properties),
    at: new Date().toISOString()
  };

  if (__DEV__) {
    console.info("[analytics]", record.event, record.properties);
  }

  await appendLog(record);

  const pending = await readPending();
  pending.push(record);
  await writePending(pending);

  void flushPending();
}

export async function flushAnalytics(): Promise<void> {
  await flushPending();
}

export async function getAnalyticsLog(): Promise<AnalyticsRecord[]> {
  const raw = await AsyncStorage.getItem(ANALYTICS_LOG_KEY);
  if (!raw) {
    return [];
  }
  return JSON.parse(raw) as AnalyticsRecord[];
}

export async function clearAnalyticsLog(): Promise<void> {
  await AsyncStorage.multiRemove([ANALYTICS_LOG_KEY, ANALYTICS_PENDING_KEY]);
}
