import { useState } from "react";

// backend URL
const API = "http://localhost:8000";

// normalize the response so the UI always sees { summary, clauses }
function normalize(data) {
  if (Array.isArray(data)) return { summary: null, clauses: data };
  return {
    summary: data?.summary ?? null,
    clauses: data?.clauses ?? [],
  };
}

// custom hook that holds all the state and API calls for contract analysis
export function useContractAnalysis() {
  // analysis results from the backend
  const [results, setResults] = useState(null);

  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  // error message to show the user
  const [error, setError] = useState(null);

  // sends pasted text to the backend and stores the results
  async function analyzeText(text) {
    // ignoring empty input or if an analysis is already running
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
      setResults(normalize(await res.json()));
    } catch (err) {
      setError(err.message || "Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  // uploads a .txt/.pdf/.docx and gets the raw text back from the backend
  async function extractTextFromFile(file) {
    if (!file || uploading || loading) return null;
    setUploading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/extract-text`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error: ${res.status}`);
      }
      const data = await res.json();
      return data?.contract_text ?? "";
    } catch (err) {
      setError(err.message || "Could not read the uploaded file.");
      return null;
    } finally {
      setUploading(false);
    }
  }

  function setUploadError(message) {
    setError(message);
  }

  return {
    results,
    loading,
    uploading,
    error,
    analyzeText,
    extractTextFromFile,
    setUploadError,
  };
}
