import argparse
from datetime import date

import joblib
import pandas as pd

from src.config import CLASSIFIER_FILE, REGRESSOR_FILE
from src.data_processing import load_matches, load_rankings
from src.features import make_match_features


def predict_match(home_team: str, away_team: str, match_date: str | None = None, neutral: bool = True, country: str = "") -> dict:
    prediction_date = pd.to_datetime(match_date or date.today().isoformat())
    matches = load_matches()
    rankings = load_rankings()

    classifier_artifact = joblib.load(CLASSIFIER_FILE)
    model = classifier_artifact["model"]
    label_encoder = classifier_artifact["label_encoder"]
    feature_columns = classifier_artifact["feature_columns"]

    features = make_match_features(
        home_team=home_team,
        away_team=away_team,
        match_date=prediction_date,
        matches=matches,
        rankings=rankings,
        neutral=neutral,
        country=country,
    )
    feature_frame = pd.DataFrame([{column: features[column] for column in feature_columns}])

    probabilities = model.predict_proba(feature_frame)[0]
    labels = label_encoder.inverse_transform(range(len(probabilities)))
    probability_map = {label: float(probability) for label, probability in zip(labels, probabilities)}

    score_prediction = None
    if REGRESSOR_FILE.exists():
        regressor_artifact = joblib.load(REGRESSOR_FILE)
        score_model = regressor_artifact["model"]
        home_goals, away_goals = score_model.predict(feature_frame)[0]
        score_prediction = {
            "home_score": max(0, round(float(home_goals))),
            "away_score": max(0, round(float(away_goals))),
        }

    return {
        "home_team": home_team,
        "away_team": away_team,
        "model_name": classifier_artifact["model_name"],
        "probabilities": probability_map,
        "score_prediction": score_prediction,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict a football match result.")
    parser.add_argument("--home", required=True, help="Home or first team name")
    parser.add_argument("--away", required=True, help="Away or second team name")
    parser.add_argument("--date", default=None, help="Match date, format YYYY-MM-DD")
    parser.add_argument("--country", default="", help="Host country")
    parser.add_argument("--not-neutral", action="store_true", help="Mark match as not neutral")
    args = parser.parse_args()

    result = predict_match(
        home_team=args.home,
        away_team=args.away,
        match_date=args.date,
        neutral=not args.not_neutral,
        country=args.country,
    )

    probabilities = result["probabilities"]
    print(f"{args.home} vs {args.away}")
    print(f"Model: {result['model_name']}")
    print(f"{args.home} thắng: {probabilities.get('home_win', 0.0) * 100:.2f}%")
    print(f"Hòa: {probabilities.get('draw', 0.0) * 100:.2f}%")
    print(f"{args.away} thắng: {probabilities.get('away_win', 0.0) * 100:.2f}%")

    if result["score_prediction"]:
        score = result["score_prediction"]
        print(f"Tỷ số dự đoán: {args.home} {score['home_score']} - {score['away_score']} {args.away}")


if __name__ == "__main__":
    main()

