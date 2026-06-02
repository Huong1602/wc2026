import { createMatchPrediction, listPredictions } from "../services/predictionService.js";
import { sendError, sendSuccess } from "../utils/response.js";

export async function getPredictions(request, response) {
  try {
    const predictions = await listPredictions();
    return sendSuccess(response, predictions);
  } catch (error) {
    return sendError(response, error.message);
  }
}

export async function createPrediction(request, response) {
  try {
    const prediction = await createMatchPrediction(request.body);
    return sendSuccess(response, prediction, 201);
  } catch (error) {
    const statusCode = error.statusCode || 500;
    return sendError(response, error.message, statusCode);
  }
}

