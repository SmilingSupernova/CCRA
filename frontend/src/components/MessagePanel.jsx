export default function MessagePanel({ title, children }) {
  return (
    <div className="flex h-96 flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <h3 className="font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-slate-500">
        {children}
      </p>
    </div>
  );
}
