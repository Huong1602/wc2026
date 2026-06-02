import json

import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from src.config import CLASSIFIER_FILE, METRICS_FILE, MODELS_DIR, PROCESSED_DATA_DIR, REGRESSOR_FILE, TRAINING_DATA_FILE
from src.data_processing import build_training_dataset, load_matches, load_rankings


FEATURE_COLUMNS = [
    "home_rank",
    "away_rank",
    "rank_diff",
    "home_recent_points",
    "away_recent_points",
    "recent_points_diff",
    "home_recent_goal_diff",
    "away_recent_goal_diff",
    "recent_goal_diff_delta",
    "home_recent_goals_for",
    "away_recent_goals_for",
    "h2h_home_points",
    "neutral",
    "home_is_2026_host",
    "away_is_2026_host",
]


def get_candidate_models() -> dict:
    models = {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, random_state=42)),
            ]
        ),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
    }

    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.08,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
        )
    except ImportError:
        pass

    return models


def train() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    matches = load_matches()
    rankings = load_rankings()
    dataset = build_training_dataset(matches, rankings)
    dataset.to_csv(TRAINING_DATA_FILE, index=False)

    x = dataset[FEATURE_COLUMNS]
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(dataset["result"])

    class_counts = dataset["result"].value_counts()
    stratify_target = y if len(dataset) >= 8 and class_counts.min() >= 2 else None

    if len(dataset) >= 8:
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=0.25,
            random_state=42,
            stratify=stratify_target,
        )
    else:
        x_train, x_test, y_train, y_test = x, x, y, y

    metrics = {}
    best_model_name = None
    best_model = None
    best_accuracy = -1.0

    for model_name, model in get_candidate_models().items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        metrics[model_name] = {
            "accuracy": float(accuracy),
            "classification_report": classification_report(
                y_test,
                predictions,
                labels=list(range(len(label_encoder.classes_))),
                target_names=label_encoder.classes_,
                output_dict=True,
                zero_division=0,
            ),
        }

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model_name = model_name
            best_model = model

    score_regressor = RandomForestRegressor(n_estimators=200, random_state=42)
    score_regressor.fit(x, dataset[["home_score", "away_score"]])

    joblib.dump(
        {
            "model": best_model,
            "model_name": best_model_name,
            "label_encoder": label_encoder,
            "feature_columns": FEATURE_COLUMNS,
        },
        CLASSIFIER_FILE,
    )
    joblib.dump(
        {
            "model": score_regressor,
            "feature_columns": FEATURE_COLUMNS,
        },
        REGRESSOR_FILE,
    )

    metrics["best_model"] = best_model_name
    with open(METRICS_FILE, "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    print(f"Saved classifier: {CLASSIFIER_FILE}")
    print(f"Saved score regressor: {REGRESSOR_FILE}")
    print(f"Saved metrics: {METRICS_FILE}")
    print(f"Best model: {best_model_name} ({best_accuracy:.3f} accuracy)")


if __name__ == "__main__":
    train()
