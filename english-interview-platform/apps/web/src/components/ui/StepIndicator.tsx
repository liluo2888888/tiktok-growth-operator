type StepIndicatorProps = {
  current: number;
  total: number;
  labels?: string[];
};

export function StepIndicator({ current, total, labels }: StepIndicatorProps) {
  return (
    <ol className="step-indicator" aria-label={`第 ${current} 步，共 ${total} 步`}>
      {Array.from({ length: total }, (_, i) => {
        const step = i + 1;
        const state =
          step < current ? "done" : step === current ? "active" : "upcoming";
        return (
          <li key={step} className={state}>
            <span className="step-indicator-dot" aria-hidden />
            {labels?.[i] && <span className="step-indicator-label">{labels[i]}</span>}
          </li>
        );
      })}
    </ol>
  );
}
