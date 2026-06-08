import fs from "node:fs/promises";
import path from "node:path";

function getProjectRoot() {
  return path.resolve(process.cwd(), "..");
}

function getMlDirectory() {
  return process.env.ML_DIR || path.join(getProjectRoot(), "ml");
}

export async function getModelMetrics() {
  const metricsPath = path.join(getMlDirectory(), "reports", "training_metrics.json");
  const edaPath = path.join(getMlDirectory(), "reports", "eda_summary.json");

  const [metricsContent, edaContent] = await Promise.all([
    fs.readFile(metricsPath, "utf-8"),
    fs.readFile(edaPath, "utf-8").catch(() => "{}"),
  ]);

  return {
    metrics: JSON.parse(metricsContent),
    eda: JSON.parse(edaContent),
  };
}
