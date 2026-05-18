/** 界面中文文案（面试题目与作答内容仍为英文） */

export const ui = {
  brand: {
    kicker: "Quest English",
    title: "英文面试 Quest 包"
  },
  skipLink: "跳到主要内容",
  nav: {
    main: "主导航",
    questMap: "任务地图",
    passport: "护照",
    legal: "法律与隐私"
  },
  flow: ["设置", "任务", "练习", "反馈", "护照"] as const,
  api: {
    checking: "正在检查 API…",
    connected: "API 已连接",
    offline: "API 未连接"
  },
  common: {
    retry: "重试",
    back: "返回",
    next: "下一步",
    minWords: (n: number) => `至少 ${n} 个英文单词`,
    words: (n: number) => `${n} 个单词`,
    minutes: (n: number) => `约 ${n} 分钟`,
    session: (id: string) => `会话 ${id}`,
    turn: (n: number) => `第 ${n} 轮`,
    stage: (s: string) => `阶段 · ${s}`,
    earnedAt: (date: string) => `获得于 ${date}`,
    track: (role: string) => `赛道：${role}`,
    jobInterviewTrack: "求职面试赛道"
  },
  errors: {
    generic: "出了点问题",
    startSession: "无法启动练习会话",
    submit: "提交失败",
    load: "加载失败",
    loadFeedback: "无法加载反馈"
  },
  status: {
    notStarted: "未开始",
    inProgress: "进行中",
    completed: "已完成"
  },
  scores: {
    readiness: "面试就绪度",
    readinessOf: (n: number) => `面试就绪度：${n} / 100`,
    clarity: "清晰度",
    structure: "结构",
    confidence: "自信度",
    relevance: "相关性",
    breakdown: "得分明细",
    ready: "就绪"
  },
  stages: {
    opening: "开场",
    closing: "收尾",
    behavioral: "行为面",
    followup: "追问"
  } as Record<string, string>
} as const;

export function stageLabel(stage: string) {
  return ui.stages[stage] ?? stage;
}
