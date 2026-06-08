import argparse
import json
from datetime import date

import joblib
import pandas as pd

from src.config import CLASSIFIER_FILE, PREDICTION_OUTPUT_FILE, REGRESSOR_FILE
from src.data_processing import load_matches, load_rankings
from src.features import make_match_features


LABEL_TO_OUTPUT_KEY = {
    "home_win": "homeWin",
    "draw": "draw",
    "away_win": "awayWin",
}


def predict_match(
    home_team: str,
    away_team: str,
    match_date: str | None = None,
    neutral: bool = True,
    country: str = "United States",
    tournament: str = "FIFA World Cup",
) -> dict:
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
        tournament=tournament,
    )
    feature_frame = pd.DataFrame([{column: features[column] for column in feature_columns}])

    probabilities = model.predict_proba(feature_frame)[0]
    labels = label_encoder.inverse_transform(range(len(probabilities)))
    probability_map = {"homeWin": 0.0, "draw": 0.0, "awayWin": 0.0}
    for label, probability in zip(labels, probabilities):
        probability_map[LABEL_TO_OUTPUT_KEY[label]] = float(probability)

    score_prediction = {"home": 0, "away": 0}
    if REGRESSOR_FILE.exists():
        regressor_artifact = joblib.load(REGRESSOR_FILE)
        score_model = regressor_artifact["model"]
        home_goals, away_goals = score_model.predict(feature_frame)[0]
        score_prediction = {
            "home": max(0, round(float(home_goals))),
            "away": max(0, round(float(away_goals))),
        }

    top_features = [
        item["feature"] if isinstance(item, dict) else str(item)
        for item in classifier_artifact.get("top_features", [])[:5]
    ]

    result = {
        "homeTeam": home_team,
        "awayTeam": away_team,
        "matchDate": prediction_date.date().isoformat(),
        "country": country,
        "neutral": neutral,
        "probabilities": probability_map,
        "predictedScore": score_prediction,
        "modelName": classifier_artifact["model_name"],
        "topFeatures": top_features,
        "featureValues": {column: float(feature_frame.iloc[0][column]) for column in feature_columns},
    }

    PREDICTION_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PREDICTION_OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict a football match result.")
    parser.add_argument("--home", required=True, help="Home or first team name")
    parser.add_argument("--away", required=True, help="Away or second team name")
    parser.add_argument("--date", default=None, help="Match date, format YYYY-MM-DD")
    parser.add_argument("--country", default="United States", help="Host country")
    parser.add_argument("--tournament", default="FIFA World Cup", help="Tournament name")
    parser.add_argument("--not-neutral", action="store_true", help="Mark match as not neutral")
    parser.add_argument("--text", action="store_true", help="Print human-readable output instead of JSON")
    args = parser.parse_args()

    result = predict_match(
        home_team=args.home,
        away_team=args.away,
        match_date=args.date,
        neutral=not args.not_neutral,
        country=args.country,
        tournament=args.tournament,
    )

    if args.text:
        probabilities = result["probabilities"]
        score = result["predictedScore"]
        print(f"{args.home} vs {args.away}")
        print(f"Model: {result['modelName']}")
        print(f"{args.home} thắng: {probabilities['homeWin'] * 100:.2f}%")
        print(f"Hòa: {probabilities['draw'] * 100:.2f}%")
        print(f"{args.away} thắng: {probabilities['awayWin'] * 100:.2f}%")
        print(f"Tỷ số dự đoán: {args.home} {score['home']} - {score['away']} {args.away}")
        print(f"Top features: {', '.join(result['topFeatures'])}")
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
