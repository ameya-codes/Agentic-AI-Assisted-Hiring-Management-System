import * as React from "react";
import { useNavigate } from "react-router-dom";
import { setRole } from "../api/client";

const ROLES = ["Hiring Manager", "HR Recruiter", "Candidate", "Interviewer"] as const;

export function LoginPage() {
  const navigate = useNavigate();
  const [role, setR] = React.useState<(typeof ROLES)[number]>("HR Recruiter");

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-white p-14 flex-col justify-center">
        <p className="text-xs font-semibold tracking-[0.25em] text-indigo-300 uppercase">HireFlow AI</p>
        <h1 className="mt-4 text-4xl font-bold tracking-tight leading-tight max-w-md">
          Agent-assisted hiring with human approval at every critical step.
        </h1>
        <p className="mt-4 text-slate-300 max-w-md leading-relaxed">
          HireFlow AI helps teams draft requisitions, screen resumes, coordinate interviews, summarize feedback,
          and prepare offer language — while recruiters and hiring managers stay in control of decisions, pay, and
          compliance.
        </p>
        <ul className="mt-8 space-y-3 text-sm text-slate-200">
          <li className="flex gap-2">
            <span className="text-indigo-400">✓</span> Role-based workspace (manager, HR, interviewer, candidate
            view)
          </li>
          <li className="flex gap-2">
            <span className="text-indigo-400">✓</span> Works offline with smart mocks, or connect your OpenAI key for
            live language models
          </li>
          <li className="flex gap-2">
            <span className="text-indigo-400">✓</span> One shared hiring database for demos and coursework
          </li>
        </ul>
      </div>
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-card border border-slate-200/80">
          <p className="text-xs font-semibold text-indigo-600 tracking-wide uppercase">HireFlow AI</p>
          <h2 className="mt-1 text-xl font-bold text-slate-900">Sign in</h2>
          <p className="mt-1 text-sm text-slate-500">Classroom / demo — pick a role. No password.</p>
          <label className="mt-6 block text-xs font-semibold uppercase tracking-wide text-slate-500">Role</label>
          <select
            value={role}
            onChange={(e) => setR(e.target.value as (typeof ROLES)[number])}
            className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => {
              setRole(role);
              navigate("/app/dashboard");
            }}
            className="mt-6 w-full rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 hover:bg-indigo-500 transition-colors"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
