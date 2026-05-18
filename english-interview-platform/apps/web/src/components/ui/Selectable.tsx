type SelectableProps = {
  title: string;
  description: string;
  selected?: boolean;
  badge?: string;
  onClick?: () => void;
};

export function Selectable({ title, description, selected, badge, onClick }: SelectableProps) {
  return (
    <button
      type="button"
      className={selected ? "selectable selected" : "selectable"}
      onClick={onClick}
      aria-pressed={selected}
    >
      <div className="selectable-title">
        {title}
        {badge && <span className="badge">{badge}</span>}
      </div>
      <div className="selectable-desc">{description}</div>
    </button>
  );
}
