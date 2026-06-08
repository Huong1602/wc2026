import pandas as pd

from src.config import INTERNATIONAL_RESULTS_URL, MATCHES_FILE, RANKINGS_FILE, RAW_DATA_DIR


def expected_score(team_rating: float, opponent_rating: float) -> float:
    return 1 / (1 + 10 ** ((opponent_rating - team_rating) / 400))


def actual_score(goals_for: int, goals_against: int) -> float:
    if goals_for > goals_against:
        return 1.0
    if goals_for == goals_against:
        return 0.5
    return 0.0


def clean_matches(matches: pd.DataFrame) -> pd.DataFrame:
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
    matches = matches[required_columns].copy()
    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    matches = matches.dropna(subset=["date", "home_team", "away_team", "home_score", "away_score"])
    matches["home_team"] = matches["home_team"].astype(str).str.strip()
    matches["away_team"] = matches["away_team"].astype(str).str.strip()
    matches["country"] = matches["country"].astype(str).str.strip()
    matches["tournament"] = matches["tournament"].astype(str).str.strip()
    matches["home_score"] = matches["home_score"].astype(int)
    matches["away_score"] = matches["away_score"].astype(int)
    matches["neutral"] = matches["neutral"].astype(str).str.lower().isin(["true", "1", "yes"])
    matches = matches.drop_duplicates(subset=["date", "home_team", "away_team"], keep="last")
    return matches.sort_values("date").reset_index(drop=True)


def build_elo_rankings(matches: pd.DataFrame, k_factor: int = 32) -> pd.DataFrame:
    ratings: dict[str, float] = {}
    ranking_rows = []
    current_year = None
    previous_date = None

    def append_snapshot(snapshot_date) -> None:
        snapshot = sorted(ratings.items(), key=lambda item: item[1], reverse=True)
        for rank, (team, points) in enumerate(snapshot, start=1):
            ranking_rows.append(
                {
                    "date": snapshot_date.date().isoformat(),
                    "team": team,
                    "rank": rank,
                    "points": round(points, 2),
                }
            )

    for _, match in matches.iterrows():
        if current_year is not None and match["date"].year != current_year and previous_date is not None:
            append_snapshot(previous_date)

        current_year = match["date"].year
        previous_date = match["date"]
        home_team = match["home_team"]
        away_team = match["away_team"]
        home_rating = ratings.get(home_team, 1500.0)
        away_rating = ratings.get(away_team, 1500.0)

        home_expected = expected_score(home_rating, away_rating)
        away_expected = expected_score(away_rating, home_rating)
        home_actual = actual_score(int(match["home_score"]), int(match["away_score"]))
        away_actual = 1 - home_actual

        ratings[home_team] = home_rating + k_factor * (home_actual - home_expected)
        ratings[away_team] = away_rating + k_factor * (away_actual - away_expected)

    if previous_date is not None:
        append_snapshot(previous_date)

    rankings = pd.DataFrame(ranking_rows)
    rankings = rankings.drop_duplicates(subset=["date", "team"], keep="last")
    return rankings.sort_values(["date", "rank"]).reset_index(drop=True)


def ingest() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if MATCHES_FILE.exists():
        matches = pd.read_csv(MATCHES_FILE)
    else:
        matches = pd.read_csv(INTERNATIONAL_RESULTS_URL)
    matches = clean_matches(matches)
    rankings = build_elo_rankings(matches)
    matches.to_csv(MATCHES_FILE, index=False)
    rankings.to_csv(RANKINGS_FILE, index=False)

    print(f"Saved matches: {MATCHES_FILE} ({len(matches):,} rows)")
    print(f"Saved rankings: {RANKINGS_FILE} ({len(rankings):,} rows)")
    print("Ranking file is Elo-derived from public international results for reproducible coursework use.")


if __name__ == "__main__":
    ingest()
