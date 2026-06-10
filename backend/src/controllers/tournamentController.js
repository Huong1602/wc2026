import { getTournamentSimulation, runTournamentSimulation } from "../services/tournamentService.js";
import { sendError, sendSuccess } from "../utils/response.js";

export async function getSimulation(request, response) {
  try {
    const simulation = await getTournamentSimulation();
    return sendSuccess(response, simulation);
  } catch (error) {
    return sendError(response, error.message, error.statusCode || 500);
  }
}

export async function simulateTournament(request, response) {
  try {
    const simulations = request.body?.simulations || request.query?.simulations || 10_000;
    const simulation = await runTournamentSimulation(simulations);
    return sendSuccess(response, simulation);
  } catch (error) {
    return sendError(response, error.message, error.statusCode || 500);
  }
}

