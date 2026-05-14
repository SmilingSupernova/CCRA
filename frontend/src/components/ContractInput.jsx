import { useRef, useState } from "react";

const ACCEPTED_EXTENSIONS = [".txt", ".pdf", ".docx"];

// left panel component: textarea + upload + analyze buttons
export default function ContractInput({
  loading,
  uploading,
  onAnalyzeText,
  onExtractFile,
  onInvalidFile,
}) {
  // current contract text shown in the textarea
  const [text, setText] = useState("");
  // name of the most recently uploaded file (just for display)
  const [fileName, setFileName] = useState("");
  // ref so the visible Upload button can click the hidden file input
  const fileInputRef = useRef(null);

  // fires when the user hits Analyze
  function handleAnalyzeText() {
    if (!text.trim() || loading || uploading) return;
    onAnalyzeText(text);
  }

  // fires when the user picks a file from the file dialog
  async function handleFilePicked(e) {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;

    const ok = ACCEPTED_EXTENSIONS.some((ext) =>
      file.name.toLowerCase().endsWith(ext),
    );
    if (!ok) {
      onInvalidFile("Please upload a .txt, .pdf, or .docx file.");
      return;
    }

    const extracted = await onExtractFile(file);
    if (typeof extracted === "string") {
      setText(extracted);
      setFileName(file.name);
    }
  }

  const busy = loading || uploading;

  return (
    <section>
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-1 text-base font-semibold text-slate-900">
          Your contract
        </h2>
        <p className="mb-4 text-sm text-slate-500">
          Paste the text or upload a file.
        </p>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste your contract here..."
          className="h-80 w-full resize-none rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm leading-relaxed focus:border-indigo-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100"
        />

        <div className="mt-2 flex justify-between text-xs text-slate-500">
          <span>{text.length.toLocaleString()} characters</span>
          {fileName && <span className="truncate">Uploaded: {fileName}</span>}
        </div>

        {/* hidden file input the Upload button clicks it via ref */}
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          onChange={handleFilePicked}
          className="hidden"
        />

        <div className="mt-5 flex gap-3">
          <button
            onClick={() => fileInputRef.current.click()}
            disabled={busy}
            className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:border-slate-400 hover:bg-slate-50 disabled:opacity-60"
          >
            {uploading ? "Reading file…" : "Upload file"}
          </button>
          <button
            onClick={handleAnalyzeText}
            disabled={!text.trim() || busy}
            className="flex-1 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:bg-slate-300"
          >
            {loading ? "Analyzing…" : "Analyze contract"}
          </button>
        </div>

        <p className="mt-3 text-center text-xs text-slate-400">
          Supports .txt, .pdf, and .docx
        </p>
      </div>
    </section>
  );
}
