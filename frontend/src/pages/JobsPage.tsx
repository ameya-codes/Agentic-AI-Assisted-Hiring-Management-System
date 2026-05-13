import * as React from "react";
import { api, getRole, setApplicantEmail } from "../api/client";
import { useActiveRequisition } from "../context/RequisitionContext";
import { jobScopeQuery } from "../requisitionStorage";
import { Card, PageTitle, PocStrip } from "../components/PageChrome";

type Job = {
  id: number;
  title: string;
  department: string;
  location: string;
  salary_min: number;
  salary_max: number;
  experience_level: string;
  required_skills: string;
  description: string;
  status: string;
};

type PublicJob = {
  id: number;
  title: string;
  department: string;
  location: string;
  experience_level: string;
  required_skills: string;
  description: string;
};

function CareersSection() {
  const [jobs, setJobs] = React.useState<PublicJob[]>([]);
  const [listErr, setListErr] = React.useState<string | null>(null);
  const [applyJob, setApplyJob] = React.useState<PublicJob | null>(null);
  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [file, setFile] = React.useState<File | null>(null);
  const [submitting, setSubmitting] = React.useState(false);
  const [formErr, setFormErr] = React.useState<string | null>(null);
  const [successNote, setSuccessNote] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    setJobs((await api.get("/api/careers/open-roles")) as PublicJob[]);
  }, []);

  React.useEffect(() => {
    load().catch(() => setListErr("Could not load open roles."));
  }, [load]);

  return (
    <>
      <PageTitle
        kicker="Careers"
        title="Open roles at HireFlow"
        subtitle="Public job summaries only — compensation and internal hiring data stay with your recruiting team."
      />
      <PocStrip />
      {listErr && <p className="text-red-600 text-sm mb-4">{listErr}</p>}
      {successNote && (
        <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          {successNote}
        </div>
      )}
      <div className="space-y-4">
        {jobs.length === 0 ? (
          <Card>
            <p className="text-sm text-slate-600">No open roles right now. Check back later.</p>
          </Card>
        ) : (
          jobs.map((j) => (
            <Card key={j.id}>
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{j.title}</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    {j.department} · {j.location} · {j.experience_level}
                  </p>
                  <p className="text-sm text-slate-600 mt-3">
                    <span className="font-semibold text-slate-700">Focus: </span>
                    {j.required_skills}
                  </p>
                  <p className="text-sm text-slate-600 mt-2 whitespace-pre-wrap leading-relaxed">{j.description}</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setApplyJob(j);
                    setFormErr(null);
                  }}
                  className="shrink-0 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
                >
                  Apply
                </button>
              </div>
            </Card>
          ))
        )}
      </div>

      {applyJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Apply · {applyJob.title}</h3>
            <p className="text-sm text-slate-500 mt-1">Upload PDF, DOCX, or TXT (max 5MB).</p>
            <div className="mt-4 space-y-3">
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
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="w-full text-sm text-slate-600"
              />
            </div>
            {formErr && <p className="text-sm text-red-600 mt-3">{formErr}</p>}
            <div className="flex gap-2 mt-6">
              <button
                type="button"
                onClick={() => {
                  setApplyJob(null);
                  setFormErr(null);
                }}
                className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={async () => {
                  if (!name.trim() || !email.trim() || !file) {
                    setFormErr("Name, email, and résumé file are required.");
                    return;
                  }
                  const lower = file.name.toLowerCase();
                  if (!lower.endsWith(".pdf") && !lower.endsWith(".docx") && !lower.endsWith(".txt")) {
                    setFormErr("Please upload PDF, DOCX, or TXT. Legacy .doc is not supported in this POC.");
                    return;
                  }
                  setSubmitting(true);
                  setFormErr(null);
                  try {
                    const fd = new FormData();
                    fd.append("job_id", String(applyJob.id));
                    fd.append("name", name.trim());
                    fd.append("email", email.trim());
                    fd.append("resume", file);
                    await api.postForm("/api/careers/apply", fd);
                    setApplicantEmail(email.trim());
                    setApplyJob(null);
                    setName("");
                    setEmail("");
                    setFile(null);
                    setSuccessNote(
                      "Application submitted. Your résumé is with the recruiting team; AI-assisted screening runs in the background (same flow as recruiter Screening).",
                    );
                  } catch (e) {
                    setFormErr(e instanceof Error ? e.message : "Apply failed");
                  } finally {
                    setSubmitting(false);
                  }
                }}
                className="flex-1 rounded-xl bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
              >
                {submitting ? "Submitting…" : "Submit application"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

type Applicant = {
  candidate_id: number;
  name: string;
  email: string;
  status: string;
  applied_at: string;
  job_id: number;
  job_title: string;
  job_status: string;
  job_department: string;
  match_score: number | null;
  recommendation: string | null;
};

function InternalJobsSection() {
  const { activeJobId, setActiveJobId } = useActiveRequisition();
  const [jobs, setJobs] = React.useState<Job[]>([]);
  const [applicants, setApplicants] = React.useState<Applicant[]>([]);
  const [title, setTitle] = React.useState("Software Engineer II");
  const [department, setDepartment] = React.useState("Engineering");
  const [location, setLocation] = React.useState("Hybrid");
  const [salaryMin, setSalaryMin] = React.useState(120000);
  const [salaryMax, setSalaryMax] = React.useState(155000);
  const [skills, setSkills] = React.useState("Python, SQL, AWS");
  const [desc, setDesc] = React.useState("");
  const [ai, setAi] = React.useState<Record<string, string> | null>(null);
  const [msg, setMsg] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    const j = (await api.get("/api/jobs")) as Job[];
    setJobs(j);
    if (activeJobId == null) {
      setApplicants([]);
      return;
    }
    const a = (await api.get(`/api/jobs/applicants${jobScopeQuery(activeJobId)}`)) as Applicant[];
    setApplicants(a);
  }, [activeJobId]);

  React.useEffect(() => {
    load().catch(() => setMsg("Could not reach API."));
  }, [load]);

  return (
    <>
      <PageTitle
        kicker="Workforce planning"
        title="Job requisitions"
        subtitle="Publish roles, see who applied to each requisition, and use Screening for AI-assisted review."
      />
      <PocStrip />
      {msg && <p className="text-red-600 text-sm mb-4">{msg}</p>}
      <div className="grid lg:grid-cols-5 gap-6">
        <Card className="lg:col-span-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            New requisition
          </h3>
          <div className="space-y-3">
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Title"
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="Department"
              />
              <input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="Location"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                value={salaryMin}
                onChange={(e) => setSalaryMin(Number(e.target.value))}
                className="rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
              <input
                type="number"
                value={salaryMax}
                onChange={(e) => setSalaryMax(Number(e.target.value))}
                className="rounded-xl border border-slate-200 px-3 py-2 text-sm"
              />
            </div>
            <input
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Skills"
            />
            <textarea
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              rows={3}
              className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="Description"
            />
            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={async () => {
                  const out = (await api.post("/api/ai/job-description", {
                    title,
                    department,
                    location,
                    salary_min: salaryMin,
                    salary_max: salaryMax,
                    experience_level: "Mid",
                    required_skills: skills,
                    notes: desc,
                  })) as Record<string, string>;
                  setAi(out);
                  setDesc((d) => d || out.description);
                }}
                className="flex-1 rounded-xl border border-slate-200 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Draft with AI
              </button>
              <button
                type="button"
                onClick={async () => {
                  const res = (await api.post("/api/jobs", {
                    title,
                    department,
                    location,
                    salary_min: salaryMin,
                    salary_max: salaryMax,
                    experience_level: "Mid",
                    required_skills: skills,
                    description: desc || ai?.description || "",
                  })) as { id: number };
                  setActiveJobId(res.id);
                  setMsg("Saved — this requisition is now active in the sidebar.");
                  load();
                }}
                className="flex-1 rounded-xl bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
              >
                Publish
              </button>
            </div>
          </div>
        </Card>
        <Card className="lg:col-span-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Published ({jobs.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100">
                  <th className="pb-2 pr-4">Title</th>
                  <th className="pb-2 pr-4">Team</th>
                  <th className="pb-2 pr-4">Location</th>
                  <th className="pb-2">Band</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((j) => (
                  <tr
                    key={j.id}
                    className={
                      j.id === activeJobId
                        ? "border-b border-indigo-100 bg-indigo-50/60 last:border-0"
                        : "border-b border-slate-50 last:border-0"
                    }
                  >
                    <td className="py-3 pr-4 font-medium text-slate-900">{j.title}</td>
                    <td className="py-3 pr-4 text-slate-600">{j.department}</td>
                    <td className="py-3 pr-4 text-slate-600">{j.location}</td>
                    <td className="py-3 text-slate-600 tabular-nums">
                      ${j.salary_min.toLocaleString()} – ${j.salary_max.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {ai && (
            <details className="mt-6 rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <summary className="cursor-pointer text-sm font-semibold text-slate-800">Latest AI draft</summary>
              <div className="mt-3 text-sm max-w-none text-slate-600 whitespace-pre-wrap leading-relaxed">{ai.description}</div>
            </details>
          )}
        </Card>
      </div>
      <Card className="mt-6">
        <div className="border-b border-slate-100 pb-4 mb-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Applicants for active requisition
          </h3>
          <p className="text-sm text-slate-600 mt-1">
            Scoped to the job selected in the sidebar. Everyone who applied (careers or screening) appears here with
            the same <strong className="text-slate-800">job_id</strong>. Use <strong>Screening</strong> for résumé text
            and AI preview; <strong>Pipeline</strong> for stages.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100">
                <th className="pb-2 pr-3">Applied</th>
                <th className="pb-2 pr-3">Name</th>
                <th className="pb-2 pr-3">Email</th>
                <th className="pb-2 pr-3">Role</th>
                <th className="pb-2 pr-3">Req. status</th>
                <th className="pb-2 pr-3">Pipeline</th>
                <th className="pb-2 pr-3">Match</th>
                <th className="pb-2">AI rec.</th>
              </tr>
            </thead>
            <tbody>
              {applicants.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-6 text-slate-500">
                    No applicants yet for this requisition. Career applications and screening saves both attach to this
                    job_id.
                  </td>
                </tr>
              ) : (
                applicants.map((r) => (
                  <tr key={r.candidate_id} className="border-b border-slate-50 last:border-0">
                    <td className="py-2.5 pr-3 text-slate-500 whitespace-nowrap">{r.applied_at}</td>
                    <td className="py-2.5 pr-3 font-medium text-slate-900">{r.name}</td>
                    <td className="py-2.5 pr-3 text-slate-600">{r.email || "—"}</td>
                    <td className="py-2.5 pr-3 text-slate-800">{r.job_title}</td>
                    <td className="py-2.5 pr-3 text-slate-600">{r.job_status}</td>
                    <td className="py-2.5 pr-3 text-slate-600">{r.status}</td>
                    <td className="py-2.5 pr-3 tabular-nums text-slate-700">
                      {r.match_score != null ? r.match_score : "—"}
                    </td>
                    <td className="py-2.5 text-slate-600 max-w-[180px] truncate" title={r.recommendation ?? ""}>
                      {r.recommendation ?? "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </>
  );
}

export function JobsPage() {
  const role = getRole();
  if (role === "Candidate") return <CareersSection />;
  return <InternalJobsSection />;
}
