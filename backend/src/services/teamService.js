import { pool } from "../config/db.js";

export async function listTeams() {
  const query = `
    SELECT
      teams.id,
      teams.name,
      teams.confederation,
      rankings.rank,
      rankings.points
    FROM teams
    LEFT JOIN LATERAL (
      SELECT rank, points
      FROM fifa_rankings
      WHERE fifa_rankings.team_id = teams.id
      ORDER BY ranking_date DESC
      LIMIT 1
    ) rankings ON TRUE
    ORDER BY teams.name ASC
  `;

  const result = await pool.query(query);
  return result.rows;
}

export async function findTeamByName(name) {
  const result = await pool.query(
    "SELECT id, name, confederation FROM teams WHERE LOWER(name) = LOWER($1)",
    [name]
  );

  return result.rows[0] || null;
}

