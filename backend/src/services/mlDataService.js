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
  const matchesPath = path.join(getMlDirectory(), "data", "raw", "matches.csv");
  const rankingsPath = path.join(getMlDirectory(), "data", "raw", "rankings.csv");
  const [matches, rankings] = await Promise.all([readCsv(matchesPath), readCsv(rankingsPath)]);

  const latestRankingByTeam = new Map();
  for (const row of rankings) {
    const existing = latestRankingByTeam.get(row.team);
    if (!existing || row.date > existing.date) {
      latestRankingByTeam.set(row.team, row);
    }
  }

  const teamNames = new Set();
  for (const row of matches) {
    if (row.home_team) teamNames.add(row.home_team);
    if (row.away_team) teamNames.add(row.away_team);
  }

  return [...teamNames].sort((left, right) => left.localeCompare(right)).map((name, index) => {
    const ranking = latestRankingByTeam.get(name);
    return {
      id: index + 1,
      name,
      confederation: "N/A",
      rank: ranking ? Number(ranking.rank) : null,
      points: ranking ? Number(ranking.points) : null,
      source: "ml_dataset",
    };
  });
}

