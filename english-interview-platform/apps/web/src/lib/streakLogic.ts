export type StreakState = {
  streakCount: number;
  lastCompletedDate: string | null;
};

export type StreakSummary = StreakState & {
  todayCompleted: boolean;
};

export function utcDateKey(date: Date = new Date()): string {
  return date.toISOString().slice(0, 10);
}

export function previousUtcDateKey(date: Date = new Date()): string {
  const copy = new Date(date.getTime());
  copy.setUTCDate(copy.getUTCDate() - 1);
  return utcDateKey(copy);
}

export function applyQuestCompletion(state: StreakState, today: string): StreakSummary {
  if (state.lastCompletedDate === today) {
    return {
      streakCount: state.streakCount,
      lastCompletedDate: state.lastCompletedDate,
      todayCompleted: true
    };
  }

  const yesterday = previousUtcDateKey(new Date(`${today}T12:00:00.000Z`));
  let streakCount = 1;

  if (state.lastCompletedDate === yesterday) {
    streakCount = Math.max(1, state.streakCount + 1);
  }

  return {
    streakCount,
    lastCompletedDate: today,
    todayCompleted: true
  };
}

export function readStreakSummary(state: StreakState, today: string): StreakSummary {
  const todayCompleted = state.lastCompletedDate === today;
  let streakCount = state.streakCount;

  if (!todayCompleted && state.lastCompletedDate) {
    const yesterday = previousUtcDateKey(new Date(`${today}T12:00:00.000Z`));
    if (state.lastCompletedDate !== yesterday) {
      streakCount = 0;
    }
  }

  return {
    streakCount,
    lastCompletedDate: state.lastCompletedDate,
    todayCompleted
  };
}

export function isStreakAtRisk(summary: StreakSummary, today: string): boolean {
  if (summary.todayCompleted || summary.streakCount === 0 || !summary.lastCompletedDate) {
    return false;
  }
  const yesterday = previousUtcDateKey(new Date(`${today}T12:00:00.000Z`));
  return summary.lastCompletedDate === yesterday;
}

const WEEKDAY_ZH = ["日", "一", "二", "三", "四", "五", "六"] as const;

export type StreakWeekMark = {
  dateKey: string;
  weekdayLabel: string;
  done: boolean;
  today: boolean;
};

export function getStreakWeekMarks(history: string[], today: string): StreakWeekMark[] {
  const doneSet = new Set(history);
  const marks: StreakWeekMark[] = [];

  for (let offset = 6; offset >= 0; offset -= 1) {
    const date = new Date(`${today}T12:00:00.000Z`);
    date.setUTCDate(date.getUTCDate() - offset);
    const dateKey = utcDateKey(date);
    marks.push({
      dateKey,
      weekdayLabel: WEEKDAY_ZH[date.getUTCDay()],
      done: doneSet.has(dateKey),
      today: dateKey === today
    });
  }

  return marks;
}
