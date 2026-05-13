import * as React from "react";
import { api, getApplicantEmail, getRole } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { jobScopeQuery } from "../requisitionStorage";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type ActiveReq = {
  id: number;
  title: string;
  department: string;
  location: string;
  status: string;
};

type PipelineRow = { status: string; count: number };

type RequisitionRow = {
  id: number;
  title: string;
  status: string;
  department: string;
  location: string;
  applicant_count: number;
};

type InternalDashboard = {
  open_jobs: number;
  total_candidates: number;
  shortlisted: number;
  interviews: number;
  offers: number;
  pipeline: PipelineRow[];
  requisitions?: RequisitionRow[];
  active_requisition?: ActiveReq | null;
};

type CareerApp = {
  id: number;
  job_title: string;
  status: string;
  applied_at: string;
};

type CareerOverview = {
  open_roles: number;
  applications: CareerApp[];
};

export function DashboardPage() {
  const role = getRole();
  const isCandidate = role === "Candidate";
  const showRequisitions = role === "Hiring Manager" || role === "HR Recruiter";
  const { activeJobId } = useActiveRequisition();

  const [data, setData] = React.useState<InternalDashboard | null>(null);
  const [career, setCareer] = React.useState<CareerOverview | null>(null);
  const [audit, setAudit] = React.useState<Record<string, unknown>[]>([]);
  const [err, setErr] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      try {
        if (isCandidate) {
          const email = getApplicantEmail() ?? "";
          const c = (await api.get(
            `/api/careers/overview?email=${encodeURIComponent(email)}`,
          )) as CareerOverview;
          setCareer(c);
        } else {
          const q = jobScopeQuery(activeJobId);
          const d = (await api.get(`/api/dashboard${q}`)) as InternalDashboard;
          setData(d);
          setAudit((await api.get("/api/audit")) as Record<string, unknown>[]);
        }
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Failed to load");
      }
    })();
  }, [isCandidate, activeJobId]);

  if (err) {
    return (
      <Card>
        <p className="text-red-600 text-sm">{err}</p>
        <p className="text-slate-500 text-sm mt-2">Start the API: uvicorn api.main:app --reload --port 8000</p>
      </Card>
    );
  }

  if (isCandidate) {
    if (!career) return <p className="text-slate-500">Loading…</p>;
    return (
      <>
        <PageTitle
          kicker="Careers"
          title="Your HireFlow careers home"
          subtitle="Open roles only — no internal hiring metrics or audit data are shown here."
        />
        <PocStrip />
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <div className="rounded-2xl bg-white border border-slate-200/90 p-5 shadow-card relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-violet-500" />
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Open roles</div>
            <div className="mt-2 text-3xl font-bold text-slate-900 tracking-tight">{career.open_roles}</div>
          </div>
          <div className="rounded-2xl bg-white border border-slate-200/90 p-5 shadow-card relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500" />
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Your applications</div>
            <div className="mt-2 text-3xl font-bold text-slate-900 tracking-tight">{career.applications.length}</div>
            <p className="text-xs text-slate-500 mt-2">
              We match applications by the email you use when you apply. Same email next visit shows your history.
            </p>
          </div>
        </div>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Roles you applied to
          </h3>
          {career.applications.length === 0 ? (
            <p className="text-sm text-slate-600">
              No applications yet. Go to <strong>Open roles</strong>, pick a position, and submit your résumé (PDF or
              Word). Our recruiting team and AI-assisted screening receive your profile; a human still makes decisions.
            </p>
          ) : (
            <div className="space-y-2">
              {career.applications.map((a) => (
                <div
                  key={String(a.id)}
                  className="flex flex-wrap justify-between gap-2 rounded-xl bg-slate-50 px-4 py-3 text-sm"
                >
                  <span className="font-medium text-slate-800">{a.job_title}</span>
                  <span className="text-slate-500">{a.status}</span>
                  <span className="text-xs text-slate-400 w-full sm:w-auto">{a.applied_at}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
        <p className="text-xs text-slate-500 mt-6 max-w-2xl leading-relaxed">
          Production systems often sync applications from Workday, Greenhouse, or other ATS via API so hiring managers
          see the same pipeline on an internal dashboard. This POC stores everything in SQLite and surfaces it to
          recruiters under Screening and Pipeline.
        </p>
      </>
    );
  }

  if (!data) return <p className="text-slate-500">Loading…</p>;

  return (
    <>
      <PageTitle
        kicker="Dashboard"
        title="Overview"
        subtitle={
          data.active_requisition
            ? `Numbers below are for requisition #${data.active_requisition.id} only. Change position in the sidebar.`
            : "Pipeline snapshot and recent audit events — shared hiring database."
        }
      />
      <PocStrip />
      {data.active_requisition && (
        <div className="mb-6 rounded-2xl border border-indigo-200 bg-indigo-50/90 px-4 py-3 text-sm text-indigo-950">
          <span className="font-semibold">Active requisition:</span>{" "}
          <span className="font-bold">{data.active_requisition.title}</span> ·{" "}
          {data.active_requisition.department} · {data.active_requisition.location} · Status:{" "}
          {data.active_requisition.status}
        </div>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {(data.active_requisition
          ? [
              ["Applicants", data.total_candidates],
              ["Shortlisted", data.shortlisted],
              ["Interviews", data.interviews],
              ["Offers", data.offers],
            ]
          : [
              ["Open roles", data.open_jobs],
              ["Candidates", data.total_candidates],
              ["Shortlisted", data.shortlisted],
              ["Interviews", data.interviews],
              ["Offers", data.offers],
            ]
        ).map(([label, val]) => (
          <div
            key={String(label)}
            className="rounded-2xl bg-white border border-slate-200/90 p-5 shadow-card relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-violet-500" />
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">{label}</div>
            <div className="mt-2 text-3xl font-bold text-slate-900 tracking-tight">{val as number}</div>
          </div>
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Pipeline by stage
          </h3>
          <div className="space-y-2">
            {data.pipeline.length === 0 ? (
              <p className="text-sm text-slate-500">No candidates yet.</p>
            ) : (
              data.pipeline.map((row) => (
                <div
                  key={row.status}
                  className="flex justify-between items-center rounded-xl bg-slate-50 px-4 py-3 text-sm"
                >
                  <span className="font-medium text-slate-800">{row.status}</span>
                  <span className="tabular-nums font-semibold text-indigo-600">{row.count}</span>
                </div>
              ))
            )}
          </div>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Audit trail
          </h3>
          <div className="max-h-72 overflow-y-auto space-y-2 text-xs">
            {audit.slice(0, 12).map((row) => (
              <div key={String(row.id)} className="rounded-lg bg-slate-50 px-3 py-2 text-slate-600">
                <span className="font-semibold text-slate-800">{String(row.action)}</span> ·{" "}
                {String(row.user_role)} · {String(row.details ?? "")}
              </div>
            ))}
          </div>
        </Card>
      </div>
      {showRequisitions && (data.requisitions ?? []).length > 0 && (
        <Card className="mt-6">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Requisitions & status
          </h3>
          <p className="text-sm text-slate-600 mb-4">
            Hiring managers open and track requisitions here; applicant counts flow in as candidates apply from the
            careers portal or recruiter screening.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100">
                  <th className="pb-2 pr-4">Title</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Team</th>
                  <th className="pb-2 pr-4">Location</th>
                  <th className="pb-2">Applicants</th>
                </tr>
              </thead>
              <tbody>
                {(data.requisitions ?? []).map((r) => (
                  <tr key={r.id} className="border-b border-slate-50 last:border-0">
                    <td className="py-3 pr-4 font-medium text-slate-900">{r.title}</td>
                    <td className="py-3 pr-4 text-slate-600">{r.status}</td>
                    <td className="py-3 pr-4 text-slate-600">{r.department}</td>
                    <td className="py-3 pr-4 text-slate-600">{r.location}</td>
                    <td className="py-3 tabular-nums text-slate-800">{r.applicant_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </>
  );
}
