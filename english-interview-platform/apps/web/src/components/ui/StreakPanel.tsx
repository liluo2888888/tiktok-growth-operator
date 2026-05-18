import { ButtonLink } from "./Button";
import { Icon } from "./Icon";

type StreakPanelProps = {
  streakCount: number;
  todayCompleted: boolean;
  ctaLabel: string;
  ctaTo: string;
  hint: string;
};

export function StreakPanel({
  streakCount,
  todayCompleted,
  ctaLabel,
  ctaTo,
  hint
}: StreakPanelProps) {
  return (
    <aside className="streak-panel" aria-label="每日连续练习">
      <div className="streak-panel-top">
        <div className="streak-panel-flame" aria-hidden>
          <Icon name="flame" size={26} />
        </div>
        <div>
          <p className="streak-panel-count">{streakCount}</p>
          <p className="streak-panel-label">天连续</p>
        </div>
        <span className={`streak-panel-badge ${todayCompleted ? "done" : "open"}`}>
          {todayCompleted ? "今日已完成" : "今日待完成"}
        </span>
      </div>
      <p className="streak-panel-hint">{hint}</p>
      {!todayCompleted && (
        <ButtonLink to={ctaTo} variant="primary">
          {ctaLabel}
        </ButtonLink>
      )}
    </aside>
  );
}
