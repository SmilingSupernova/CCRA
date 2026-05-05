import ClauseCard from "./ClauseCard";
import MessagePanel from "./MessagePanel";
import Spinner from "./Spinner";
import Summary from "./Summary";

function LoadingPanel() {
  return (
    <div className="flex h-96 flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <Spinner />
      <h3 className="mt-4 font-semibold text-slate-900">Analyzing…</h3>
    </div>
  );
}

export default function ResultsPanel({ loading, error, results, onDownload }) {
  if (loading) return <LoadingPanel />;

  if (error) {
    return <MessagePanel title="Something went wrong">{error}</MessagePanel>;
  }

  if (results) {
    return (
      <div className="space-y-4">
        <Summary clauses={results} onDownload={onDownload} />
        {results.map((clause, i) => (
          <ClauseCard key={i} clause={clause} />
        ))}
      </div>
    );
  }

  return (
    <MessagePanel title="No contract analyzed yet">
      Paste or upload a contract on the left to get started.
    </MessagePanel>
  );
}
