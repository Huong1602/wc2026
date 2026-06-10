import { useEffect, useState } from "react";

import {
  createPrediction,
  fetchMatches,
  fetchModelMetrics,
  fetchPredictions,
  fetchTeams,
  fetchTournamentSimulation,
  runTournamentSimulation,
} from "./api.js";
import MatchTable from "./components/MatchTable.jsx";
import ModelEvaluation from "./components/ModelEvaluation.jsx";
import PredictionForm from "./components/PredictionForm.jsx";
import PredictionHistory from "./components/PredictionHistory.jsx";
import PredictionResult from "./components/PredictionResult.jsx";
import TeamTable from "./components/TeamTable.jsx";
import TournamentSimulation from "./components/TournamentSimulation.jsx";

export default function App() {
  const [teams, setTeams] = useState([]);
  const [matches, setMatches] = useState([]);
  const [history, setHistory] = useState([]);
  const [evaluation, setEvaluation] = useState(null);
  const [tournamentSimulation, setTournamentSimulation] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadDashboardData() {
    try {
      const [teamData, matchData, predictionData, evaluationData, tournamentData] = await Promise.all([
        fetchTeams(),
        fetchMatches(),
        fetchPredictions(),
        fetchModelMetrics(),
        fetchTournamentSimulation().catch(() => null),
      ]);
      setTeams(teamData);
      setMatches(matchData);
      setHistory(predictionData);
      setEvaluation(evaluationData);
      setTournamentSimulation(tournamentData);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function handlePredict(formData) {
    setLoading(true);
    setError("");

    try {
      const result = await createPrediction(formData);
      setPrediction(result);
      await loadDashboardData();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunTournamentSimulation(simulations) {
    setSimulationLoading(true);
    setError("");

    try {
      const result = await runTournamentSimulation(simulations);
      setTournamentSimulation(result);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSimulationLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-emerald-400">
            FIFA World Cup 2026
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-5xl">
            Hệ thống dự đoán kết quả bóng đá
          </h1>
          <p className="mt-4 max-w-3xl text-slate-300">
            Demo fullstack dùng dữ liệu trận quốc tế công khai, ranking Elo-derived,
            phong độ gần đây, lịch sử đối đầu và lợi thế đồng chủ nhà để dự báo xác suất thắng hòa thua.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <PredictionForm teams={teams} loading={loading} onSubmit={handlePredict} />
          <PredictionResult prediction={prediction} />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <TeamTable teams={teams} />
          <MatchTable matches={matches} />
        </div>

        <div className="mt-8">
          <ModelEvaluation evaluation={evaluation} />
        </div>

        <div className="mt-8">
          <TournamentSimulation
            simulation={tournamentSimulation}
            loading={simulationLoading}
            onRun={handleRunTournamentSimulation}
          />
        </div>

        <div className="mt-8">
          <PredictionHistory history={history} />
        </div>
      </section>
    </main>
  );
}
