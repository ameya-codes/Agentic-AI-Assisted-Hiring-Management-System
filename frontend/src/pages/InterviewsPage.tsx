import * as React from "react";
import { api, getRole } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { jobScopeQuery } from "../requisitionStorage";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Short = { id: number; name: string; job_title: string };
type IV = {
  id: number;
  candidate_id: number;
  candidate_name: string;
  job_title: string;
  interviewer_name: string;
  scheduled_at: string;
  interview_type: string;
  has_feedback: number;
};

export function InterviewsPage() {
  const role = getRole();
  const { activeJobId } = useActiveRequisition();
  const [tab, setTab] = React.useState<"schedule" | "feedback">(
    role === "Interviewer" ? "feedback" : "schedule"
  );
  const [shorts, setShorts] = React.useState<Short[]>([]);
  const [candId, setCandId] = React.useState<number | "">("");
  const [interviewer, setInterviewer] = React.useState("Jamie Ortiz");
  const [when, setWhen] = React.useState("2026-06-01 15:00");
  const [itype, setItype] = React.useState("Technical");

  const [ivs, setIvs] = React.useState<IV[]>([]);
  const [ivPick, setIvPick] = React.useState<number | "">("");
  const [tech, setTech] = React.useState("Strong technical discussion.");
  const [comm, setComm] = React.useState("Clear communication.");
  const [rating, setRating] = React.useState(4);
  const [hire, setHire] = React.useState("Maybe");

  const refresh = React.useCallback(async () => {
    const q = jobScopeQuery(activeJobId);
    const s = (await api.get(`/api/candidates/shortlisted${q}`)) as Short[];
    const iv = (await api.get(`/api/interviews${q}`)) as IV[];
    setShorts(s);
    setIvs(iv);
    const pend = iv.filter((x) => x.has_feedback === 0);
    setIvPick((prev) => {
      if (typeof prev === "number" && pend.some((p) => p.id === prev)) return prev;
      return pend.length ? pend[0].id : "";
    });
  }, [activeJobId]);

  React.useEffect(() => {
    refresh().catch(() => {});
  }, [refresh]);

  React.useEffect(() => {
    if (shorts.length && candId === "") setCandId(shorts[0].id);
  }, [shorts, candId]);

  const pending = ivs.filter((x) => x.has_feedback === 0);

  return (
    <>
      <PageTitle
        kicker="Coordination"
        title="Interviews"
        subtitle="Shortlist and interviews are filtered to the active requisition from the sidebar."
      />
      <PocStrip />
      <div className="flex gap-2 mb-6">
        {role !== "Interviewer" ? (
          <button
            type="button"
            onClick={() => setTab("schedule")}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              tab === "schedule" ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-slate-700"
            }`}
          >
            Schedule
          </button>
        ) : null}
        <button
          type="button"
          onClick={() => setTab("feedback")}
          className={`rounded-full px-4 py-2 text-sm font-semibold ${
            tab === "feedback" ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-slate-700"
          }`}
        >
          Feedback
        </button>
      </div>

      {tab === "schedule" && role !== "Interviewer" ? (
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            New interview
          </h3>
          <div className="grid md:grid-cols-2 gap-4 max-w-2xl">
            <div>
              <label className="text-xs font-semibold text-slate-500">Candidate</label>
              <select
                value={candId === "" ? "" : String(candId)}
                onChange={(e) => setCandId(Number(e.target.value))}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              >
                {shorts.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} · {s.job_title}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500">Interviewer</label>
              <input
                value={interviewer}
                onChange={(e) => setInterviewer(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500">Start (YYYY-MM-DD HH:MM)</label>
              <input
                value={when}
                onChange={(e) => setWhen(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm font-mono"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500">Type</label>
              <select
                value={itype}
                onChange={(e) => setItype(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              >
                <option>Technical</option>
                <option>Behavioral</option>
                <option>Final</option>
              </select>
            </div>
          </div>
          <button
            type="button"
            disabled={candId === ""}
            onClick={async () => {
              await api.post("/api/interviews", {
                candidate_id: candId,
                interviewer_name: interviewer,
                scheduled_at: when,
                interview_type: itype,
              });
              refresh();
            }}
            className="mt-6 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            Save to calendar
          </button>
        </Card>
      ) : null}

      {tab === "feedback" ? (
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Submit debrief
          </h3>
          {pending.length === 0 ? (
            <p className="text-sm text-slate-500">No interviews awaiting feedback.</p>
          ) : (
            <div className="space-y-4 max-w-2xl">
              <div>
                <label className="text-xs font-semibold text-slate-500">Interview</label>
                <select
                  value={ivPick === "" ? "" : String(ivPick)}
                  onChange={(e) => setIvPick(Number(e.target.value))}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                >
                  {pending.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.candidate_name} · {p.interview_type} · {p.scheduled_at}
                    </option>
                  ))}
                </select>
              </div>
              <textarea
                value={tech}
                onChange={(e) => setTech(e.target.value)}
                rows={3}
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="Technical notes"
              />
              <textarea
                value={comm}
                onChange={(e) => setComm(e.target.value)}
                rows={3}
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="Communication notes"
              />
              <div className="flex gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-500">Rating 1–5</label>
                  <input
                    type="number"
                    min={1}
                    max={5}
                    value={rating}
                    onChange={(e) => setRating(Number(e.target.value))}
                    className="mt-1 w-20 rounded-xl border border-slate-200 px-3 py-2 text-sm"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-xs font-semibold text-slate-500">Decision</label>
                  <select
                    value={hire}
                    onChange={(e) => setHire(e.target.value)}
                    className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                  >
                    <option>Hire</option>
                    <option>No Hire</option>
                    <option>Maybe</option>
                  </select>
                </div>
              </div>
              <button
                type="button"
                disabled={ivPick === ""}
                onClick={async () => {
                  await api.post("/api/feedback", {
                    interview_id: ivPick,
                    technical_feedback: tech,
                    communication_feedback: comm,
                    overall_rating: rating,
                    hire_decision: hire,
                  });
                  refresh();
                }}
                className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40"
              >
                Submit feedback
              </button>
            </div>
          )}
        </Card>
      ) : null}
    </>
  );
}
