import { spawn } from "node:child_process";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";

import { getMlDirectory } from "./mlDataService.js";

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

async function readJsonReport(fileName) {
  const filePath = path.join(getMlDirectory(), "reports", fileName);
  const content = await fsp.readFile(filePath, "utf-8");
  return JSON.parse(content);
}

export async function getTournamentSimulation() {
  try {
    const [championProbabilities, groupStage, knockoutBracket] = await Promise.all([
      readJsonReport("champion_probabilities.json"),
      readJsonReport("group_stage_simulation.json"),
      readJsonReport("knockout_bracket_prediction.json"),
    ]);

    return {
      championProbabilities,
      groupStage,
      knockoutBracket,
    };
  } catch (error) {
    const wrappedError = new Error("Tournament simulation reports are not generated yet. Run simulation first.");
    wrappedError.statusCode = 404;
    throw wrappedError;
  }
}

export function runTournamentSimulation(simulations = 10_000) {
  const safeSimulations = Math.max(1, Math.min(Number(simulations) || 10_000, 50_000));

  return new Promise((resolve, reject) => {
    const child = spawn(
      getPythonExecutable(),
      ["-m", "src.tournament_simulator", "--simulations", String(safeSimulations)],
      {
        cwd: getMlDirectory(),
        shell: false,
      }
    );

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", reject);

    child.on("close", async (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Tournament simulation failed with exit code ${code}`));
        return;
      }

      try {
        const lines = stdout.trim().split(/\r?\n/);
        const summary = JSON.parse(lines[lines.length - 1]);
        const reports = await getTournamentSimulation();
        resolve({
          summary,
          ...reports,
        });
      } catch (error) {
        reject(new Error(`Could not parse tournament simulation output: ${stdout}`));
      }
    });
  });
}

