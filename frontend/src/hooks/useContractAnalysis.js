import { useState } from "react";

const API = "http://localhost:8000";

export function useContractAnalysis() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function analyzeText(text) {
    if (!text.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const res = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contract_text: text }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      setResults(await res.json());
    } catch (err) {
      setError(err.message || "Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  async function analyzeFile(file) {
    if (!file || loading) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/analyze-file`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error: ${res.status}`);
      }
      setResults(await res.json());
    } catch (err) {
      setError(err.message || "Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  function setUploadError(message) {
    setError(message);
  }

  return {
    results,
    loading,
    error,
    analyzeText,
    analyzeFile,
    setUploadError,
  };
}
