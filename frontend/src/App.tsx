import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { getRole } from "./api/client";
import { AppShell } from "./components/AppShell";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { JobsPage } from "./pages/JobsPage";
import { PipelinePage } from "./pages/PipelinePage";
import { ScreeningPage } from "./pages/ScreeningPage";
import { InterviewsPage } from "./pages/InterviewsPage";
import { OffersPage } from "./pages/OffersPage";
import { OnboardingPage } from "./pages/OnboardingPage";
import { AgentsPage } from "./pages/AgentsPage";
import { RoleRoute } from "./components/RoleRoute";
import { RequisitionProvider } from "./context/RequisitionContext";

function RequireAuth({ children }: { children: ReactNode }) {
  if (!getRole()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/app"
        element={
          <RequireAuth>
            <RequisitionProvider>
              <AppShell />
            </RequisitionProvider>
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route
          path="screening"
          element={
            <RoleRoute allow={["HR Recruiter", "Hiring Manager"]}>
              <ScreeningPage />
            </RoleRoute>
          }
        />
        <Route
          path="pipeline"
          element={
            <RoleRoute allow={["HR Recruiter", "Hiring Manager"]}>
              <PipelinePage />
            </RoleRoute>
          }
        />
        <Route
          path="interviews"
          element={
            <RoleRoute allow={["HR Recruiter", "Hiring Manager", "Interviewer"]}>
              <InterviewsPage />
            </RoleRoute>
          }
        />
        <Route
          path="offers"
          element={
            <RoleRoute allow={["HR Recruiter", "Hiring Manager"]}>
              <OffersPage />
            </RoleRoute>
          }
        />
        <Route
          path="onboarding"
          element={
            <RoleRoute allow={["HR Recruiter", "Hiring Manager"]}>
              <OnboardingPage />
            </RoleRoute>
          }
        />
        <Route
          path="agents"
          element={
            <RoleRoute allow={["HR Recruiter", "Hiring Manager", "Interviewer"]}>
              <AgentsPage />
            </RoleRoute>
          }
        />
      </Route>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
