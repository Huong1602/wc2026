import pandas as pd

from src.config import MATCHES_FILE, RANKINGS_FILE, SAMPLE_MATCHES_FILE, SAMPLE_RANKINGS_FILE
from src.features import make_match_features


def load_matches(path=MATCHES_FILE) -> pd.DataFrame:
    if not path.exists():
        path = SAMPLE_MATCHES_FILE

    matches = pd.read_csv(path)
    required_columns = [
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "tournament",
        "country",
        "neutral",
    ]
    missing_columns = [column for column in required_columns if column not in matches.columns]
    if missing_columns:
        raise ValueError(f"Missing match columns: {', '.join(missing_columns)}")

    matches = matches[required_columns].copy()
    matches["date"] = pd.to_datetime(matches["date"])
    matches["home_team"] = matches["home_team"].astype(str).str.strip()
    matches["away_team"] = matches["away_team"].astype(str).str.strip()
    matches["country"] = matches["country"].astype(str).str.strip()
    matches["tournament"] = matches["tournament"].astype(str).str.strip()
    matches = matches.dropna(subset=["date", "home_team", "away_team", "home_score", "away_score"])
    matches["home_score"] = matches["home_score"].astype(int)
    matches["away_score"] = matches["away_score"].astype(int)
    matches["neutral"] = matches["neutral"].astype(str).str.lower().isin(["true", "1", "yes"])
    matches = matches.drop_duplicates(subset=["date", "home_team", "away_team"], keep="last")
    return matches.sort_values("date").reset_index(drop=True)


def load_rankings(path=RANKINGS_FILE) -> pd.DataFrame:
    if not path.exists():
        path = SAMPLE_RANKINGS_FILE

    rankings = pd.read_csv(path)
    required_columns = ["date", "team", "rank"]
    missing_columns = [column for column in required_columns if column not in rankings.columns]
    if missing_columns:
        raise ValueError(f"Missing ranking columns: {', '.join(missing_columns)}")

    rankings = rankings.copy()
    rankings["date"] = pd.to_datetime(rankings["date"])
    rankings["team"] = rankings["team"].astype(str).str.strip()
    rankings["rank"] = rankings["rank"].astype(float)
    if "points" not in rankings.columns:
        rankings["points"] = 0.0
    rankings = rankings.dropna(subset=["date", "team", "rank"])
    rankings = rankings.drop_duplicates(subset=["date", "team"], keep="last")
    return rankings.sort_values("date").reset_index(drop=True)


def get_result_label(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "home_win"
    if home_score < away_score:
        return "away_win"
    return "draw"


def build_training_dataset(matches: pd.DataFrame, rankings: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, match in matches.iterrows():
        features = make_match_features(
            home_team=match["home_team"],
            away_team=match["away_team"],
            match_date=match["date"],
            matches=matches,
            rankings=rankings,
            neutral=bool(match["neutral"]),
            country=match["country"],
            tournament=match["tournament"],
        )

        rows.append(
            {
                "date": match["date"],
                "home_team": match["home_team"],
                "away_team": match["away_team"],
                "tournament": match["tournament"],
                "country": match["country"],
                **features,
                "home_score": int(match["home_score"]),
                "away_score": int(match["away_score"]),
                "result": get_result_label(int(match["home_score"]), int(match["away_score"])),
            }
        )

    return pd.DataFrame(rows)
