import type { MissionStatus } from "@/storage/userProfile";

export function missionStatusLabel(status: MissionStatus): string {
  switch (status) {
    case "completed":
      return "Completed";
    case "in_progress":
      return "In progress";
    default:
      return "Not started";
  }
}
