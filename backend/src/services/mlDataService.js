import fs from "node:fs/promises";
import path from "node:path";

function getProjectRoot() {
  return path.resolve(process.cwd(), "..");
}

export function getMlDirectory() {
  return process.env.ML_DIR || path.join(getProjectRoot(), "ml");
}

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let inQuotes = false;

  for (const character of line) {
    if (character === '"') {
      inQuotes = !inQuotes;
    } else if (character === "," && !inQuotes) {
      values.push(current);
      current = "";
    } else {
      current += character;
    }
  }

  values.push(current);
  return values.map((value) => value.trim());
}

async function readCsv(filePath) {
  const content = await fs.readFile(filePath, "utf-8");
  const [headerLine, ...lines] = content.trim().split(/\r?\n/);
  const headers = parseCsvLine(headerLine);

  return lines.map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] || ""]));
  });
}

export async function listMlTeams() {
  const groupsPath = path.join(getMlDirectory(), "data", "raw", "worldcup_2026_groups.csv");
  const rankingsPath = path.join(getMlDirectory(), "data", "raw", "rankings.csv");
  const [groups, rankings] = await Promise.all([readCsv(groupsPath), readCsv(rankingsPath)]);

  const latestRankingByTeam = new Map();
  for (const row of rankings) {
    const existing = latestRankingByTeam.get(row.team);
    if (!existing || row.date > existing.date) {
      latestRankingByTeam.set(row.team, row);
    }
  }

  return groups.map((row, index) => {
    const name = row.team;
    const ranking = latestRankingByTeam.get(name);
    return {
      id: index + 1,
      name,
      group: row.group,
      slot: row.slot,
      confederation: "N/A",
      rank: ranking ? Number(ranking.rank) : null,
      points: ranking ? Number(ranking.points) : null,
      source: "worldcup_2026",
    };
  });
}

export async function isWorldCupTeam(teamName) {
  const teams = await listMlTeams();
  return teams.some((team) => team.name.toLowerCase() === String(teamName).trim().toLowerCase());
}
