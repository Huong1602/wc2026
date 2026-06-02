import pandas as pd

from src.config import HOST_TEAMS_2026


def result_points(goals_for: int, goals_against: int) -> int:
    if goals_for > goals_against:
        return 3
    if goals_for == goals_against:
        return 1
    return 0


def get_recent_stats(matches: pd.DataFrame, team: str, match_date: pd.Timestamp, window: int = 5) -> dict:
    history = matches[
        (matches["date"] < match_date)
        & ((matches["home_team"] == team) | (matches["away_team"] == team))
    ].sort_values("date", ascending=False).head(window)

    if history.empty:
        return {"recent_points": 1.0, "recent_goal_diff": 0.0, "recent_goals_for": 1.0}

    points = []
    goal_diffs = []
    goals_for = []

    for _, row in history.iterrows():
        is_home = row["home_team"] == team
        team_goals = int(row["home_score"] if is_home else row["away_score"])
        opponent_goals = int(row["away_score"] if is_home else row["home_score"])
        points.append(result_points(team_goals, opponent_goals))
        goal_diffs.append(team_goals - opponent_goals)
        goals_for.append(team_goals)

    return {
        "recent_points": float(sum(points) / len(points)),
        "recent_goal_diff": float(sum(goal_diffs) / len(goal_diffs)),
        "recent_goals_for": float(sum(goals_for) / len(goals_for)),
    }


def get_head_to_head_points(
    matches: pd.DataFrame,
    home_team: str,
    away_team: str,
    match_date: pd.Timestamp,
    window: int = 5,
) -> float:
    history = matches[
        (matches["date"] < match_date)
        & (
            ((matches["home_team"] == home_team) & (matches["away_team"] == away_team))
            | ((matches["home_team"] == away_team) & (matches["away_team"] == home_team))
        )
    ].sort_values("date", ascending=False).head(window)

    if history.empty:
        return 1.0

    points = []
    for _, row in history.iterrows():
        if row["home_team"] == home_team:
            points.append(result_points(int(row["home_score"]), int(row["away_score"])))
        else:
            points.append(result_points(int(row["away_score"]), int(row["home_score"])))

    return float(sum(points) / len(points))


def get_latest_rank(rankings: pd.DataFrame, team: str, match_date: pd.Timestamp) -> float:
    team_rankings = rankings[(rankings["team"] == team) & (rankings["date"] <= match_date)].sort_values(
        "date",
        ascending=False,
    )

    if not team_rankings.empty:
        return float(team_rankings.iloc[0]["rank"])

    if not rankings.empty:
        return float(rankings["rank"].median())

    return 50.0


def make_match_features(
    home_team: str,
    away_team: str,
    match_date: pd.Timestamp,
    matches: pd.DataFrame,
    rankings: pd.DataFrame,
    neutral: bool = True,
    country: str = "",
) -> dict:
    home_recent = get_recent_stats(matches, home_team, match_date)
    away_recent = get_recent_stats(matches, away_team, match_date)
    home_rank = get_latest_rank(rankings, home_team, match_date)
    away_rank = get_latest_rank(rankings, away_team, match_date)
    h2h_points = get_head_to_head_points(matches, home_team, away_team, match_date)

    return {
        "home_rank": home_rank,
        "away_rank": away_rank,
        "rank_diff": home_rank - away_rank,
        "home_recent_points": home_recent["recent_points"],
        "away_recent_points": away_recent["recent_points"],
        "recent_points_diff": home_recent["recent_points"] - away_recent["recent_points"],
        "home_recent_goal_diff": home_recent["recent_goal_diff"],
        "away_recent_goal_diff": away_recent["recent_goal_diff"],
        "recent_goal_diff_delta": home_recent["recent_goal_diff"] - away_recent["recent_goal_diff"],
        "home_recent_goals_for": home_recent["recent_goals_for"],
        "away_recent_goals_for": away_recent["recent_goals_for"],
        "h2h_home_points": h2h_points,
        "neutral": int(bool(neutral)),
        "home_is_2026_host": int(home_team in HOST_TEAMS_2026 and country in HOST_TEAMS_2026),
        "away_is_2026_host": int(away_team in HOST_TEAMS_2026 and country in HOST_TEAMS_2026),
    }

