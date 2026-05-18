import { apiBaseUrl } from "@/services/api";

export type ApiHealthResult = {
  ok: boolean;
  url: string;
  status?: number;
  error?: string;
};

export async function checkApiHealth(timeoutMs = 5000): Promise<ApiHealthResult> {
  const url = `${apiBaseUrl}/healthz`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    return {
      ok: response.ok,
      url,
      status: response.status,
      error: response.ok ? undefined : `HTTP ${response.status}`
    };
  } catch (error) {
    return {
      ok: false,
      url,
      error: error instanceof Error ? error.message : "Network request failed"
    };
  } finally {
    clearTimeout(timer);
  }
}
