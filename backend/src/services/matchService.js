import { pool } from "../config/db.js";

export async function listMatches(limit = 20) {
  const result = await pool.query(
    `
      SELECT
        matches.id,
        matches.match_date AS "matchDate",
        matches.tournament,
        home_team.name AS "homeTeam",
        away_team.name AS "awayTeam",
        matches.home_score AS "homeScore",
        matches.away_score AS "awayScore",
        matches.country,
        matches.neutral
      FROM matches
      JOIN teams AS home_team ON home_team.id = matches.home_team_id
      JOIN teams AS away_team ON away_team.id = matches.away_team_id
      ORDER BY matches.match_date DESC
      LIMIT $1
    `,
    [limit]
  );

  return result.rows;
}

