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
  if (readiness >= 80) {
    return "Interview ready";
  }
  if (readiness >= 60) {
    return "Building momentum";
  }
  return "Keep practicing";
}

export function buildShareMessage(stamp: {
  missionLabel: string;
  roleLabel: string;
  readiness: number;
  earnedAt: string;
}): string {
  return [
    "Quest English — Interview Quest Pack",
    `Mission: ${stamp.missionLabel}`,
    `Role: ${stamp.roleLabel}`,
    `Readiness: ${stamp.readiness}/100`,
    `Earned: ${new Date(stamp.earnedAt).toLocaleDateString()}`
  ].join("\n");
}
