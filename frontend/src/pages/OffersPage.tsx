import * as React from "react";
import { api, getRole } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { jobScopeQuery } from "../requisitionStorage";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Pool = { id: number; name: string; job_title: string; hire_decision: string };
type Offer = {
  id: number;
  candidate_id: number;
  candidate_name: string;
  salary: number;
  approval_status: string;
  start_date: string;
  job_title: string;
};

const STATUSES = ["Draft", "Pending HR Approval", "Approved", "Sent"];

export function OffersPage() {
  const role = getRole();
  const { activeJobId } = useActiveRequisition();
  const [pool, setPool] = React.useState<Pool[]>([]);
  const [offers, setOffers] = React.useState<Offer[]>([]);
  const [cid, setCid] = React.useState<number | "">("");
  const [salary, setSalary] = React.useState(125000);
  const [start, setStart] = React.useState("2026-06-16");
  const [title, setTitle] = React.useState("");
  const [mgr, setMgr] = React.useState("Alex Rivera — Engineering Manager");

  const load = React.useCallback(async () => {
    const q = jobScopeQuery(activeJobId);
    setPool((await api.get(`/api/offers/eligible-candidates${q}`)) as Pool[]);
    setOffers((await api.get(`/api/offers${q}`)) as Offer[]);
  }, [activeJobId]);

  React.useEffect(() => {
    load().catch(() => {});
  }, [load]);

  React.useEffect(() => {
    if (pool.length && cid === "") {
      setCid(pool[0].id);
      setTitle(pool[0].job_title);
    }
  }, [pool, cid]);

  return (
    <>
      <PageTitle
        kicker="Total rewards"
        title="Offers & approvals"
        subtitle="Eligible candidates and offer records are scoped to the active requisition in the sidebar."
      />
      <PocStrip />
      {role === "HR Recruiter" && pool.length > 0 ? (
        <Card className="mb-6">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            New offer
          </h3>
          <div className="grid md:grid-cols-2 gap-4 max-w-3xl">
            <div>
              <label className="text-xs font-semibold text-slate-500">Candidate</label>
              <select
                value={cid === "" ? "" : String(cid)}
                onChange={(e) => {
                  const id = Number(e.target.value);
                  setCid(id);
                  const p = pool.find((x) => x.id === id);
                  if (p) setTitle(p.job_title);
                }}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              >
                {pool.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} · {p.hire_decision}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500">Base salary (USD)</label>
              <input
                type="number"
                value={salary}
                onChange={(e) => setSalary(Number(e.target.value))}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500">Start date</label>
              <input
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500">Title on letter</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
            <div className="md:col-span-2">
              <label className="text-xs font-semibold text-slate-500">Reports to</label>
              <input
                value={mgr}
                onChange={(e) => setMgr(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
          </div>
          <button
            type="button"
            disabled={cid === ""}
            onClick={async () => {
              await api.post("/api/offers", {
                candidate_id: cid,
                salary,
                start_date: start,
                job_title: title,
                reporting_manager: mgr,
              });
              load();
            }}
            className="mt-6 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            Save draft offer
          </button>
        </Card>
      ) : null}

      <Card>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
          Offer records
        </h3>
        <div className="space-y-4">
          {offers.map((o) => (
            <div
              key={o.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-100 bg-slate-50/80 px-4 py-3"
            >
              <div>
                <div className="font-semibold text-slate-900">{o.candidate_name}</div>
                <div className="text-xs text-slate-500">Offer #{o.id}</div>
              </div>
              <div className="text-sm font-semibold text-slate-800 tabular-nums">${o.salary.toLocaleString()}</div>
              {role === "HR Recruiter" ? (
                <div className="flex items-center gap-2">
                  <select
                    key={`${o.id}-${o.approval_status}`}
                    defaultValue={o.approval_status}
                    onChange={async (e) => {
                      await api.patch(`/api/offers/${o.id}/status`, { approval_status: e.target.value });
                      load();
                    }}
                    className="rounded-lg border border-slate-200 px-2 py-1.5 text-xs font-medium"
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-600 border border-slate-200">
                  {o.approval_status}
                </span>
              )}
            </div>
          ))}
          {offers.length === 0 && <p className="text-sm text-slate-500">No offers yet.</p>}
        </div>
      </Card>
    </>
  );
}
