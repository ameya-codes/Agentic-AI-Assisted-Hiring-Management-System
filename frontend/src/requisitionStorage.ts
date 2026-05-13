/** localStorage key for the hiring workspace "active requisition" scope. */
export const ACTIVE_REQUISITION_KEY = "hireflowActiveRequisitionId";

export function readStoredRequisitionId(): number | null {
  const raw = localStorage.getItem(ACTIVE_REQUISITION_KEY);
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

export function writeStoredRequisitionId(id: number | null): void {
  if (id == null) localStorage.removeItem(ACTIVE_REQUISITION_KEY);
  else localStorage.setItem(ACTIVE_REQUISITION_KEY, String(id));
}

export function jobScopeQuery(jobId: number | null): string {
  if (jobId == null) return "";
  return `?job_id=${encodeURIComponent(String(jobId))}`;
}
