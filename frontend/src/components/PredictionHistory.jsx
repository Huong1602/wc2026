function percent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

export default function PredictionHistory({ history }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <h2 className="text-xl font-semibold">Lịch sử dự đoán</h2>
      <div className="mt-4 overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th className="py-2">Trận</th>
              <th className="py-2">Xác suất</th>
              <th className="py-2 text-right">Tỷ số</th>
            </tr>
          </thead>
          <tbody>
            {history.length === 0 && (
              <tr>
                <td colSpan="3" className="py-4 text-center text-slate-500">
                  Chưa có lịch sử dự đoán.
                </td>
              </tr>
            )}
            {history.map((item) => (
              <tr key={item.id} className="border-t border-slate-800">
                <td className="py-3">
                  {item.homeTeam} vs {item.awayTeam}
                  <span className="block text-xs text-slate-500">{String(item.matchDate).slice(0, 10)}</span>
                </td>
                <td className="py-3 text-slate-300">
                  {percent(item.homeWinProbability)} / {percent(item.drawProbability)} /{" "}
                  {percent(item.awayWinProbability)}
                </td>
                <td className="py-3 text-right">
                  {item.predictedHomeScore} - {item.predictedAwayScore}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

