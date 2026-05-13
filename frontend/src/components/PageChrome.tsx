import type { ReactNode } from "react";

export function PageTitle({
  kicker,
  title,
  subtitle,
}: {
  kicker?: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <header className="mb-8">
      {kicker ? (
        <p className="text-xs font-semibold tracking-[0.18em] text-indigo-600 uppercase mb-1">{kicker}</p>
      ) : null}
      <h1 className="text-3xl font-bold text-slate-900 tracking-tight">{title}</h1>
      {subtitle ? <p className="mt-2 text-slate-600 max-w-2xl leading-relaxed text-base">{subtitle}</p> : null}
    </header>
  );
}

export function PocStrip() {
  return (
    <div className="mb-8 rounded-xl border border-indigo-100 bg-gradient-to-r from-indigo-50/90 to-slate-50 px-4 py-3 text-sm text-slate-600 border-l-4 border-l-indigo-500">
      Academic proof of concept — AI is mocked. Hiring, pay, and compliance stay with people.
    </div>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-2xl bg-white shadow-card border border-slate-200/90 p-6 ${className}`.trim()}
    >
      {children}
    </div>
  );
}
