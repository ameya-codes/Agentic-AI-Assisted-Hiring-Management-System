import * as React from "react";
import { api } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Job = { id: number; title: string; department: string };

export function ScreeningPage() {
  const { activeJobId } = useActiveRequisition();
  const [jobs, setJobs] = React.useState<Job[]>([]);
  const [name, setName] = React.useState("Jamie Doe");
  const [email, setEmail] = React.useState("jamie@example.com");
  const [resume, setResume] = React.useState(
    "Python, AWS, 5 years backend. BS CS. Built APIs and data pipelines.",
  );
  const [result, setResult] = React.useState<Record<string, unknown> | null>(null);
  const [saved, setSaved] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      const j = (await api.get("/api/jobs")) as Job[];
      setJobs(j.map((x) => ({ id: x.id, title: x.title, department: x.department })));
    })().catch(() => {});
  }, []);

  const current = jobs.find((j) => j.id === activeJobId);

  return (
    <>
      <PageTitle
        kicker="Talent acquisition"
        title="Resume screening"
        subtitle="Screening is tied to the active requisition in the sidebar — same job_id is stored on every candidate record."
      />
      <PocStrip />
      <Card className="mb-4">
        <p className="text-sm text-slate-700">
          <span className="font-semibold text-slate-900">Active requisition:</span>{" "}
          {current ? (
            <>
              #{current.id} · {current.title} · {current.department}
            </>
          ) : (
            <span className="text-amber-700">Select or publish a requisition from the sidebar.</span>
          )}
        </p>
      </Card>
      <Card>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Name"
            />
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Email"
            />
            <textarea
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              rows={8}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm font-mono"
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={activeJobId == null}
                onClick={async () => {
                  if (activeJobId == null) return;
                  const out = (await api.post("/api/ai/preview-screen", {
                    job_id: activeJobId,
                    resume_text: resume,
                  })) as Record<string, unknown>;
                  setResult(out);
                  setSaved(null);
                }}
                className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40"
              >
                Preview screening
              </button>
              <button
                type="button"
                disabled={activeJobId == null}
                onClick={async () => {
                  if (activeJobId == null) return;
                  await api.post("/api/candidates/screen", {
                    job_id: activeJobId,
                    name,
                    email,
                    resume_text: resume,
                  });
                  setSaved("Candidate and screening saved for this requisition.");
                }}
                className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-800 hover:bg-slate-50 disabled:opacity-40"
              >
                Save to ATS
              </button>
            </div>
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
              Agent output
            </h3>
            {!result ? (
              <p className="text-sm text-slate-500">Run preview to see structured fields and match score.</p>
            ) : (
              <dl className="space-y-3 text-sm">
                {Object.entries(result).map(([k, v]) => (
                  <div key={k}>
                    <dt className="text-xs font-semibold uppercase text-slate-400">{k}</dt>
                    <dd className="mt-0.5 text-slate-700 whitespace-pre-wrap">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            )}
            {saved && <p className="mt-6 text-sm font-medium text-emerald-700">{saved}</p>}
          </div>
        </div>
      </Card>
    </>
  );
}
