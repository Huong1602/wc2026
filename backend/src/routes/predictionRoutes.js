import { Router } from "express";

import { createPrediction, getPredictions } from "../controllers/predictionController.js";

const router = Router();

router.get("/", getPredictions);
router.post("/", createPrediction);

export default router;

