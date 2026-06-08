import { Router } from "express";

import { getMetrics } from "../controllers/modelController.js";

const router = Router();

router.get("/metrics", getMetrics);

export default router;
