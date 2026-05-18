export type QuestGoal = "job_interview";

export type QuestRole = {
  id: "product" | "general";
  label: string;
  description: string;
};

export type QuestMission = {
  id: "self_intro" | "behavioral";
  label: string;
  subtitle: string;
  durationMinutes: number;
  interviewerLine: string;
};

export const QUEST_PACK = {
  id: "interview",
  title: "Interview Quest Pack",
  description: "Two focused drills for your next English interview."
} as const;

export const GOALS: { id: QuestGoal; label: string; description: string }[] = [
  {
    id: "job_interview",
    label: "Job Interview",
    description: "Practice spoken answers for real hiring conversations."
  }
];

export const ROLES: QuestRole[] = [
  {
    id: "product",
    label: "Product Manager",
    description: "Positioning, tradeoffs, and cross-functional stories."
  },
  {
    id: "general",
    label: "General Professional",
    description: "Broad interview prep when your role is still flexible."
  }
];

export const MISSIONS: QuestMission[] = [
  {
    id: "self_intro",
    label: "Self Introduction",
    subtitle: "Open strong in the first 60 seconds.",
    durationMinutes: 3,
    interviewerLine: "Walk me through your background and why this role fits you."
  },
  {
    id: "behavioral",
    label: "Behavioral Interview",
    subtitle: "Answer with clear situation, action, and result.",
    durationMinutes: 5,
    interviewerLine: "Tell me about a time you handled a difficult stakeholder."
  }
];

export function getRoleById(roleId: string): QuestRole | undefined {
  return ROLES.find((role) => role.id === roleId);
}

export function getMissionById(missionId: string): QuestMission | undefined {
  return MISSIONS.find((mission) => mission.id === missionId);
}
