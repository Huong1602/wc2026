function percent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

export default function ModelEvaluation({ evaluation }) {
  if (!evaluation?.metrics) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
        <h2 className="text-xl font-semibold">Model Evaluation</h2>
        <p className="mt-3 text-sm text-slate-400">
          Metrics chưa sẵn sàng. Hãy chạy `python -m src.train` trong thư mục `ml`.
        </p>
      </section>
    );
  }

  const { metrics, eda } = evaluation;
  const bestModel = metrics.best_model;
  const bestMetrics = metrics.models?.[bestModel] || {};

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Model Evaluation</h2>
          <p className="mt-1 text-sm text-slate-400">
            Time-based split, macro F1, log loss và MAE tỷ số.
          </p>
        </div>
        <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-300">
          Best: {bestModel || "N/A"}
        </span>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-4">
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Rows</p>
          <p className="mt-2 text-2xl font-bold">{metrics.dataset?.rows || "-"}</p>
        </div>
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Accuracy</p>
          <p className="mt-2 text-2xl font-bold">{percent(bestMetrics.accuracy)}</p>
        </div>
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Macro F1</p>
          <p className="mt-2 text-2xl font-bold">{percent(bestMetrics.macro_f1)}</p>
        </div>
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Avg goals</p>
          <p className="mt-2 text-2xl font-bold">{Number(eda?.average_total_goals || 0).toFixed(2)}</p>
        </div>
      </div>

      {bestMetrics.top_features?.length > 0 && (
        <div className="mt-5">
          <p className="text-sm font-medium text-slate-300">Top features</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {bestMetrics.top_features.slice(0, 6).map((item) => (
              <span key={item.feature} className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                {item.feature}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

