import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { getRole } from "../api/client";

export function RoleRoute({
  allow,
  children,
}: {
  allow: readonly string[];
  children: ReactNode;
}) {
  const r = getRole();
  if (!r || !allow.includes(r)) return <Navigate to="/app/dashboard" replace />;
  return <>{children}</>;
}
