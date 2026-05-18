import { apiBaseUrl } from "@/services/api";
import type { AnalyticsRecord } from "@/services/analytics";
import { getDeviceId } from "@/storage/deviceId";

export async function ingestAnalyticsEvents(records: AnalyticsRecord[]): Promise<boolean> {
  if (records.length === 0) {
    return true;
  }

  try {
    const response = await fetch(`${apiBaseUrl}/v1/mobile/analytics/events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Device-Id": await getDeviceId()
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
