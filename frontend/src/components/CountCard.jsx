import { getRiskStyle } from "../utils/riskStyles";

export default function CountCard({ level, count }) {
  const s = getRiskStyle(level);
  return (
    <div className={`rounded-lg border p-3 ${s.badge}`}>
      <div className="text-xs font-semibold uppercase tracking-wide opacity-80">
        {level} risk
      </div>
      <div className="mt-1 text-2xl font-bold">{count}</div>
    </div>
  );
}
