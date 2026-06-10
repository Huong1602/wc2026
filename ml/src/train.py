import json

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
    mean_absolute_error,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

from src.config import (
    CLASSIFIER_FILE,
    FIGURES_DIR,
    METRICS_FILE,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    REGRESSOR_FILE,
    TRAINING_DATA_FILE,
)
from src.data_processing import build_training_dataset, load_matches, load_rankings

TRAIN_START_DATE = "2000-01-01"
MAX_TRAINING_MATCHES = 6000


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
    "home_days_since_last_match",
    "away_days_since_last_match",
    "days_since_last_match_delta",
    "home_world_cup_points",
    "away_world_cup_points",
    "world_cup_points_diff",
    "tournament_importance",
]


def get_candidate_models(class_count: int) -> dict:
    models = {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=80,
            max_depth=10,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
        ),
    }

    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=160,
            max_depth=3,
            learning_rate=0.06,
            objective="multi:softprob",
            num_class=class_count,
            eval_metric="mlogloss",
            random_state=42,
        )
    except ImportError:
        pass

    return models


def time_based_split(dataset: pd.DataFrame, train_ratio: float = 0.8):
    dataset = dataset.sort_values("date").reset_index(drop=True)
    split_index = max(1, int(len(dataset) * train_ratio))
    if split_index >= len(dataset):
        split_index = len(dataset) - 1

    train_data = dataset.iloc[:split_index].copy()
    test_data = dataset.iloc[split_index:].copy()
    return train_data, test_data


def get_top_features(model, feature_columns: list[str], limit: int = 8) -> list[dict]:
    estimator = model.named_steps["model"] if isinstance(model, Pipeline) else model

    if hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        importances = abs(estimator.coef_).mean(axis=0)
    else:
        return []

    feature_importances = sorted(
        zip(feature_columns, importances),
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        {"feature": feature, "importance": float(importance)}
        for feature, importance in feature_importances[:limit]
    ]


def save_confusion_matrix(y_true, y_pred, labels: list[str], model_name: str) -> str:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(labels))))
    figure_path = FIGURES_DIR / f"confusion_matrix_{model_name}.png"

    plt.figure(figsize=(7, 5))
    sns.heatmap(matrix, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion Matrix - {model_name}")
    plt.tight_layout()
    plt.savefig(figure_path)
    plt.close()
    return str(figure_path)


def train() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    matches = load_matches()
    matches = matches[matches["date"] >= pd.Timestamp(TRAIN_START_DATE)].tail(MAX_TRAINING_MATCHES).reset_index(drop=True)
    rankings = load_rankings()
    dataset = build_training_dataset(matches, rankings)
    dataset.to_csv(TRAINING_DATA_FILE, index=False)

    label_encoder = LabelEncoder()
    dataset["target"] = label_encoder.fit_transform(dataset["result"])
    labels = list(label_encoder.classes_)

    train_data, test_data = time_based_split(dataset)
    x_train = train_data[FEATURE_COLUMNS]
    y_train = train_data["target"]
    x_test = test_data[FEATURE_COLUMNS]
    y_test = test_data["target"]

    metrics = {
        "dataset": {
            "rows": int(len(dataset)),
            "train_rows": int(len(train_data)),
            "test_rows": int(len(test_data)),
            "date_min": dataset["date"].min().date().isoformat(),
            "date_max": dataset["date"].max().date().isoformat(),
            "split": "time_based_80_20",
            "target_distribution": dataset["result"].value_counts(normalize=True).round(4).to_dict(),
        },
        "models": {},
    }
    best_model_name = None
    best_model = None
    best_score = -1.0
    trained_models = {}

    for model_name, model in get_candidate_models(len(labels)).items():
        model.fit(x_train, y_train)
        trained_models[model_name] = model
        predictions = model.predict(x_test)
        probabilities = model.predict_proba(x_test) if hasattr(model, "predict_proba") else None
        accuracy = accuracy_score(y_test, predictions)
        macro_f1 = classification_report(
            y_test,
            predictions,
            labels=list(range(len(labels))),
            target_names=labels,
            output_dict=True,
            zero_division=0,
        )["macro avg"]["f1-score"]

        model_metrics = {
            "accuracy": float(accuracy),
            "macro_f1": float(macro_f1),
            "classification_report": classification_report(
                y_test,
                predictions,
                labels=list(range(len(labels))),
                target_names=labels,
                output_dict=True,
                zero_division=0,
            ),
            "confusion_matrix_figure": save_confusion_matrix(y_test, predictions, labels, model_name),
            "top_features": get_top_features(model, FEATURE_COLUMNS),
        }

        if probabilities is not None:
            model_metrics["log_loss"] = float(log_loss(y_test, probabilities, labels=list(range(len(labels)))))

        metrics["models"][model_name] = model_metrics

        if macro_f1 > best_score:
            best_score = macro_f1
            best_model_name = model_name
            best_model = model

    score_regressor = RandomForestRegressor(n_estimators=80, max_depth=10, min_samples_leaf=3, random_state=42)
    score_regressor.fit(x_train, train_data[["home_score", "away_score"]])
    score_predictions = score_regressor.predict(x_test)
    metrics["score_regression"] = {
        "model": "random_forest_regressor",
        "home_score_mae": float(mean_absolute_error(test_data["home_score"], score_predictions[:, 0])),
        "away_score_mae": float(mean_absolute_error(test_data["away_score"], score_predictions[:, 1])),
    }

    joblib.dump(
        {
            "model": best_model,
            "models": trained_models,
            "model_name": best_model_name,
            "label_encoder": label_encoder,
            "feature_columns": FEATURE_COLUMNS,
            "top_features": get_top_features(best_model, FEATURE_COLUMNS),
        },
        CLASSIFIER_FILE,
        compress=3,
    )
    joblib.dump(
        {
            "model": score_regressor,
            "feature_columns": FEATURE_COLUMNS,
        },
        REGRESSOR_FILE,
        compress=3,
    )

    metrics["best_model"] = best_model_name
    with open(METRICS_FILE, "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    print(f"Saved classifier: {CLASSIFIER_FILE}")
    print(f"Saved score regressor: {REGRESSOR_FILE}")
    print(f"Saved metrics: {METRICS_FILE}")
    print(f"Best model: {best_model_name} ({best_score:.3f} macro F1)")


if __name__ == "__main__":
    train()
