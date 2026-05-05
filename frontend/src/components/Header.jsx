export default function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center gap-3 px-6 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-lg font-bold text-white">
          C
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Contract Clause Risk Classifier
          </h1>
        </div>
      </div>
    </header>
  );
}
