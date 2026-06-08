import math

from src.config import CLASSIFIER_FILE, METRICS_FILE, REGRESSOR_FILE, TRAINING_DATA_FILE
from src.data_processing import load_matches, load_rankings
from src.predict import predict_match


def validate_data() -> None:
    matches = load_matches()
    rankings = load_rankings()

    required_match_columns = ["date", "home_team", "away_team", "home_score", "away_score", "tournament", "country", "neutral"]
    required_ranking_columns = ["date", "team", "rank"]

    assert not matches[required_match_columns].isnull().any().any(), "matches contains null values"
    assert not rankings[required_ranking_columns].isnull().any().any(), "rankings contains null values"
    assert not matches.duplicated(subset=["date", "home_team", "away_team"]).any(), "matches contains duplicates"

    teams_in_matches = set(matches["home_team"]) | set(matches["away_team"])
    teams_in_rankings = set(rankings["team"])
    missing_teams = teams_in_matches - teams_in_rankings
    assert not missing_teams, f"teams missing rankings: {sorted(list(missing_teams))[:10]}"


def validate_artifacts() -> None:
    for path in [CLASSIFIER_FILE, REGRESSOR_FILE, METRICS_FILE, TRAINING_DATA_FILE]:
        assert path.exists(), f"missing artifact: {path}"


def validate_prediction() -> None:
    prediction = predict_match("France", "Japan", "2026-06-15")
    probabilities = prediction["probabilities"]
    total_probability = probabilities["homeWin"] + probabilities["draw"] + probabilities["awayWin"]
    assert math.isclose(total_probability, 1.0, rel_tol=1e-6), "probabilities do not sum to 1"
    assert prediction["modelName"], "modelName is missing"
    assert prediction["topFeatures"], "topFeatures is missing"


def main() -> None:
    validate_data()
    validate_artifacts()
    validate_prediction()
    print("Validation passed: data, artifacts, and prediction contract are valid.")


if __name__ == "__main__":
    main()

