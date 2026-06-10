import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

import { pool } from "../config/db.js";
import { isWorldCupTeam } from "./mlDataService.js";
import { findOrCreateTeamByName } from "./teamService.js";

function createBadRequest(message) {
  const error = new Error(message);
  error.statusCode = 400;
  return error;
}

function normalizeDate(value) {
  if (!value) {
    return "2026-06-15";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw createBadRequest("matchDate is invalid.");
  }

  return value.slice(0, 10);
}

function getProjectRoot() {
  return path.resolve(process.cwd(), "..");
}

function getMlDirectory() {
  return process.env.ML_DIR || path.join(getProjectRoot(), "ml");
}

function getPythonExecutable() {
  if (process.env.PYTHON_EXECUTABLE) {
    return process.env.PYTHON_EXECUTABLE;
  }

  const mlDirectory = getMlDirectory();
  const windowsVenvPython = path.join(mlDirectory, ".venv", "Scripts", "python.exe");
  if (fs.existsSync(windowsVenvPython)) {
    return windowsVenvPython;
  }

  return process.platform === "win32" ? "python" : "python3";
}

function runPythonPrediction(payload) {
  const mlDirectory = getMlDirectory();
  const args = [
    "-m",
    "src.predict",
    "--home",
    payload.homeTeam,
    "--away",
    payload.awayTeam,
    "--date",
    payload.matchDate,
    "--country",
    payload.country,
    "--tournament",
    payload.tournament || "FIFA World Cup",
  ];

  if (payload.neutral === false) {
    args.push("--not-neutral");
  }

  return new Promise((resolve, reject) => {
    const child = spawn(getPythonExecutable(), args, {
      cwd: mlDirectory,
      shell: false,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", (error) => {
      reject(error);
    });

    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Python prediction failed with exit code ${code}`));
        return;
      }

      try {
        const lines = stdout.trim().split(/\r?\n/);
        resolve(JSON.parse(lines[lines.length - 1]));
      } catch (error) {
        reject(new Error(`Could not parse ML prediction output: ${stdout}`));
      }
    });
  });
}

export async function createMatchPrediction(payload) {
  const homeTeamName = String(payload.homeTeam || "").trim();
  const awayTeamName = String(payload.awayTeam || "").trim();
  const matchDate = normalizeDate(payload.matchDate);
  const country = String(payload.country || "United States").trim();
  const neutral = payload.neutral !== false;
  const tournament = String(payload.tournament || "FIFA World Cup").trim();

  if (!homeTeamName || !awayTeamName) {
    throw createBadRequest("homeTeam and awayTeam are required.");
  }

  if (homeTeamName.toLowerCase() === awayTeamName.toLowerCase()) {
    throw createBadRequest("Two teams must be different.");
  }

  const [homeIsWorldCupTeam, awayIsWorldCupTeam] = await Promise.all([
    isWorldCupTeam(homeTeamName),
    isWorldCupTeam(awayTeamName),
  ]);

  if (!homeIsWorldCupTeam || !awayIsWorldCupTeam) {
    throw createBadRequest("Only FIFA World Cup 2026 teams are supported in this demo.");
  }

  const homeTeam = await findOrCreateTeamByName(homeTeamName);
  const awayTeam = await findOrCreateTeamByName(awayTeamName);

  const mlPrediction = await runPythonPrediction({
    homeTeam: homeTeam.name,
    awayTeam: awayTeam.name,
    matchDate,
    country,
    neutral,
    tournament,
  });

  const insertResult = await pool.query(
    `
      INSERT INTO predictions (
        home_team_id,
        away_team_id,
        match_date,
        country,
        neutral,
        home_win_probability,
        draw_probability,
        away_win_probability,
        predicted_home_score,
        predicted_away_score
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING id, created_at AS "createdAt"
    `,
    [
      homeTeam.id,
      awayTeam.id,
      matchDate,
      country,
      neutral,
      mlPrediction.probabilities.homeWin,
      mlPrediction.probabilities.draw,
      mlPrediction.probabilities.awayWin,
      mlPrediction.predictedScore.home,
      mlPrediction.predictedScore.away,
    ]
  );

  return {
    id: insertResult.rows[0].id,
    ...mlPrediction,
    createdAt: insertResult.rows[0].createdAt,
  };
}

export async function listPredictions(limit = 10) {
  const result = await pool.query(
    `
      SELECT
        predictions.id,
        home_team.name AS "homeTeam",
        away_team.name AS "awayTeam",
        predictions.match_date AS "matchDate",
        predictions.country,
        predictions.neutral,
        predictions.home_win_probability AS "homeWinProbability",
        predictions.draw_probability AS "drawProbability",
        predictions.away_win_probability AS "awayWinProbability",
        predictions.predicted_home_score AS "predictedHomeScore",
        predictions.predicted_away_score AS "predictedAwayScore",
        predictions.created_at AS "createdAt"
      FROM predictions
      JOIN teams AS home_team ON home_team.id = predictions.home_team_id
      JOIN teams AS away_team ON away_team.id = predictions.away_team_id
      ORDER BY predictions.created_at DESC
      LIMIT $1
    `,
    [limit]
  );

  return result.rows;
}
