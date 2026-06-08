import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import EDA_REPORT_FILE, FIGURES_DIR, REPORTS_DIR
from src.data_processing import get_result_label, load_matches, load_rankings


def save_countplot(data: pd.DataFrame, x: str, title: str, path) -> None:
    plt.figure(figsize=(8, 5))
    sns.countplot(data=data, x=x, order=data[x].value_counts().index)
    plt.title(title)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def run_eda() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    matches = load_matches()
    rankings = load_rankings()
    matches["result"] = matches.apply(
        lambda row: get_result_label(int(row["home_score"]), int(row["away_score"])),
        axis=1,
    )
    matches["total_goals"] = matches["home_score"] + matches["away_score"]
    matches["goal_diff"] = matches["home_score"] - matches["away_score"]

    save_countplot(matches, "result", "Distribution of match results", FIGURES_DIR / "result_distribution.png")

    plt.figure(figsize=(9, 5))
    sns.histplot(matches["total_goals"], bins=12, kde=False)
    plt.title("Total goals per match")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "total_goals_distribution.png")
    plt.close()

    tournament_summary = (
        matches.groupby("tournament")
        .agg(matches=("date", "count"), avg_goals=("total_goals", "mean"), draw_rate=("result", lambda values: (values == "draw").mean()))
        .sort_values("matches", ascending=False)
        .head(10)
        .reset_index()
    )

    home_advantage = {
        "non_neutral_home_win_rate": float(matches.loc[~matches["neutral"], "result"].eq("home_win").mean()),
        "neutral_home_win_rate": float(matches.loc[matches["neutral"], "result"].eq("home_win").mean()),
    }

    summary = {
        "rows": int(len(matches)),
        "date_min": matches["date"].min().date().isoformat(),
        "date_max": matches["date"].max().date().isoformat(),
        "teams": int(pd.unique(pd.concat([matches["home_team"], matches["away_team"]])).size),
        "result_distribution": matches["result"].value_counts(normalize=True).round(4).to_dict(),
        "average_total_goals": float(matches["total_goals"].mean()),
        "home_advantage": home_advantage,
        "top_tournaments": tournament_summary.to_dict(orient="records"),
        "ranking_rows": int(len(rankings)),
        "ranking_note": "rankings.csv is Elo-derived when official FIFA historical CSV is unavailable.",
        "conclusions": [
            "Draws are usually a minority class, so macro F1 is more informative than accuracy alone.",
            "Non-neutral games generally show stronger home advantage than neutral games.",
            "Ranking/strength features should be combined with recent form because team strength changes over time.",
        ],
    }

    with open(EDA_REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print(f"Saved EDA summary: {EDA_REPORT_FILE}")
    print(f"Saved figures: {FIGURES_DIR}")


if __name__ == "__main__":
    run_eda()

