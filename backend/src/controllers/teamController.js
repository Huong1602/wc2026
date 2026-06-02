import { listTeams } from "../services/teamService.js";
import { sendError, sendSuccess } from "../utils/response.js";

export async function getTeams(request, response) {
  try {
    const teams = await listTeams();
    return sendSuccess(response, teams);
  } catch (error) {
    return sendError(response, error.message);
  }
}

