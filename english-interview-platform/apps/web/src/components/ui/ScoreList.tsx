import { ui } from "@/lib/copy";

type ScoreListProps = {
  scores: {
    clarity: number;
    structure: number;
    confidence: number;
    relevance: number;
    readiness: number;
  };
};

export function ScoreList({ scores }: ScoreListProps) {
  const rows = [
    [ui.scores.clarity, scores.clarity],
    [ui.scores.structure, scores.structure],
    [ui.scores.confidence, scores.confidence],
    [ui.scores.relevance, scores.relevance]
  ] as const;

  return (
    <ul className="score-list">
      {rows.map(([label, value]) => (
        <li key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </li>
      ))}
    </ul>
  );
}
