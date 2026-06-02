import { pool } from "../config/db.js";
import { findTeamByName } from "./teamService.js";

const HOST_TEAMS_2026 = new Set(["United States", "Canada", "Mexico"]);

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
    throw createBadRequest("matchDate không hợp lệ.");
  }

  return value.slice(0, 10);
}

function resultPoints(goalsFor, goalsAgainst) {
  if (goalsFor > goalsAgainst) return 3;
  if (goalsFor === goalsAgainst) return 1;
  return 0;
}

function average(values, fallback = 0) {
  if (!values.length) {
    return fallback;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

async function getLatestRank(teamId, matchDate) {
  const result = await pool.query(
    `
      SELECT rank
      FROM fifa_rankings
      WHERE team_id = $1 AND ranking_date <= $2
      ORDER BY ranking_date DESC
      LIMIT 1
    `,
    [teamId, matchDate]
  );

  return Number(result.rows[0]?.rank || 50);
}

async function getRecentStats(teamId, matchDate) {
  const result = await pool.query(
    `
      SELECT home_team_id, away_team_id, home_score, away_score
      FROM matches
      WHERE match_date < $1
      AND (home_team_id = $2 OR away_team_id = $2)
      ORDER BY match_date DESC
      LIMIT 5
    `,
    [matchDate, teamId]
  );

  const points = [];
  const goalDiffs = [];
  const goalsFor = [];

  for (const match of result.rows) {
    const isHome = match.home_team_id === teamId;
    const teamGoals = Number(isHome ? match.home_score : match.away_score);
    const opponentGoals = Number(isHome ? match.away_score : match.home_score);

    points.push(resultPoints(teamGoals, opponentGoals));
    goalDiffs.push(teamGoals - opponentGoals);
    goalsFor.push(teamGoals);
  }

  return {
    points: average(points, 1),
    goalDiff: average(goalDiffs, 0),
    goalsFor: average(goalsFor, 1),
  };
}

async function getHeadToHeadPoints(homeTeamId, awayTeamId, matchDate) {
  const result = await pool.query(
    `
      SELECT home_team_id, away_team_id, home_score, away_score
      FROM matches
      WHERE match_date < $1
      AND (
        (home_team_id = $2 AND away_team_id = $3)
        OR (home_team_id = $3 AND away_team_id = $2)
      )
      ORDER BY match_date DESC
      LIMIT 5
    `,
    [matchDate, homeTeamId, awayTeamId]
  );

  const points = result.rows.map((match) => {
    if (match.home_team_id === homeTeamId) {
      return resultPoints(Number(match.home_score), Number(match.away_score));
    }

    return resultPoints(Number(match.away_score), Number(match.home_score));
  });

  return average(points, 1);
}

function softmax(scores) {
  const maxScore = Math.max(...scores);
  const exponents = scores.map((score) => Math.exp(score - maxScore));
  const total = exponents.reduce((sum, value) => sum + value, 0);
  return exponents.map((value) => value / total);
}

function buildPredictionScores(features) {
  const rankSignal = (features.awayRank - features.homeRank) / 25;
  const formSignal = (features.homeRecent.points - features.awayRecent.points) / 3;
  const goalDiffSignal = (features.homeRecent.goalDiff - features.awayRecent.goalDiff) / 4;
  const h2hSignal = (features.headToHeadPoints - 1) / 3;
  const hostSignal = features.homeHostAdvantage - features.awayHostAdvantage;

  const advantage = rankSignal + formSignal + goalDiffSignal + h2hSignal + hostSignal;
  const drawScore = 0.65 - Math.abs(advantage) * 0.35;

  return {
    home: advantage,
    draw: drawScore,
    away: -advantage,
  };
}

function buildPredictedScore(probabilities, features) {
  const homeAttack = features.homeRecent.goalsFor + probabilities.homeWin * 1.2 + features.homeHostAdvantage * 0.4;
  const awayAttack = features.awayRecent.goalsFor + probabilities.awayWin * 1.2 + features.awayHostAdvantage * 0.4;

  return {
    homeScore: Math.max(0, Math.round(homeAttack)),
    awayScore: Math.max(0, Math.round(awayAttack)),
  };
}

export async function createMatchPrediction(payload) {
  const homeTeamName = String(payload.homeTeam || "").trim();
  const awayTeamName = String(payload.awayTeam || "").trim();
  const matchDate = normalizeDate(payload.matchDate);
  const country = String(payload.country || "United States").trim();
  const neutral = payload.neutral !== false;

  if (!homeTeamName || !awayTeamName) {
    throw createBadRequest("homeTeam và awayTeam là bắt buộc.");
  }

  if (homeTeamName.toLowerCase() === awayTeamName.toLowerCase()) {
    throw createBadRequest("Hai đội không được trùng nhau.");
  }

  const homeTeam = await findTeamByName(homeTeamName);
  const awayTeam = await findTeamByName(awayTeamName);

  if (!homeTeam || !awayTeam) {
    throw createBadRequest("Đội tuyển chưa có trong dữ liệu mẫu.");
  }

  const [homeRank, awayRank, homeRecent, awayRecent, headToHeadPoints] = await Promise.all([
    getLatestRank(homeTeam.id, matchDate),
    getLatestRank(awayTeam.id, matchDate),
    getRecentStats(homeTeam.id, matchDate),
    getRecentStats(awayTeam.id, matchDate),
    getHeadToHeadPoints(homeTeam.id, awayTeam.id, matchDate),
  ]);

  const features = {
    homeRank,
    awayRank,
    homeRecent,
    awayRecent,
    headToHeadPoints,
    homeHostAdvantage: HOST_TEAMS_2026.has(homeTeam.name) && country === homeTeam.name ? 0.2 : 0,
    awayHostAdvantage: HOST_TEAMS_2026.has(awayTeam.name) && country === awayTeam.name ? 0.2 : 0,
  };

  const scores = buildPredictionScores(features);
  const [homeWin, draw, awayWin] = softmax([scores.home, scores.draw, scores.away]);
  const probabilities = {
    homeWin,
    draw,
    awayWin,
  };
  const predictedScore = buildPredictedScore(probabilities, features);

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
      homeWin,
      draw,
      awayWin,
      predictedScore.homeScore,
      predictedScore.awayScore,
    ]
  );

  return {
    id: insertResult.rows[0].id,
    homeTeam: homeTeam.name,
    awayTeam: awayTeam.name,
    matchDate,
    country,
    neutral,
    probabilities,
    predictedScore,
    features: {
      homeRank,
      awayRank,
      rankDiff: homeRank - awayRank,
      homeRecent,
      awayRecent,
      headToHeadPoints,
    },
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

