import * as React from "react";
import { api } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { jobScopeQuery } from "../requisitionStorage";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Row = Record<string, unknown>;

const STATUSES = [
  "New",
  "Shortlisted",
  "Interview Scheduled",
  "Interview Completed",
  "Offer Generated",
  "Onboarded",
  "Rejected",
];

export function PipelinePage() {
  const { activeJobId } = useActiveRequisition();
  const [rows, setRows] = React.useState<Row[]>([]);
  const [pick, setPick] = React.useState<number | null>(null);
  const [status, setStatus] = React.useState("New");

  const load = React.useCallback(async () => {
    const q = jobScopeQuery(activeJobId);
    setRows((await api.get(`/api/candidates/ranked${q}`)) as Row[]);
  }, [activeJobId]);

  React.useEffect(() => {
    load().catch(() => {});
  }, [load]);

  React.useEffect(() => {
    if (rows.length && pick === null) {
      setPick(Number(rows[0].candidate_id));
      setStatus(String(rows[0].status));
    }
  }, [rows, pick]);

  return (
    <>
      <PageTitle
        kicker="Recruiting operations"
        title="Candidate pipeline"
        subtitle="Ranked candidates for the active requisition only — switch jobs in the sidebar to change scope."
      />
      <PocStrip />
      {rows.length === 0 ? (
        <Card>
          <p className="text-sm text-slate-500">No candidates yet.</p>
        </Card>
      ) : (
        <>
      <Card>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
          Ranked candidates
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100">
                <th className="pb-2 pr-3">#</th>
                <th className="pb-2 pr-3">Candidate</th>
                <th className="pb-2 pr-3">Role</th>
                <th className="pb-2 pr-3">Match</th>
                <th className="pb-2 pr-3">AI rec</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={String(r.candidate_id)} className="border-b border-slate-50 last:border-0">
                  <td className="py-2.5 pr-3 text-slate-500">{String(r.rank)}</td>
                  <td className="py-2.5 pr-3 font-medium text-slate-900">{String(r.name)}</td>
                  <td className="py-2.5 pr-3 text-slate-600">{String(r.job_title)}</td>
                  <td className="py-2.5 pr-3 tabular-nums font-semibold text-indigo-600">{String(r.match_score)}</td>
                  <td className="py-2.5 pr-3 text-slate-600">{String(r.recommendation)}</td>
                  <td className="py-2.5">
                    <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
                      {String(r.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
      <Card className="mt-6">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
          Update status
        </h3>
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="text-xs font-semibold text-slate-500">Candidate</label>
            <select
              value={pick ?? ""}
              onChange={(e) => {
                const id = Number(e.target.value);
                setPick(id);
                const row = rows.find((x) => Number(x.candidate_id) === id);
                if (row) setStatus(String(row.status));
              }}
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            >
              {rows.map((r) => (
                <option key={String(r.candidate_id)} value={String(r.candidate_id)}>
                  {String(r.name)} · {String(r.job_title)}
                </option>
              ))}
            </select>
          </div>
          <div className="w-48">
            <label className="text-xs font-semibold text-slate-500">New status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            disabled={pick === null}
            onClick={async () => {
              if (pick === null) return;
              await api.patch(`/api/candidates/${pick}/status`, { status });
              load();
            }}
            className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            Apply
          </button>
        </div>
      </Card>
        </>
      )}
    </>
  );
}
