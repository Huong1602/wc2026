from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

MATCHES_FILE = RAW_DATA_DIR / "matches.csv"
RANKINGS_FILE = RAW_DATA_DIR / "rankings.csv"
SAMPLE_MATCHES_FILE = RAW_DATA_DIR / "sample_matches.csv"
SAMPLE_RANKINGS_FILE = RAW_DATA_DIR / "sample_fifa_rankings.csv"
TRAINING_DATA_FILE = PROCESSED_DATA_DIR / "training_dataset.csv"
CLASSIFIER_FILE = MODELS_DIR / "result_classifier.joblib"
REGRESSOR_FILE = MODELS_DIR / "score_regressor.joblib"
METRICS_FILE = REPORTS_DIR / "training_metrics.json"
EDA_REPORT_FILE = REPORTS_DIR / "eda_summary.json"
PREDICTION_OUTPUT_FILE = REPORTS_DIR / "latest_prediction.json"
WORLDCUP_GROUPS_FILE = RAW_DATA_DIR / "worldcup_2026_groups.csv"
WORLDCUP_FIXTURES_FILE = RAW_DATA_DIR / "worldcup_2026_group_fixtures.csv"
WORLDCUP_KNOCKOUT_TEMPLATE_FILE = RAW_DATA_DIR / "worldcup_2026_knockout_template.csv"
GROUP_STAGE_SIMULATION_FILE = REPORTS_DIR / "group_stage_simulation.json"
KNOCKOUT_BRACKET_FILE = REPORTS_DIR / "knockout_bracket_prediction.json"
CHAMPION_PROBABILITIES_FILE = REPORTS_DIR / "champion_probabilities.json"

INTERNATIONAL_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

HOST_TEAMS_2026 = {"United States", "Canada", "Mexico"}
