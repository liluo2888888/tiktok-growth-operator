import type { ReactNode } from "react";

type PanelProps = {
  title?: string;
  children: ReactNode;
  className?: string;
  variant?: "default" | "inset" | "highlight";
};

export function Panel({ title, children, className = "", variant = "default" }: PanelProps) {
  return (
    <section className={`panel panel-${variant} ${className}`.trim()}>
      {title && <h2 className="panel-title">{title}</h2>}
      {children}
    </section>
  );
}
