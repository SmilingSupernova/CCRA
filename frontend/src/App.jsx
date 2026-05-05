import ContractInput from "./components/ContractInput";
import Header from "./components/Header";
import ResultsPanel from "./components/ResultsPanel";
import { useContractAnalysis } from "./hooks/useContractAnalysis";

export default function App() {
  const {
    results,
    loading,
    error,
    analyzeText,
    analyzeFile,
    setUploadError,
  } = useContractAnalysis();

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
      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 py-8 lg:grid-cols-2">
        <ContractInput
          loading={loading}
          onAnalyzeText={analyzeText}
          onAnalyzeFile={analyzeFile}
          onInvalidFile={setUploadError}
        />
        <section>
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
