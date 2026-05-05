import { useState } from "react";
import Chip from "./Chip";
import RiskBadge from "./RiskBadge";
import { getRiskStyle } from "../utils/riskStyles";

function ChevronIcon({ open }) {
  return (
    <svg
      className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${
        open ? "rotate-180" : ""
      }`}
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.39a.75.75 0 01-1.08 0L5.21 8.27a.75.75 0 01.02-1.06z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export default function ClauseCard({ clause }) {
  const [open, setOpen] = useState(false);
  const s = getRiskStyle(clause.risk);

  return (
    <article className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md">
      {/* thin colored stripe at the top, color matches the risk level */}
      <div className={`h-1 ${s.bar}`} />

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left hover:bg-slate-50"
      >
        <div className="min-w-0">
          <div className="text-xs text-slate-500">
            Clause {clause.clause_number}
          </div>
          <h3 className="truncate text-lg font-semibold text-slate-900">
            {clause.category}
          </h3>
        </div>
        <div className="flex items-center gap-3">
          <RiskBadge value={clause.risk} />
          <ChevronIcon open={open} />
        </div>
      </button>

      {open && (
        <div className="border-t border-slate-100 px-5 py-5">
          <p className="mb-4 whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
            {clause.text}
          </p>

          {clause.explanation && (
            <div
              className={`mb-4 rounded-lg p-4 text-sm leading-relaxed ${s.explanation}`}
            >
              <div
                className={`mb-1 text-xs font-semibold uppercase tracking-wide ${s.explanationLabel}`}
              >
                Explanation
              </div>
              {clause.explanation}
            </div>
          )}

          {clause.entities?.length > 0 && (
            <div className="mb-3">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Entities
              </div>
              <div className="flex flex-wrap gap-2">
                {clause.entities.map((e, i) => (
                  <Chip key={i}>
                    {e.text}{" "}
                    <span className="text-slate-400">· {e.type}</span>
                  </Chip>
                ))}
              </div>
            </div>
          )}

          {clause.keyphrases?.length > 0 && (
            <div>
              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Key phrases
              </div>
              <div className="flex flex-wrap gap-2">
                {clause.keyphrases.map((k, i) => (
                  <Chip key={i}>{k}</Chip>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </article>
  );
}
