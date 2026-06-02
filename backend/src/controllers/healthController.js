import { pool } from "../config/db.js";
import { sendError, sendSuccess } from "../utils/response.js";

export async function getHealth(request, response) {
  try {
    await pool.query("SELECT 1");
    return sendSuccess(response, {
      status: "ok",
      database: "connected",
    });
  } catch (error) {
    return sendError(response, error.message);
  }
}

