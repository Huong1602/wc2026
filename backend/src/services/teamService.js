import { pool } from "../config/db.js";
import { listMlTeams } from "./mlDataService.js";

export async function listTeams() {
  return listMlTeams();
}

export async function findTeamByName(name) {
  const result = await pool.query(
    "SELECT id, name, confederation FROM teams WHERE LOWER(name) = LOWER($1)",
    [name]
  );

  return result.rows[0] || null;
}

export async function findOrCreateTeamByName(name) {
  const existingTeam = await findTeamByName(name);
  if (existingTeam) {
    return existingTeam;
  }

  const result = await pool.query(
    `
      INSERT INTO teams (name, confederation)
      VALUES ($1, $2)
      ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
      RETURNING id, name, confederation
    `,
    [name, "N/A"]
  );

  return result.rows[0];
}
