import { useState } from "react";

export default function PredictionForm({ teams, loading, onSubmit }) {
  const [homeTeam, setHomeTeam] = useState("France");
  const [awayTeam, setAwayTeam] = useState("Japan");
  const [matchDate, setMatchDate] = useState("2026-06-15");
  const [country, setCountry] = useState("United States");
  const [tournament, setTournament] = useState("FIFA World Cup");
  const [neutral, setNeutral] = useState(true);

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit({
      homeTeam,
      awayTeam,
      matchDate,
      country,
      tournament,
      neutral,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
      <h2 className="text-xl font-semibold">Nhập trận đấu cần dự đoán</h2>
      <p className="mt-1 text-sm text-slate-400">Chọn hai đội tuyển thuộc danh sách 48 đội World Cup 2026.</p>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-sm font-medium text-slate-300">Đội 1</span>
          <select
            value={homeTeam}
            onChange={(event) => setHomeTeam(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-emerald-400"
          >
            {teams.map((team) => (
              <option key={team.id} value={team.name}>
                {team.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-300">Đội 2</span>
          <select
            value={awayTeam}
            onChange={(event) => setAwayTeam(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-emerald-400"
          >
            {teams.map((team) => (
              <option key={team.id} value={team.name}>
                {team.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-300">Ngày thi đấu</span>
          <input
            type="date"
            value={matchDate}
            onChange={(event) => setMatchDate(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-emerald-400"
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-300">Quốc gia tổ chức</span>
          <select
            value={country}
            onChange={(event) => setCountry(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-emerald-400"
          >
            <option>United States</option>
            <option>Canada</option>
            <option>Mexico</option>
          </select>
        </label>

        <label className="block sm:col-span-2">
          <span className="text-sm font-medium text-slate-300">Giải đấu</span>
          <select
            value={tournament}
            onChange={(event) => setTournament(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-emerald-400"
          >
            <option>FIFA World Cup</option>
            <option>FIFA World Cup qualification</option>
            <option>Friendly</option>
          </select>
        </label>
      </div>

      <label className="mt-4 flex items-center gap-3 text-sm text-slate-300">
        <input
          type="checkbox"
          checked={neutral}
          onChange={(event) => setNeutral(event.target.checked)}
          className="h-4 w-4 rounded border-slate-600 bg-slate-950 text-emerald-500"
        />
        Trận đấu sân trung lập
      </label>

      <button
        type="submit"
        disabled={loading}
        className="mt-5 w-full rounded-lg bg-emerald-500 px-4 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-600"
      >
        {loading ? "Đang dự đoán..." : "Dự đoán kết quả"}
      </button>
    </form>
  );
}
