import { track } from "@/lib/analytics";
import type { PassportStamp } from "@/lib/storage";

export type ShareChannel = "text_web" | "text_fallback";

function buildShareMessage(stamp: PassportStamp): string {
  const earned = new Date(stamp.earnedAt).toLocaleDateString("zh-CN");
  return [
    "Quest English — 面试 Quest 护照印章",
    `任务：${stamp.missionLabel}`,
    `岗位：${stamp.roleLabel}`,
    `就绪度：${stamp.readiness}/100`,
    `获得：${earned}`
  ].join("\n");
}

export async function sharePassportStamp(stamp: PassportStamp): Promise<ShareChannel> {
  const title = "Quest English — 护照印章";
  const text = buildShareMessage(stamp);

  if (typeof navigator.share === "function") {
    try {
      await navigator.share({ title, text });
      void track("passport_share", { channel: "text_web", stampId: stamp.id });
      return "text_web";
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw error;
      }
    }
  }

  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    void track("passport_share", { channel: "text_fallback", stampId: stamp.id });
    return "text_fallback";
  }

  throw new Error("当前浏览器不支持分享或复制");
}
