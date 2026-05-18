import { Link } from "react-router-dom";

import { Icon } from "./Icon";

type MissionTileProps = {
  to: string;
  label: string;
  subtitle: string;
  durationMinutes: number;
  statusLabel: string;
  index: number;
};

export function MissionTile({
  to,
  label,
  subtitle,
  durationMinutes,
  statusLabel,
  index
}: MissionTileProps) {
  return (
    <Link to={to} className="mission-tile" style={{ textDecoration: "none", color: "inherit" }}>
      <span className="mission-tile-index">{String(index + 1).padStart(2, "0")}</span>
      <div className="mission-tile-body">
        <h3>{label}</h3>
        <p>{subtitle}</p>
        <div className="mission-tile-meta">
          <span>约 {durationMinutes} 分钟</span>
          <span className="status-pill">{statusLabel}</span>
        </div>
      </div>
      <span className="mission-tile-arrow" aria-hidden>
        <Icon name="arrowRight" size={18} />
      </span>
    </Link>
  );
}
