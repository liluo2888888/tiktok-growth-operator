import type { PassportStamp } from "@/lib/storage";

export const SHARE_POSTER_SIZE = 360;

export function missionStampEmoji(missionId: string): string {
  switch (missionId) {
    case "self_intro":
      return "🎯";
    case "behavioral":
      return "💬";
    default:
      return "🛂";
  }
}

export function readinessTier(readiness: number): string {
  if (readiness >= 80) return "面试就绪";
  if (readiness >= 60) return "稳步提升";
  return "继续加油";
}

export function formatStampDate(iso: string): string {
  return new Date(iso).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });
}

export function stampPosterFilename(stamp: PassportStamp): string {
  const slug = stamp.missionId.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
  return `quest-english-stamp-${slug}.png`;
}
