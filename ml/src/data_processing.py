import pandas as pd

from src.config import MATCHES_FILE, RANKINGS_FILE
from src.features import make_match_features


def load_matches(path=MATCHES_FILE) -> pd.DataFrame:
    matches = pd.read_csv(path)
    matches["date"] = pd.to_datetime(matches["date"])
    matches["neutral"] = matches["neutral"].astype(str).str.lower().isin(["true", "1", "yes"])
    return matches.sort_values("date").reset_index(drop=True)


def load_rankings(path=RANKINGS_FILE) -> pd.DataFrame:
    rankings = pd.read_csv(path)
    rankings["date"] = pd.to_datetime(rankings["date"])
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
        )

        rows.append(
            {
                "date": match["date"],
                "home_team": match["home_team"],
                "away_team": match["away_team"],
                **features,
                "home_score": int(match["home_score"]),
                "away_score": int(match["away_score"]),
                "result": get_result_label(int(match["home_score"]), int(match["away_score"])),
            }
        )

    return pd.DataFrame(rows)
