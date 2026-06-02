import { listMatches } from "../services/matchService.js";
import { sendError, sendSuccess } from "../utils/response.js";

export async function getMatches(request, response) {
  try {
    const matches = await listMatches();
    return sendSuccess(response, matches);
  } catch (error) {
    return sendError(response, error.message);
  }
}

