import * as React from "react";
import { api } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Job = { id: number; title: string; department: string };

type ScreenResult = {
  skills?: string;
  experience?: string;
  education?: string;
  certifications?: string;
  strengths?: string;
  weaknesses?: string;
  match_score?: number;
  recommendation?: string;
  extracted_excerpt?: string;
  extracted_chars?: number;
};

function ScreeningOutput({ result }: { result: ScreenResult }) {
  const score = result.match_score;
  const rec = result.recommendation ?? "";
  const recColor =
    rec === "Proceed to Interview"
      ? "bg-emerald-100 text-emerald-900 border-emerald-200"
      : rec === "Hold"
        ? "bg-amber-100 text-amber-900 border-amber-200"
        : rec === "Reject"
          ? "bg-rose-100 text-rose-900 border-rose-200"
          : "bg-slate-100 text-slate-800 border-slate-200";

  const rows: [string, string | undefined][] = [
    ["Skills signals", result.skills],
    ["Experience", result.experience],
    ["Education", result.education],
    ["Certifications", result.certifications],
  ];

  return (
    <div className="space-y-4">
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-white p-4">
          <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-500">Match score</div>
          <div className="mt-1 text-4xl font-bold text-indigo-900 tabular-nums">{score ?? "—"}</div>
          <p className="text-xs text-slate-500 mt-2">Heuristic + LLM when API key is configured.</p>
        </div>
        <div className={`rounded-2xl border p-4 ${recColor}`}>
          <div className="text-[10px] font-bold uppercase tracking-wider opacity-80">AI recommendation</div>
          <div className="mt-2 text-lg font-bold">{rec || "—"}</div>
        </div>
      </div>
      <div className="grid gap-3">
        {rows.map(([label, val]) =>
          val ? (
            <div key={label} className="rounded-xl border border-slate-100 bg-slate-50/80 px-3 py-2.5">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</div>
              <p className="text-sm text-slate-800 mt-1 leading-relaxed">{val}</p>
            </div>
          ) : null,
        )}
      </div>
      {(result.strengths || result.weaknesses) && (
        <div className="grid md:grid-cols-2 gap-3">
          {result.strengths ? (
            <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 px-3 py-3">
              <div className="text-[10px] font-bold uppercase text-emerald-700">Strengths</div>
              <p className="text-sm text-slate-800 mt-1 whitespace-pre-wrap">{result.strengths}</p>
            </div>
          ) : null}
          {result.weaknesses ? (
            <div className="rounded-xl border border-amber-100 bg-amber-50/40 px-3 py-3">
              <div className="text-[10px] font-bold uppercase text-amber-800">Risks / gaps</div>
              <p className="text-sm text-slate-800 mt-1 whitespace-pre-wrap">{result.weaknesses}</p>
            </div>
          ) : null}
        </div>
      )}
      {result.extracted_excerpt != null && (
        <details className="rounded-xl border border-slate-200 bg-white px-3 py-2">
          <summary className="cursor-pointer text-sm font-semibold text-slate-700">
            Extracted résumé text (preview, {result.extracted_chars ?? result.extracted_excerpt.length} chars)
          </summary>
          <pre className="mt-2 max-h-48 overflow-y-auto text-xs text-slate-600 whitespace-pre-wrap font-mono leading-relaxed">
            {result.extracted_excerpt}
          </pre>
        </details>
      )}
    </div>
  );
}

