import * as React from "react";
import { api } from "../api/client";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Person = { id: number; name: string; approval_status: string };
type Task = { id: number; task_name: string; completed: number; sort_order: number };

export function OnboardingPage() {
  const [people, setPeople] = React.useState<Person[]>([]);
  const [cid, setCid] = React.useState<number | "">("");
  const [tasks, setTasks] = React.useState<Task[]>([]);
  const [faqQ, setFaqQ] = React.useState("When will I receive my laptop?");
  const [faqA, setFaqA] = React.useState<string | null>(null);

  const loadPeople = React.useCallback(async () => {
    const p = (await api.get("/api/onboarding/candidates")) as Person[];
    setPeople(p);
    setCid((prev) => (prev === "" && p.length ? p[0].id : prev));
  }, []);

  React.useEffect(() => {
    loadPeople().catch(() => {});
  }, [loadPeople]);

  React.useEffect(() => {
    if (cid === "") return;
    (async () => {
      setTasks((await api.get(`/api/onboarding/${cid}/tasks`)) as Task[]);
    })().catch(() => {});
  }, [cid]);

  const toggle = async (t: Task) => {
    await api.patch(`/api/onboarding/tasks/${t.id}`, { completed: !t.completed });
    setTasks((await api.get(`/api/onboarding/${cid}/tasks`)) as Task[]);
  };

  return (
    <>
      <PageTitle
        kicker="People operations"
        title="Onboarding"
        subtitle="Checklist for approved or sent offers — plus a lightweight policy FAQ bot."
      />
      <PocStrip />
      {people.length === 0 ? (
        <Card>
          <p className="text-sm text-slate-600">No candidates with approved or sent offers yet.</p>
        </Card>
      ) : (
        <>
          <Card className="mb-6">
            <label className="text-xs font-semibold text-slate-500">New hire</label>
            <select
              value={cid === "" ? "" : String(cid)}
              onChange={(e) => setCid(Number(e.target.value))}
              className="mt-2 w-full max-w-md rounded-xl border border-slate-200 px-3 py-2 text-sm"
            >
              {people.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} · {p.approval_status}
                </option>
              ))}
            </select>
          </Card>
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
                Checklist
              </h3>
              <ul className="space-y-2">
                {tasks.map((t) => (
                  <li key={t.id} className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={Boolean(t.completed)}
                      onChange={() => toggle(t)}
                      className="h-4 w-4 rounded border-slate-300 text-indigo-600"
                    />
                    <span className="text-sm text-slate-800">{t.task_name}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
                Onboarding assistant
              </h3>
              <input
                value={faqQ}
                onChange={(e) => setFaqQ(e.target.value)}
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
              <button
                type="button"
                onClick={async () => {
                  const r = (await api.get(`/api/ai/onboarding?q=${encodeURIComponent(faqQ)}`)) as {
                    answer: string;
                  };
                  setFaqA(r.answer);
                }}
                className="mt-3 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
              >
                Ask
              </button>
              {faqA && <p className="mt-4 text-sm text-slate-700 leading-relaxed">{faqA}</p>}
            </Card>
          </div>
        </>
      )}
    </>
  );
}
