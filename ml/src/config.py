from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

MATCHES_FILE = RAW_DATA_DIR / "sample_matches.csv"
RANKINGS_FILE = RAW_DATA_DIR / "sample_fifa_rankings.csv"
TRAINING_DATA_FILE = PROCESSED_DATA_DIR / "training_dataset.csv"
CLASSIFIER_FILE = MODELS_DIR / "result_classifier.joblib"
REGRESSOR_FILE = MODELS_DIR / "score_regressor.joblib"
METRICS_FILE = REPORTS_DIR / "training_metrics.json"

HOST_TEAMS_2026 = {"United States", "Canada", "Mexico"}

