function formatPercent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

function getScore(predictedScore, key, legacyKey) {
  return predictedScore?.[key] ?? predictedScore?.[legacyKey] ?? 0;
}

function formatModelName(name) {
  return name
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatResult(resultKey) {
  const labels = {
    homeWin: "Đội 1 thắng",
    draw: "Hòa",
    awayWin: "Đội 2 thắng",
  };

  return labels[resultKey] || resultKey;
}

export default function PredictionResult({ prediction }) {
  if (!prediction) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
        <h2 className="text-xl font-semibold">Kết quả dự đoán</h2>
        <p className="mt-3 text-slate-400">
          Chưa có dự đoán. Nhập trận đấu ở form bên trái để xem xác suất, tỷ số và các feature quan trọng.
        </p>
      </div>
    );
  }

  const { probabilities, predictedScore, modelPredictions = {} } = prediction;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <h2 className="text-xl font-semibold">
        {prediction.homeTeam} vs {prediction.awayTeam}
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Ngày {prediction.matchDate} tại {prediction.country} · Model chính: {formatModelName(prediction.modelName || "N/A")}
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
          {prediction.homeTeam} {getScore(predictedScore, "home", "homeScore")} -{" "}
          {getScore(predictedScore, "away", "awayScore")} {prediction.awayTeam}
        </p>
      </div>

      {Object.keys(modelPredictions).length > 0 && (
        <div className="mt-5 overflow-hidden rounded-xl border border-slate-800">
          <div className="border-b border-slate-800 bg-slate-950 px-4 py-3">
            <p className="font-medium">So sánh dự đoán theo từng mô hình</p>
            <p className="text-xs text-slate-500">Dùng để tham khảo, model chính vẫn là model có macro F1 tốt nhất.</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950 text-slate-400">
                <tr>
                  <th className="px-4 py-2">Model</th>
                  <th className="px-4 py-2">{prediction.homeTeam}</th>
                  <th className="px-4 py-2">Hòa</th>
                  <th className="px-4 py-2">{prediction.awayTeam}</th>
                  <th className="px-4 py-2">Kết luận</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(modelPredictions).map(([modelName, modelPrediction]) => (
                  <tr key={modelName} className="border-t border-slate-800">
                    <td className="px-4 py-2 font-medium">
                      {formatModelName(modelName)}
                      {modelName === prediction.modelName && (
                        <span className="ml-2 rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-300">
                          chính
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2">{formatPercent(modelPrediction.probabilities.homeWin)}</td>
                    <td className="px-4 py-2">{formatPercent(modelPrediction.probabilities.draw)}</td>
                    <td className="px-4 py-2">{formatPercent(modelPrediction.probabilities.awayWin)}</td>
                    <td className="px-4 py-2">{formatResult(modelPrediction.predictedResult)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {prediction.topFeatures?.length > 0 && (
        <div className="mt-5">
          <p className="text-sm font-medium text-slate-300">Yếu tố ảnh hưởng mạnh</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {prediction.topFeatures.map((feature) => (
              <span key={feature} className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                {feature}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

