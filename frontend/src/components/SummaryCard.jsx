export default function SummaryCard({ summary }) {
  if (!summary) return null;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-1 text-base font-semibold text-slate-900">
        Contract Summary
      </h2>
      <p className="text-sm leading-relaxed text-slate-700">{summary}</p>
    </div>
  );
}
