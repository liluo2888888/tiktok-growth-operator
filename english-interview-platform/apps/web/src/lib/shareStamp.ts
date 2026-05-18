import { track } from "@/lib/analytics";
import { renderStampPosterPng } from "@/lib/renderStampPosterPng";
import type { PassportStamp } from "@/lib/storage";

export type ShareChannel = "image" | "text_web" | "text_fallback";

export type ShareResult = {
  channel: ShareChannel;
  posterDownloaded: boolean;
};

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

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function sharePassportStamp(stamp: PassportStamp): Promise<ShareResult> {
  const title = "Quest English — 护照印章";
  const text = buildShareMessage(stamp);
  const { blob, filename } = await renderStampPosterPng(stamp);
  const file = new File([blob], filename, { type: "image/png" });

  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ title, text, files: [file] });
      void track("passport_share", { channel: "image", stampId: stamp.id });
      return { channel: "image", posterDownloaded: false };
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw error;
      }
    }
  }

  downloadBlob(blob, filename);

  if (typeof navigator.share === "function") {
    try {
      await navigator.share({ title, text });
      void track("passport_share", { channel: "text_web", stampId: stamp.id });
      return { channel: "text_web", posterDownloaded: true };
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw error;
      }
    }
  }

  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    void track("passport_share", { channel: "text_fallback", stampId: stamp.id });
    return { channel: "text_fallback", posterDownloaded: true };
  }

  void track("passport_share", { channel: "image", stampId: stamp.id });
  return { channel: "image", posterDownloaded: true };
}

export function shareResultHint(result: ShareResult): string | null {
  if (result.channel === "image" && !result.posterDownloaded) {
    return null;
  }
  if (result.channel === "image") {
    return "分享海报已保存为 PNG。";
  }
  if (result.channel === "text_web") {
    return "海报已下载，并已打开系统分享。";
  }
  return "海报已下载，分享文案已复制到剪贴板。";
}
