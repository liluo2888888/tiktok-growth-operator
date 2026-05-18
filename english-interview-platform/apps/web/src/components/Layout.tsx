import { NavLink, Outlet, useLocation } from "react-router-dom";

import { FlowStep } from "@/components/ui/FlowStep";
import { useFlowIndex } from "@/hooks/useFlowIndex";
import { ui } from "@/lib/copy";

export function Layout() {
  const flowIndex = useFlowIndex();
  const { pathname } = useLocation();
  const pageClass =
    pathname === "/interview"
      ? "page-interview"
      : pathname.startsWith("/passport")
        ? "page-passport"
        : "";

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        {ui.skipLink}
      </a>
      <header className="app-header">
        <div className="app-header-inner">
          <NavLink to="/" className="brand">
            <span className="brand-kicker">{ui.brand.kicker}</span>
            <span className="brand-title">{ui.brand.title}</span>
          </NavLink>
          <div className="header-right">
            <nav className="app-nav" aria-label={ui.nav.main}>
              <NavLink
                to="/quest-map"
                className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              >
                {ui.nav.questMap}
              </NavLink>
              <NavLink
                to="/passport"
                className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              >
                {ui.nav.passport}
              </NavLink>
              <NavLink
                to="/legal"
                className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              >
                {ui.nav.legal}
              </NavLink>
            </nav>
            <FlowStep activeIndex={flowIndex} />
          </div>
        </div>
      </header>
      <main id="main-content" className={`page ${pageClass}`.trim()} tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}
