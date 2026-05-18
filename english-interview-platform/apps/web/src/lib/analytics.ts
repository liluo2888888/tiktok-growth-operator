import { getDeviceId } from "@/lib/storage";

const PENDING_KEY = "quest.analytics.pending";
const LOG_KEY = "quest.analytics.log";
const MAX_LOG = 50;

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
    if (value === undefined || value === null) continue;
    normalized[key] = value;
  }
  return normalized;
}

function readPending(): AnalyticsRecord[] {
  try {
    const raw = localStorage.getItem(PENDING_KEY);
    return raw ? (JSON.parse(raw) as AnalyticsRecord[]) : [];
  } catch {
    return [];
  }
}

function writePending(records: AnalyticsRecord[]) {
  if (records.length === 0) {
    localStorage.removeItem(PENDING_KEY);
    return;
  }
  localStorage.setItem(PENDING_KEY, JSON.stringify(records));
}

function appendLog(record: AnalyticsRecord) {
  try {
    const raw = localStorage.getItem(LOG_KEY);
    const existing = raw ? (JSON.parse(raw) as AnalyticsRecord[]) : [];
    localStorage.setItem(LOG_KEY, JSON.stringify([record, ...existing].slice(0, MAX_LOG)));
  } catch {
    /* ignore quota */
  }
}

async function ingestAnalyticsEvents(records: AnalyticsRecord[]): Promise<boolean> {
  if (records.length === 0) return true;
  try {
    const response = await fetch("/v1/mobile/analytics/events", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Device-Id": getDeviceId()
      },
      body: JSON.stringify({
        events: records.map((record) => ({
          event: record.event,
          properties: record.properties,
          at: record.at
        }))
      })
    });
    return response.ok;
  } catch {
    return false;
  }
}

async function flushPending() {
  const pending = readPending();
  if (pending.length === 0) return;
  const ok = await ingestAnalyticsEvents(pending);
  if (ok) writePending([]);
}

export async function track(event: AnalyticsEvent, properties: AnalyticsPayload = {}) {
  const record: AnalyticsRecord = {
    event,
    properties: normalizePayload(properties),
    at: new Date().toISOString()
  };

  if (import.meta.env.DEV) {
    console.info("[analytics]", record.event, record.properties);
  }

  appendLog(record);
  const pending = readPending();
  pending.push(record);
  writePending(pending);
  void flushPending();
}
