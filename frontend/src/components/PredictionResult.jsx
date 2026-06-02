function formatPercent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

export default function PredictionResult({ prediction }) {
  if (!prediction) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
        <h2 className="text-xl font-semibold">Kết quả dự đoán</h2>
        <p className="mt-3 text-slate-400">
          Chưa có dự đoán. Nhập trận đấu ở form bên trái để xem xác suất và tỷ số baseline.
        </p>
      </div>
    );
  }

  const { probabilities, predictedScore } = prediction;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <h2 className="text-xl font-semibold">
        {prediction.homeTeam} vs {prediction.awayTeam}
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Ngày {prediction.matchDate} tại {prediction.country}
      </p>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-sm text-slate-400">{prediction.homeTeam} thắng</p>
          <p className="mt-2 text-2xl font-bold text-emerald-400">
            {formatPercent(probabilities.homeWin)}
          </p>
        </div>
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-sm text-slate-400">Hòa</p>
          <p className="mt-2 text-2xl font-bold text-amber-300">{formatPercent(probabilities.draw)}</p>
        </div>
        <div className="rounded-xl bg-slate-950 p-4">
          <p className="text-sm text-slate-400">{prediction.awayTeam} thắng</p>
          <p className="mt-2 text-2xl font-bold text-sky-400">{formatPercent(probabilities.awayWin)}</p>
        </div>
      </div>

      <div className="mt-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
        <p className="text-sm text-emerald-200">Tỷ số dự đoán</p>
        <p className="mt-1 text-3xl font-bold">
          {prediction.homeTeam} {predictedScore.homeScore} - {predictedScore.awayScore}{" "}
          {prediction.awayTeam}
        </p>
      </div>
    </div>
  );
}

