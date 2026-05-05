export default function Chip({ children }) {
  return (
    <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-700">
      {children}
    </span>
  );
}