export function ScreeningPage() {
  const { activeJobId } = useActiveRequisition();
  const [jobs, setJobs] = React.useState<Job[]>([]);
  const [mode, setMode] = React.useState<"paste" | "upload">("upload");
  const [name, setName] = React.useState("Jamie Doe");
  const [email, setEmail] = React.useState("jamie@example.com");
  const [resume, setResume] = React.useState(
    "Python, AWS, 5 years backend. BS CS. Built APIs and data pipelines.",
  );
  const [file, setFile] = React.useState<File | null>(null);
  const [result, setResult] = React.useState<ScreenResult | null>(null);
  const [saved, setSaved] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      const j = (await api.get("/api/jobs")) as Job[];
      setJobs(j.map((x) => ({ id: x.id, title: x.title, department: x.department })));
    })().catch(() => {});
  }, []);

  const current = jobs.find((j) => j.id === activeJobId);

  const runPastePreview = async () => {
    if (activeJobId == null) return;
    setBusy(true);
    setErr(null);
    setSaved(null);
    try {
      const out = (await api.post("/api/ai/preview-screen", {
        job_id: activeJobId,
        resume_text: resume,
      })) as ScreenResult;
      setResult(out);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Preview failed");
      setResult(null);
    } finally {
      setBusy(false);
    }
  };

  const runUploadPreview = async () => {
    if (activeJobId == null || !file) {
      setErr("Choose a résumé file (PDF, DOCX, or TXT).");
      return;
    }
    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".pdf") && !lower.endsWith(".docx") && !lower.endsWith(".txt")) {
      setErr("Use PDF, DOCX, or TXT. Legacy .doc is not supported.");
      return;
    }
    setBusy(true);
    setErr(null);
    setSaved(null);
    try {
      const fd = new FormData();
      fd.append("job_id", String(activeJobId));
      fd.append("resume", file);
      const out = (await api.postForm("/api/ai/preview-screen-upload", fd)) as ScreenResult;
      setResult(out);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Preview failed");
      setResult(null);
    } finally {
      setBusy(false);
    }
  };

  const savePaste = async () => {
    if (activeJobId == null) return;
    setBusy(true);
    setErr(null);
    try {
      await api.post("/api/candidates/screen", {
        job_id: activeJobId,
        name,
        email,
        resume_text: resume,
      });
      setSaved("Candidate and screening saved to this requisition.");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(false);
    }
  };

  const saveUpload = async () => {
    if (activeJobId == null || !file) {
      setErr("Choose a résumé file before saving.");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const fd = new FormData();
      fd.append("job_id", String(activeJobId));
      fd.append("name", name.trim());
      fd.append("email", email.trim());
      fd.append("resume", file);
      await api.postForm("/api/candidates/screen-upload", fd);
      setSaved("Candidate and screening saved from file upload.");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <PageTitle
        kicker="Talent acquisition"
        title="Résumé screening"
        subtitle="Preview AI-assisted signals, then commit the candidate to the ATS for the active requisition. Paste text or upload PDF / Word / TXT."
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
            <span className="text-amber-700">Select or publish a requisition in the sidebar.</span>
          )}
        </p>
      </Card>

      <div className="flex flex-wrap gap-2 mb-4">
        <button
          type="button"
          onClick={() => {
            setMode("upload");
            setErr(null);
          }}
          className={`rounded-full px-4 py-2 text-sm font-semibold ${
            mode === "upload" ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-slate-700"
          }`}
        >
          Upload résumé
        </button>
        <button
          type="button"
          onClick={() => {
            setMode("paste");
            setErr(null);
          }}
          className={`rounded-full px-4 py-2 text-sm font-semibold ${
            mode === "paste" ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-slate-700"
          }`}
        >
          Paste text
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Candidate & résumé input
          </h3>
          <div className="space-y-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Full name"
            />
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Email"
            />

            {mode === "paste" ? (
              <textarea
                value={resume}
                onChange={(e) => setResume(e.target.value)}
                rows={10}
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm font-mono"
                placeholder="Paste résumé or LinkedIn export as plain text…"
              />
            ) : (
              <div className="rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/60 px-4 py-6 text-center">
                <p className="text-sm text-slate-600 mb-3">
                  PDF, DOCX, or TXT — max 5MB. Text is extracted on the server (same path as careers apply).
                </p>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  className="text-sm text-slate-700 w-full"
                />
                {file && (
                  <p className="text-xs text-slate-500 mt-2">
                    Selected: <span className="font-medium text-slate-800">{file.name}</span>
                  </p>
                )}
              </div>
            )}

            {err && <p className="text-sm text-red-600">{err}</p>}

            <div className="flex flex-wrap gap-2 pt-1">
              <button
                type="button"
                disabled={activeJobId == null || busy}
                onClick={mode === "paste" ? runPastePreview : runUploadPreview}
                className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40"
              >
                {busy ? "Running…" : "Run AI screening"}
              </button>
              <button
                type="button"
                disabled={activeJobId == null || busy}
                onClick={mode === "paste" ? savePaste : saveUpload}
                className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-800 hover:bg-slate-50 disabled:opacity-40"
              >
                Save to ATS
              </button>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              <strong>Preview</strong> does not create a candidate row. <strong>Save to ATS</strong> inserts the
              candidate and screening for the active <code className="text-indigo-700">job_id</code>.
            </p>
          </div>
        </Card>

        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Screening output
          </h3>
          {!result ? (
            <p className="text-sm text-slate-500">
              Run <strong>Run AI screening</strong> to see match score, recommendation, and structured fields.
            </p>
          ) : (
            <ScreeningOutput result={result} />
          )}
          {saved && <p className="mt-6 text-sm font-medium text-emerald-700">{saved}</p>}
        </Card>
      </div>
    </>
  );
}
