function percent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

function roundLabel(round) {
  const labels = {
    round_of_32: "Round of 32",
    round_of_16: "Round of 16",
    quarter_final: "Quarter-final",
    semi_final: "Semi-final",
    final: "Final",
  };
  return labels[round] || round;
}

export default function TournamentSimulation({ simulation, loading, onRun }) {
  const championRows = simulation?.championProbabilities?.teams || [];
  const standings = simulation?.groupStage?.standings || {};
  const bracket = simulation?.knockoutBracket?.bracket || {};

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">World Cup 2026 Tournament Simulation</h2>
          <p className="mt-1 text-sm text-slate-400">
            Mô phỏng vòng bảng, sinh nhánh knockout và tính xác suất vô địch bằng model ML hiện tại.
          </p>
        </div>
        <button
          type="button"
          onClick={() => onRun(10000)}
          disabled={loading}
          className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-600"
        >
          {loading ? "Đang mô phỏng..." : "Run 10,000 simulations"}
        </button>
      </div>

      {!simulation && (
        <div className="mt-5 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
          Chưa có kết quả simulation. Nhấn nút chạy mô phỏng hoặc chạy `python -m src.tournament_simulator` trong thư mục `ml`.
        </div>
      )}

      {championRows.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold">Top Champion Probabilities</h3>
          <div className="mt-3 overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950 text-slate-400">
                <tr>
                  <th className="px-4 py-2">#</th>
                  <th className="px-4 py-2">Team</th>
                  <th className="px-4 py-2">Champion</th>
                  <th className="px-4 py-2">Final</th>
                  <th className="px-4 py-2">Semi-final</th>
                  <th className="px-4 py-2">Qualified</th>
                </tr>
              </thead>
              <tbody>
                {championRows.slice(0, 10).map((row, index) => (
                  <tr key={row.team} className="border-t border-slate-800">
                    <td className="px-4 py-2 text-slate-500">{index + 1}</td>
                    <td className="px-4 py-2 font-medium">{row.team}</td>
                    <td className="px-4 py-2 text-emerald-300">{percent(row.championProbability)}</td>
                    <td className="px-4 py-2">{percent(row.finalProbability)}</td>
                    <td className="px-4 py-2">{percent(row.semiFinalProbability)}</td>
                    <td className="px-4 py-2">{percent(row.qualificationProbability)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {Object.keys(standings).length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold">Simulated Group Standings</h3>
          <div className="mt-3 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Object.entries(standings).map(([groupName, rows]) => (
              <div key={groupName} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <h4 className="font-semibold text-emerald-300">Group {groupName}</h4>
                <table className="mt-2 w-full text-left text-xs">
                  <thead className="text-slate-500">
                    <tr>
                      <th className="py-1">Team</th>
                      <th className="py-1 text-right">Pts</th>
                      <th className="py-1 text-right">GD</th>
                      <th className="py-1 text-right">GF</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={row.team} className="border-t border-slate-800">
                        <td className="py-1">{row.position}. {row.team}</td>
                        <td className="py-1 text-right">{row.points}</td>
                        <td className="py-1 text-right">{row.goal_difference}</td>
                        <td className="py-1 text-right">{row.goals_for}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(bracket).length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold">
            Predicted Knockout Bracket · Champion: {simulation.knockoutBracket?.predictedChampion}
          </h3>
          <div className="mt-3 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Object.entries(bracket).map(([round, matches]) => (
              <div key={round} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                <h4 className="font-semibold text-sky-300">{roundLabel(round)}</h4>
                <div className="mt-2 space-y-2 text-xs">
                  {matches.map((match) => (
                    <div key={match.matchNo} className="rounded-lg bg-slate-900 p-2">
                      <div className="font-medium">
                        {match.homeTeam} {match.homeScore} - {match.awayScore} {match.awayTeam}
                      </div>
                      <div className="text-slate-500">Winner: {match.winner}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
