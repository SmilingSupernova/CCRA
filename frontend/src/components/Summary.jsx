import CountCard from "./CountCard";

export default function Summary({ clauses, onDownload }) {
  const counts = { High: 0, Medium: 0, Low: 0 };
  for (const c of clauses) {
    // guard against unexpected risk values like "Unknown"
    if (c.risk in counts) counts[c.risk]++;
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Total clauses
          </div>
          <div className="text-3xl font-bold text-slate-900">
            {clauses.length}
          </div>
        </div>
        <button
          onClick={onDownload}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Download JSON
        </button>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <CountCard level="High" count={counts.High} />
        <CountCard level="Medium" count={counts.Medium} />
        <CountCard level="Low" count={counts.Low} />
      </div>
    </div>
  );
}
