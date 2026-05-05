import { getRiskStyle } from "../utils/riskStyles";

export default function RiskBadge({ value }) {
  const s = getRiskStyle(value);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${s.badge}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {value || "Unknown"}
    </span>
  );
}
