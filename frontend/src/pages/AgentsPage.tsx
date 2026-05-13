import { Card, PageTitle, PocStrip } from "../components/PageChrome";

export function AgentsPage() {
  return (
    <>
      <PageTitle
        kicker="Platform"
        title="Agents & governance"
        subtitle="What the mock agents do — and what stays with people in a real deployment."
      />
      <PocStrip />
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Agent roster
          </h3>
          <ul className="space-y-3 text-sm text-slate-700">
            <li>Job description drafting & bias notes</li>
            <li>Resume screening & match score</li>
            <li>Candidate ranking for queue order</li>
            <li>Interview logistics & question banks</li>
            <li>Feedback synthesis for HR readout</li>
            <li>Offer letter text from approved facts</li>
            <li>Onboarding FAQ from playbook snippets</li>
          </ul>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
            Human-owned
          </h3>
          <ul className="space-y-3 text-sm text-slate-700">
            <li>Final hiring decision & exec calibration</li>
            <li>Salary bands and individual compensation approval</li>
            <li>Legal review and regional compliance</li>
            <li>HR investigations, conflicts, accommodations</li>
            <li>Background check adjudication</li>
          </ul>
        </Card>
      </div>
      <Card className="mt-6">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100 pb-3 mb-4">
          Stack
        </h3>
        <p className="text-sm text-slate-600 leading-relaxed">
          <strong className="text-slate-800">React + Tailwind</strong> in the browser,{" "}
          <strong className="text-slate-800">FastAPI</strong> for JSON APIs, same{" "}
          <strong className="text-slate-800">SQLite</strong> file and Python agents as the HireFlow AI project.
          Replace mock functions with guarded LLM calls when you are ready.
        </p>
      </Card>
    </>
  );
}
