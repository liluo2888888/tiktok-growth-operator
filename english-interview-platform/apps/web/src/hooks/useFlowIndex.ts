import { useLocation } from "react-router-dom";

export function useFlowIndex(): number {
  const { pathname } = useLocation();
  if (pathname.startsWith("/onboarding")) return 0;
  if (pathname.startsWith("/quest")) return 1;
  if (pathname.startsWith("/interview")) return 2;
  if (pathname.startsWith("/feedback")) return 3;
  if (pathname.startsWith("/passport")) return 4;
  return 0;
}
