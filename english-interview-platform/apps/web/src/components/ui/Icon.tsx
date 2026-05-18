import type { ReactNode, SVGAttributes } from "react";

export type IconName =
  | "flame"
  | "passport"
  | "arrowRight"
  | "map"
  | "check"
  | "mic"
  | "target"
  | "sparkles"
  | "stamp";

type IconProps = SVGAttributes<SVGSVGElement> & {
  name: IconName;
  size?: number;
  label?: string;
};

const paths: Record<IconName, ReactNode> = {
  flame: (
    <>
      <path d="M12 22c4-2.5 7-6.5 7-11a7 7 0 0 0-14 0c0 4.5 3 8.5 7 11Z" />
      <path d="M12 13c1.2-1.5 2-3.2 2-5.5a3.5 3.5 0 0 0-7 0c0 2.3.8 4 2 5.5" />
    </>
  ),
  passport: (
    <>
      <rect x="4" y="3" width="16" height="18" rx="2" />
      <circle cx="12" cy="10" r="2.5" />
      <path d="M8 16h8" />
    </>
  ),
  arrowRight: (
    <>
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </>
  ),
  map: (
    <>
      <path d="M3 6 9 4 15 6 21 4v14l-6 2-6-2-6 2V6Z" />
      <path d="M9 4v14" />
      <path d="M15 6v14" />
    </>
  ),
  check: <path d="M20 6 9 17l-5-5" />,
  mic: (
    <>
      <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3Z" />
      <path d="M19 11a7 7 0 0 1-14 0" />
      <path d="M12 18v3" />
    </>
  ),
  target: (
    <>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </>
  ),
  sparkles: (
    <>
      <path d="m9 3 1.2 3.6L14 8l-3.6 1.2L9 13l-1.2-3.8L4 8l3.8-1.2L9 3Z" />
      <path d="m17 14 1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3Z" />
    </>
  ),
  stamp: (
    <>
      <path d="M5 21V7l7-4 7 4v14" />
      <path d="M9 21v-6h6v6" />
      <path d="M9 11h6" />
    </>
  )
};

export function Icon({ name, size = 20, label, className = "", ...props }: IconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`icon ${className}`.trim()}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? "img" : undefined}
      {...props}
    >
      {paths[name]}
    </svg>
  );
}
