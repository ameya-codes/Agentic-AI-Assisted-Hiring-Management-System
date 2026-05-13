import { ACTIVE_REQUISITION_KEY } from "../requisitionStorage";

const base = import.meta.env.VITE_API_URL ?? "";

export function getRole(): string | null {
  return localStorage.getItem("demoRole");
}

export function setRole(role: string): void {
  localStorage.setItem("demoRole", role);
}

const APPLICANT_EMAIL_KEY = "demoApplicantEmail";

export function getApplicantEmail(): string | null {
  return localStorage.getItem(APPLICANT_EMAIL_KEY);
}

export function setApplicantEmail(email: string): void {
  const t = email.trim();
  if (t) localStorage.setItem(APPLICANT_EMAIL_KEY, t);
  else localStorage.removeItem(APPLICANT_EMAIL_KEY);
}

export function clearRole(): void {
  localStorage.removeItem("demoRole");
  localStorage.removeItem(APPLICANT_EMAIL_KEY);
  localStorage.removeItem(ACTIVE_REQUISITION_KEY);
}

async function request(path: string, init?: RequestInit): Promise<unknown> {
  const headers = new Headers(init?.headers);
  if (init?.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const role = getRole();
  if (role) headers.set("X-Demo-Role", role);
  const res = await fetch(`${base}${path}`, { ...init, headers });
  const text = await res.text();
  if (!res.ok) throw new Error(text || res.statusText);
  return text ? JSON.parse(text) : null;
}

export const api = {
  get: (path: string) => request(path),
  post: (path: string, body: unknown) =>
    request(path, { method: "POST", body: JSON.stringify(body) }),
  postForm: (path: string, form: FormData) =>
    request(path, { method: "POST", body: form }),
  patch: (path: string, body: unknown) =>
    request(path, { method: "PATCH", body: JSON.stringify(body) }),
};
