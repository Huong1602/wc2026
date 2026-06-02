export default function MatchTable({ matches }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <h2 className="text-xl font-semibold">Trận đấu lịch sử</h2>
      <div className="mt-4 max-h-80 overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th className="py-2">Ngày</th>
              <th className="py-2">Trận</th>
              <th className="py-2 text-right">Tỷ số</th>
            </tr>
          </thead>
          <tbody>
            {matches.map((match) => (
              <tr key={match.id} className="border-t border-slate-800">
                <td className="py-2 text-slate-400">{String(match.matchDate).slice(0, 10)}</td>
                <td className="py-2">
                  {match.homeTeam} vs {match.awayTeam}
                  <span className="block text-xs text-slate-500">{match.tournament}</span>
                </td>
                <td className="py-2 text-right">
                  {match.homeScore} - {match.awayScore}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

