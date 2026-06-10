import { Router } from "express";

import { getSimulation, simulateTournament } from "../controllers/tournamentController.js";

const router = Router();

router.get("/simulation", getSimulation);
router.post("/simulate", simulateTournament);

export default router;

