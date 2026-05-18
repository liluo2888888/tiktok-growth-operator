import type { StreakWeekMark } from "@/lib/streakLogic";

import { ButtonLink } from "./Button";
import { Icon } from "./Icon";

type StreakPanelProps = {
  streakCount: number;
  todayCompleted: boolean;
  atRisk?: boolean;
  taskTitle: string;
  taskBody: string;
  weekMarks?: StreakWeekMark[];
  ctaLabel?: string;
  ctaTo?: string;
  compact?: boolean;
};

export function StreakPanel({
  streakCount,
  todayCompleted,
  atRisk = false,
  taskTitle,
  taskBody,
  weekMarks = [],
  ctaLabel,
  ctaTo,
  compact = false
}: StreakPanelProps) {
  return (
    <aside
      className={`streak-panel${compact ? " streak-panel-compact" : ""}${atRisk ? " streak-panel-at-risk" : ""}`}
      aria-label="每日连续练习"
    >
      <div className="streak-panel-top">
        <div className="streak-panel-flame" aria-hidden>
          <Icon name="flame" size={compact ? 22 : 26} />
        </div>
        <div>
          <p className="streak-panel-count">{streakCount}</p>
          <p className="streak-panel-label">天连续</p>
        </div>
        <span className={`streak-panel-badge ${todayCompleted ? "done" : "open"}`}>
          {todayCompleted ? "今日已完成" : "今日待完成"}
        </span>
      </div>

      {weekMarks.length > 0 && (
        <div className="streak-week" aria-label="近 7 天练习记录">
          {weekMarks.map((mark) => (
            <div
              key={mark.dateKey}
              className={`streak-week-day${mark.done ? " done" : ""}${mark.today ? " today" : ""}`}
            >
              <span className="streak-week-dot" aria-hidden />
              <span className="streak-week-label">{mark.weekdayLabel}</span>
            </div>
          ))}
        </div>
      )}

      {atRisk && (
        <p className="streak-panel-risk" role="status">
          今天还没练——连续记录今晚截止，快来完成一轮。
        </p>
      )}

      <p className="streak-panel-task-title">{taskTitle}</p>
      <p className="streak-panel-hint">{taskBody}</p>

      {!todayCompleted && ctaLabel && ctaTo && (
        <ButtonLink to={ctaTo} variant="primary">
          {ctaLabel}
        </ButtonLink>
      )}
    </aside>
  );
}
