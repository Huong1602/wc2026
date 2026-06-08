import { getModelMetrics } from "../services/modelService.js";
import { sendError, sendSuccess } from "../utils/response.js";

export async function getMetrics(request, response) {
  try {
    const metrics = await getModelMetrics();
    return sendSuccess(response, metrics);
  } catch (error) {
    return sendError(response, error.message);
  }
}
