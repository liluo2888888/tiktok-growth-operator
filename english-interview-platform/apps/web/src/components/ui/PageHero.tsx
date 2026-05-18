import type { ReactNode } from "react";

type PageHeroProps = {
  kicker: string;
  title: string;
  lead?: string;
  aside?: ReactNode;
};

export function PageHero({ kicker, title, lead, aside }: PageHeroProps) {
  return (
    <header className="page-hero">
      <div className="page-hero-main">
        <p className="kicker">{kicker}</p>
        <h1 className="page-title">{title}</h1>
        {lead && <p className="page-lead">{lead}</p>}
      </div>
      {aside && <div className="page-hero-aside">{aside}</div>}
    </header>
  );
}
