export type QuestGoal = "job_interview";
export type RoleId = "product" | "general";
export type MissionId = "self_intro" | "behavioral";
export type MissionStatus = "not_started" | "in_progress" | "completed";

export const QUEST_PACK = {
  id: "interview",
  title: "英文面试 Quest 包",
  description: "为下一次英文面试准备的两组高强度短练。"
} as const;

export const GOALS = [
  {
    id: "job_interview" as const,
    label: "求职面试",
    description: "针对真实招聘场景练习英文口语回答。"
  }
];

export const ROLES = [
  {
    id: "product" as const,
    label: "产品经理",
    description: "定位、权衡与跨团队协作类故事。"
  },
  {
    id: "general" as const,
    label: "通用职场",
    description: "岗位尚未完全确定时的广谱面试准备。"
  }
];

export const MISSIONS = [
  {
    id: "self_intro" as const,
    label: "自我介绍",
    subtitle: "在前 60 秒建立清晰、有记忆点的开场。",
    durationMinutes: 3,
    interviewerLine: "Walk me through your background and why this role fits you."
  },
  {
    id: "behavioral" as const,
    label: "行为面试",
    subtitle: "用情境、行动、结果（STAR）组织回答。",
    durationMinutes: 5,
    interviewerLine: "Tell me about a time you handled a difficult stakeholder."
  }
];

export function getRole(roleId: string) {
  return ROLES.find((r) => r.id === roleId);
}

export function getMission(missionId: string) {
  return MISSIONS.find((m) => m.id === missionId);
}
