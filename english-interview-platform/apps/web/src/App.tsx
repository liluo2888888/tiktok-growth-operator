import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "@/components/Layout";
import { FeedbackPage } from "@/pages/FeedbackPage";
import { HomePage } from "@/pages/HomePage";
import { InterviewPage } from "@/pages/InterviewPage";
import { LegalPage } from "@/pages/LegalPage";
import { OnboardingPage } from "@/pages/OnboardingPage";
import { PassportDetailPage } from "@/pages/PassportDetailPage";
import { PassportPage } from "@/pages/PassportPage";
import { QuestMapPage } from "@/pages/QuestMapPage";
import { QuestStartPage } from "@/pages/QuestStartPage";

export default function App() {
  return (
    <Routes>
      <Route path="/onboarding" element={<OnboardingPage />} />
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/quest-map" element={<QuestMapPage />} />
        <Route path="/quest-start" element={<QuestStartPage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/feedback" element={<FeedbackPage />} />
        <Route path="/passport" element={<PassportPage />} />
        <Route path="/passport/:id" element={<PassportDetailPage />} />
        <Route path="/legal" element={<LegalPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
