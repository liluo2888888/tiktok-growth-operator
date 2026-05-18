import { ui } from "@/lib/copy";

type ReadinessHeroProps = {
  readiness: number;
  label?: string;
};

export function ReadinessHero({
  readiness,
  label = ui.scores.readiness
}: ReadinessHeroProps) {
  return (
    <div
      className="readiness-hero"
      role="img"
      aria-label={ui.scores.readinessOf(readiness)}
    >
      <p className="readiness-hero-label">{label}</p>
      <p className="readiness-hero-value">{readiness}</p>
      <div className="readiness-hero-bar">
        <span style={{ width: `${Math.min(100, Math.max(0, readiness))}%` }} />
      </div>
    </div>
  );
}
