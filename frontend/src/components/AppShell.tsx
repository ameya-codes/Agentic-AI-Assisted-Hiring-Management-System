import * as React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { api, clearRole, getRole } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";

type JobPick = { id: number; title: string; department: string };

const NAV_BY_ROLE: Record<string, { to: string; label: string }[]> = {
  "Hiring Manager": [
    { to: "dashboard", label: "Overview" },
    { to: "jobs", label: "Requisitions" },
    { to: "screening", label: "Screening" },
    { to: "pipeline", label: "Pipeline" },
    { to: "interviews", label: "Interviews" },
    { to: "offers", label: "Offers" },
    { to: "agents", label: "Agents" },
  ],
  "HR Recruiter": [
    { to: "dashboard", label: "Overview" },
    { to: "jobs", label: "Requisitions" },
    { to: "screening", label: "Screening" },
    { to: "pipeline", label: "Pipeline" },
    { to: "interviews", label: "Interviews" },
    { to: "offers", label: "Offers" },
    { to: "onboarding", label: "Onboarding" },
    { to: "agents", label: "Agents" },
  ],
  Candidate: [
    { to: "dashboard", label: "Overview" },
    { to: "jobs", label: "Open roles" },
  ],
  Interviewer: [
    { to: "dashboard", label: "Overview" },
    { to: "interviews", label: "Feedback" },
    { to: "agents", label: "Agents" },
  ],
};

export function AppShell() {
  const role = getRole()!;
  const nav = NAV_BY_ROLE[role] ?? NAV_BY_ROLE["HR Recruiter"];
  const navigate = useNavigate();
  const isCandidate = role === "Candidate";
  const { activeJobId, setActiveJobId } = useActiveRequisition();
  const [jobPickList, setJobPickList] = React.useState<JobPick[]>([]);

  React.useEffect(() => {
    if (isCandidate) return;
    let cancelled = false;
    (async () => {
      try {
        const list = (await api.get("/api/jobs")) as { id: number; title: string; department: string }[];
        if (cancelled) return;
        setJobPickList(
          list.map((j) => ({ id: j.id, title: j.title, department: j.department || "" })),
        );
        if (list.length === 0) {
          setActiveJobId(null);
          return;
        }
        if (activeJobId == null || !list.some((j) => j.id === activeJobId)) {
          setActiveJobId(list[0].id);
        }
      } catch {
        if (!cancelled) setJobPickList([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isCandidate, activeJobId, setActiveJobId]);

  return (
    <div className="min-h-screen flex bg-slate-100">
      <aside className="w-64 shrink-0 bg-gradient-to-b from-slate-950 to-slate-900 text-slate-200 flex flex-col border-r border-slate-800/80 shadow-xl">
        <div className="p-5 border-b border-white/10">
          <div className="text-[10px] font-semibold tracking-[0.2em] text-indigo-300 uppercase">
            HireFlow AI
          </div>
          <div className="text-lg font-bold text-white tracking-tight mt-1">
            {isCandidate ? "Careers" : "Hiring workspace"}
          </div>
          <p className="text-xs text-slate-400 mt-1 leading-snug">
            {isCandidate
              ? "Browse open roles and apply. Internal hiring tools stay with your recruiting team."
              : "Hiring workspace with human gates"}
          </p>
        </div>
        {!isCandidate && (
          <div className="px-5 pb-4 border-b border-white/10">
            <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block mb-1.5">
              Active requisition
            </label>
            {jobPickList.length === 0 ? (
              <p className="text-xs text-amber-200/90 leading-snug">
                No requisitions yet. Open <strong className="text-white">Requisitions</strong> and publish a role —
                then every screen scopes to that job.
              </p>
            ) : (
              <select
                value={activeJobId ?? ""}
                onChange={(e) => setActiveJobId(Number(e.target.value))}
                className="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-400/40"
              >
                {jobPickList.map((j) => (
                  <option key={j.id} value={j.id} className="text-slate-900">
                    #{j.id} · {j.title}
                  </option>
                ))}
              </select>
            )}
            {jobPickList.length > 0 && activeJobId != null && (
              <p className="text-[11px] text-slate-500 mt-2 leading-snug">
                Dashboard, screening, pipeline, interviews, and offers filter to this position.
              </p>
            )}
          </div>
        )}
        <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "block rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-indigo-500/25 text-white shadow-inner border border-indigo-400/20"
                    : "text-slate-300 hover:bg-white/5 hover:text-white border border-transparent",
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-white/10">
          <div className="text-[10px] uppercase tracking-wider text-slate-500">Active profile</div>
          <div className="text-sm font-semibold text-white mt-0.5">{role}</div>
          <button
            type="button"
            onClick={() => {
              clearRole();
              navigate("/login");
            }}
            className="mt-3 w-full rounded-xl bg-white/10 py-2.5 text-sm font-semibold text-white hover:bg-white/15 border border-white/10 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 min-h-screen overflow-auto">
        <div className="max-w-5xl mx-auto px-6 py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
