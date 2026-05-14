import ContractInput from "./components/ContractInput";
import Header from "./components/Header";
import ResultsPanel from "./components/ResultsPanel";
import SummaryCard from "./components/SummaryCard";
import { useContractAnalysis } from "./hooks/useContractAnalysis";

export default function App() {
  // grab everything we need from the analysis hook
  const {
    results,
    loading,
    uploading,
    error,
    analyzeText,
    extractTextFromFile,
    setUploadError,
  } = useContractAnalysis();

  // turns the results into a JSON file and triggers a browser download
  function downloadJson() {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "contract-analysis.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <Header />
      {/* two-column layout on big screens, stacked on smaller ones */}
      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 py-8 lg:grid-cols-2">
        <div className="space-y-6">
          {/* left side: paste or upload a contract */}
          <ContractInput
            loading={loading}
            uploading={uploading}
            onAnalyzeText={analyzeText}
            onExtractFile={extractTextFromFile}
            onInvalidFile={setUploadError}
          />
          {/* showing the summary card once analysis is done */}
          {!loading && results?.summary && (
            <SummaryCard summary={results.summary} />
          )}
        </div>
        <section>
          {/* right side: per-clause results, or a loader/error */}
          <ResultsPanel
            loading={loading}
            error={error}
            results={results}
            onDownload={downloadJson}
          />
        </section>
      </main>
    </div>
  );
}
