export default function TeamTable({ teams }) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <h2 className="text-xl font-semibold">Đội tuyển</h2>
      <div className="mt-4 max-h-80 overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th className="py-2">Đội</th>
              <th className="py-2">Liên đoàn</th>
              <th className="py-2 text-right">Rank</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id} className="border-t border-slate-800">
                <td className="py-2 font-medium">{team.name}</td>
                <td className="py-2 text-slate-400">{team.confederation}</td>
                <td className="py-2 text-right">{team.rank || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

