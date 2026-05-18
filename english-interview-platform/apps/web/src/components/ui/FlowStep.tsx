import { ui } from "@/lib/copy";

type FlowStepProps = {
  activeIndex: number;
};

export function FlowStep({ activeIndex }: FlowStepProps) {
  return (
    <ol className="flow-step" aria-label="练习流程">
      {ui.flow.map((label, index) => (
        <li key={label} className={index <= activeIndex ? "active" : undefined}>
          <span className="flow-step-dot" />
          <span className="flow-step-label">{label}</span>
        </li>
      ))}
    </ol>
  );
}
