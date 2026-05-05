const riskStyles = {
  High: {
    badge: "bg-rose-50 text-rose-700 border-rose-200",
    dot: "bg-rose-500",
    bar: "bg-rose-500",
    explanation: "bg-rose-50/70 border border-rose-100 text-rose-900",
    explanationLabel: "text-rose-700",
  },
  Medium: {
    badge: "bg-amber-50 text-amber-700 border-amber-200",
    dot: "bg-amber-500",
    bar: "bg-amber-500",
    explanation: "bg-amber-50/70 border border-amber-100 text-amber-900",
    explanationLabel: "text-amber-700",
  },
  Low: {
    badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
    dot: "bg-emerald-500",
    bar: "bg-emerald-500",
    explanation: "bg-emerald-50/70 border border-emerald-100 text-emerald-900",
    explanationLabel: "text-emerald-700",
  },
};

const fallbackStyle = {
  badge: "bg-slate-100 text-slate-700 border-slate-200",
  dot: "bg-slate-400",
  bar: "bg-slate-300",
  explanation: "bg-slate-50 border border-slate-200 text-slate-700",
  explanationLabel: "text-slate-500",
};

export function getRiskStyle(value) {
  return riskStyles[value] || fallbackStyle;
}
