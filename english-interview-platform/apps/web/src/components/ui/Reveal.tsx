import type { ReactNode } from "react";

type RevealProps = {
  children: ReactNode;
  className?: string;
  stagger?: boolean;
};

/** Staggered entrance — respects prefers-reduced-motion via global.css */
export function Reveal({ children, className = "", stagger = false }: RevealProps) {
  return (
    <div className={`reveal ${stagger ? "reveal-stagger" : ""} ${className}`.trim()}>
      {children}
    </div>
  );
}
