import cors from "cors";
import express from "express";

import healthRoutes from "./routes/healthRoutes.js";
import matchRoutes from "./routes/matchRoutes.js";
import modelRoutes from "./routes/modelRoutes.js";
import predictionRoutes from "./routes/predictionRoutes.js";
import teamRoutes from "./routes/teamRoutes.js";
import tournamentRoutes from "./routes/tournamentRoutes.js";

const app = express();

app.use(
  cors({
    origin: process.env.CLIENT_ORIGIN || "http://localhost:5173",
  })
);
app.use(express.json());

app.use("/api/health", healthRoutes);
app.use("/api/teams", teamRoutes);
app.use("/api/matches", matchRoutes);
app.use("/api/model", modelRoutes);
app.use("/api/predictions", predictionRoutes);
app.use("/api/tournament", tournamentRoutes);

app.use((request, response) => {
  response.status(404).json({
    success: false,
    error: `Route not found: ${request.method} ${request.originalUrl}`,
  });
});

export default app;
