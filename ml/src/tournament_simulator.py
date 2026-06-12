import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from src.config import (
    CHAMPION_PROBABILITIES_FILE,
    CLASSIFIER_FILE,
    GROUP_STAGE_SIMULATION_FILE,
    HOST_TEAMS_2026,
    KNOCKOUT_BRACKET_FILE,
    REGRESSOR_FILE,
    WORLDCUP_FIXTURES_FILE,
    WORLDCUP_GROUPS_FILE,
    WORLDCUP_KNOCKOUT_TEMPLATE_FILE,
)
from src.data_processing import load_matches, load_rankings
from src.features import get_head_to_head_points, get_latest_rank, get_recent_stats, get_tournament_importance


LABEL_TO_OUTPUT_KEY = {
    "home_win": "homeWin",
    "draw": "draw",
    "away_win": "awayWin",
}

ROUND_ORDER = ["round_of_32", "round_of_16", "quarter_final", "semi_final", "final"]


def load_artifacts():
    classifier_artifact = joblib.load(CLASSIFIER_FILE)
    regressor_artifact = joblib.load(REGRESSOR_FILE)
    return {
        "classifier": classifier_artifact["model"],
        "model_name": classifier_artifact["model_name"],
        "label_encoder": classifier_artifact["label_encoder"],
        "feature_columns": classifier_artifact["feature_columns"],
        "regressor": regressor_artifact["model"],
    }


def cache_key_for_prediction(home_team, away_team, match_date, country, neutral):
    return (home_team, away_team, str(match_date), country, bool(neutral))


def date_key(match_date):
    return pd.to_datetime(match_date).strftime("%Y-%m-%d")


def get_date_feature_cache(match_date, context):
    key = date_key(match_date)
    if key not in context["feature_cache"]:
        parsed_date = pd.to_datetime(match_date)
        context["feature_cache"][key] = {
            "recent": {
                team: get_recent_stats(context["matches"], team, parsed_date)
                for team in context["teams"]
            },
            "ranks": {
                team: get_latest_rank(context["rankings"], team, parsed_date)
                for team in context["teams"]
            },
        }
    return context["feature_cache"][key]


def get_cached_h2h_points(home_team, away_team, match_date, context):
    key = (home_team, away_team, date_key(match_date))
    if key not in context["h2h_cache"]:
        context["h2h_cache"][key] = get_head_to_head_points(
            context["matches"],
            home_team,
            away_team,
            pd.to_datetime(match_date),
        )
    return context["h2h_cache"][key]


def build_feature_row(home_team, away_team, match_date, country, neutral, context):
    feature_cache = get_date_feature_cache(match_date, context)
    home_recent = feature_cache["recent"][home_team]
    away_recent = feature_cache["recent"][away_team]
    home_rank = feature_cache["ranks"][home_team]
    away_rank = feature_cache["ranks"][away_team]
    features = {
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
        "h2h_home_points": get_cached_h2h_points(home_team, away_team, match_date, context),
        "neutral": int(bool(neutral)),
        "home_is_2026_host": int(home_team in HOST_TEAMS_2026 and country in HOST_TEAMS_2026),
        "away_is_2026_host": int(away_team in HOST_TEAMS_2026 and country in HOST_TEAMS_2026),
        "home_days_since_last_match": home_recent["days_since_last_match"],
        "away_days_since_last_match": away_recent["days_since_last_match"],
        "days_since_last_match_delta": home_recent["days_since_last_match"] - away_recent["days_since_last_match"],
        "home_world_cup_points": home_recent["world_cup_points"],
        "away_world_cup_points": away_recent["world_cup_points"],
        "world_cup_points_diff": home_recent["world_cup_points"] - away_recent["world_cup_points"],
        "tournament_importance": get_tournament_importance("FIFA World Cup"),
    }
    return features


def build_feature_frame(home_team, away_team, match_date, country, neutral, context):
    features = build_feature_row(home_team, away_team, match_date, country, neutral, context)
    return pd.DataFrame(
        [
            {
                column: features[column]
                for column in context["feature_columns"]
            }
        ]
    )


def normalize_prediction(probabilities, score_prediction, context):
    labels = context["label_encoder"].inverse_transform(range(len(probabilities)))
    probability_array = np.zeros(3, dtype=float)
    probability_map = {"homeWin": 0.0, "draw": 0.0, "awayWin": 0.0}

    for label, probability in zip(labels, probabilities):
        key = LABEL_TO_OUTPUT_KEY[label]
        probability_map[key] = float(probability)

    probability_array[0] = probability_map["homeWin"]
    probability_array[1] = probability_map["draw"]
    probability_array[2] = probability_map["awayWin"]
    home_score, away_score = score_prediction
    return {
        "probabilities": probability_map,
        "probabilityArray": probability_array,
        "baseScore": {
            "home": max(0, round(float(home_score))),
            "away": max(0, round(float(away_score))),
        },
    }


def build_predictions(records, context):
    pending_records = []
    pending_keys = []

    for record in records:
        key = cache_key_for_prediction(
            record["home_team"],
            record["away_team"],
            record["date"],
            record["country"],
            record["neutral"],
        )
        if key not in context["prediction_cache"]:
            pending_records.append(record)
            pending_keys.append(key)

    if not pending_records:
        return

    feature_rows = [
        build_feature_row(
            record["home_team"],
            record["away_team"],
            record["date"],
            record["country"],
            record["neutral"],
            context,
        )
        for record in pending_records
    ]
    feature_frame = pd.DataFrame(
        [{column: features[column] for column in context["feature_columns"]} for features in feature_rows]
    )
    probability_rows = context["classifier"].predict_proba(feature_frame)
    score_rows = context["regressor"].predict(feature_frame)

    for key, probabilities, scores in zip(pending_keys, probability_rows, score_rows):
        context["prediction_cache"][key] = normalize_prediction(probabilities, scores, context)


def build_prediction(home_team, away_team, match_date, country, neutral, context):
    feature_frame = build_feature_frame(
        home_team,
        away_team,
        match_date,
        country,
        neutral,
        context,
    )
    probabilities = context["classifier"].predict_proba(feature_frame)[0]
    scores = context["regressor"].predict(feature_frame)[0]
    return normalize_prediction(probabilities, scores, context)


def get_or_build_prediction(home_team, away_team, match_date, country, neutral, context):
    cache_key = cache_key_for_prediction(home_team, away_team, match_date, country, neutral)
    if cache_key not in context["prediction_cache"]:
        context["prediction_cache"][cache_key] = build_prediction(
            home_team,
            away_team,
            match_date,
            country,
            neutral,
            context,
        )
    return context["prediction_cache"][cache_key]


def precompute_group_predictions(fixtures, context):
    fixture_records = []
    records = fixtures.sort_values("match_no").to_dict(orient="records")
    build_predictions(records, context)
    for fixture in records:
        prediction = get_or_build_prediction(
            fixture["home_team"],
            fixture["away_team"],
            fixture["date"],
            fixture["country"],
            bool(fixture["neutral"]),
            context,
        )
        fixture_records.append({**fixture, "prediction": prediction})
    return fixture_records


def precompute_knockout_predictions(teams, context):
    records = [
        {
            "home_team": home_team,
            "away_team": away_team,
            "date": "2026-07-01",
            "country": "United States",
            "neutral": True,
        }
        for home_team in teams
        for away_team in teams
        if home_team != away_team
    ]
    build_predictions(records, context)
    for record in records:
        context["knockout_cache"][(record["home_team"], record["away_team"])] = context["prediction_cache"][
            cache_key_for_prediction(
                record["home_team"],
                record["away_team"],
                record["date"],
                record["country"],
                record["neutral"],
            )
        ]


def sample_result(prediction, rng):
    result_index = int(rng.choice(3, p=prediction["probabilityArray"]))
    return ["homeWin", "draw", "awayWin"][result_index]


def adjust_score(base_score, result, rng):
    home_score = int(base_score["home"])
    away_score = int(base_score["away"])

    if result == "draw":
        draw_score = max(0, round((home_score + away_score) / 2))
        return draw_score, draw_score

    if result == "homeWin" and home_score <= away_score:
        home_score = away_score + int(rng.integers(1, 3))

    if result == "awayWin" and away_score <= home_score:
        away_score = home_score + int(rng.integers(1, 3))

    return home_score, away_score


def empty_team_row(team, group_name, rank):
    return {
        "team": team,
        "group": group_name,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
        "rank": rank,
    }


def apply_match_to_table(table, home_team, away_team, home_score, away_score):
    home = table[home_team]
    away = table[away_team]
    home["played"] += 1
    away["played"] += 1
    home["goals_for"] += home_score
    home["goals_against"] += away_score
    away["goals_for"] += away_score
    away["goals_against"] += home_score
    home["goal_difference"] = home["goals_for"] - home["goals_against"]
    away["goal_difference"] = away["goals_for"] - away["goals_against"]

    if home_score > away_score:
        home["wins"] += 1
        away["losses"] += 1
        home["points"] += 3
    elif home_score < away_score:
        away["wins"] += 1
        home["losses"] += 1
        away["points"] += 3
    else:
        home["draws"] += 1
        away["draws"] += 1
        home["points"] += 1
        away["points"] += 1


def rank_rows(rows):
    return sorted(
        rows,
        key=lambda row: (
            -row["points"],
            -row["goal_difference"],
            -row["goals_for"],
            row["rank"],
            row["team"],
        ),
    )


def build_group_template(groups, team_ranks):
    template = {}
    for group_name, group_rows in groups.groupby("group"):
        template[group_name] = {
            row["team"]: empty_team_row(row["team"], group_name, team_ranks[row["team"]])
            for _, row in group_rows.iterrows()
        }
    return template


def clone_group_template(template):
    return {
        group_name: {
            team: row.copy()
            for team, row in table.items()
        }
        for group_name, table in template.items()
    }


def simulate_group_stage(group_template, fixture_records, rng):
    group_tables = clone_group_template(group_template)
    match_results = []

    for fixture in fixture_records:
        result = sample_result(fixture["prediction"], rng)
        home_score, away_score = adjust_score(fixture["prediction"]["baseScore"], result, rng)
        apply_match_to_table(
            group_tables[fixture["group"]],
            fixture["home_team"],
            fixture["away_team"],
            home_score,
            away_score,
        )
        match_results.append(
            {
                "matchNo": int(fixture["match_no"]),
                "group": fixture["group"],
                "date": fixture["date"],
                "homeTeam": fixture["home_team"],
                "awayTeam": fixture["away_team"],
                "homeScore": home_score,
                "awayScore": away_score,
                "sampledResult": result,
            }
        )

    standings = {}
    winners = {}
    runners_up = {}
    third_placed = []

    for group_name, table in group_tables.items():
        ranked = rank_rows(list(table.values()))
        for position, row in enumerate(ranked, start=1):
            row["position"] = position
        standings[group_name] = ranked
        winners[group_name] = ranked[0]["team"]
        runners_up[group_name] = ranked[1]["team"]
        third_placed.append(ranked[2])

    best_thirds = rank_rows(third_placed)[:8]
    qualified = sorted(
        set(winners.values()) | set(runners_up.values()) | {row["team"] for row in best_thirds}
    )

    return {
        "standings": standings,
        "matchResults": match_results,
        "winners": winners,
        "runnersUp": runners_up,
        "bestThirds": best_thirds,
        "qualifiedTeams": qualified,
    }


def resolve_slot(slot, group_result, third_slots):
    if slot.startswith("W_"):
        return group_result["winners"][slot.split("_", 1)[1]]
    if slot.startswith("R_"):
        return group_result["runnersUp"][slot.split("_", 1)[1]]
    if slot.startswith("T"):
        return third_slots[slot]
    raise ValueError(f"Unknown bracket slot: {slot}")


def get_knockout_prediction(home_team, away_team, context):
    direct_key = (home_team, away_team)
    if direct_key not in context["knockout_cache"]:
        context["knockout_cache"][direct_key] = get_or_build_prediction(
            home_team,
            away_team,
            "2026-07-01",
            "United States",
            True,
            context,
        )
    return context["knockout_cache"][direct_key]


def play_knockout_match(home_team, away_team, round_name, match_no, context, rng):
    prediction = get_knockout_prediction(home_team, away_team, context)
    probabilities = prediction["probabilities"]
    home_probability = probabilities["homeWin"] + probabilities["draw"] / 2
    away_probability = probabilities["awayWin"] + probabilities["draw"] / 2
    total = home_probability + away_probability
    home_probability = home_probability / total
    winner = home_team if rng.random() < home_probability else away_team
    result = "homeWin" if winner == home_team else "awayWin"
    home_score, away_score = adjust_score(prediction["baseScore"], result, rng)

    return {
        "matchNo": int(match_no),
        "round": round_name,
        "homeTeam": home_team,
        "awayTeam": away_team,
        "homeWinProbability": float(home_probability),
        "awayWinProbability": float(away_probability),
        "homeScore": home_score,
        "awayScore": away_score,
        "winner": winner,
    }


def simulate_knockout(group_result, knockout_template_records, context, rng):
    third_slots = {
        f"T{index}": row["team"]
        for index, row in enumerate(group_result["bestThirds"], start=1)
    }
    current_matches = []

    for template_row in knockout_template_records:
        current_matches.append(
            play_knockout_match(
                resolve_slot(template_row["home_slot"], group_result, third_slots),
                resolve_slot(template_row["away_slot"], group_result, third_slots),
                "round_of_32",
                int(template_row["match_no"]),
                context,
                rng,
            )
        )

    bracket = {"round_of_32": current_matches}
    next_match_no = max(int(row["match_no"]) for row in knockout_template_records) + 1

    for round_name in ROUND_ORDER[1:]:
        winners = [match["winner"] for match in current_matches]
        current_matches = []
        for index in range(0, len(winners), 2):
            current_matches.append(
                play_knockout_match(
                    winners[index],
                    winners[index + 1],
                    round_name,
                    next_match_no,
                    context,
                    rng,
                )
            )
            next_match_no += 1
        bracket[round_name] = current_matches

    return bracket


def update_counts(counts, group_result, bracket):
    for team in group_result["qualifiedTeams"]:
        counts["qualification"][team] += 1

    round_map = {
        "round_of_32": "round_of_32",
        "round_of_16": "round_of_16",
        "quarter_final": "quarter_final",
        "semi_final": "semi_final",
        "final": "final",
    }
    for round_name, count_name in round_map.items():
        for match in bracket.get(round_name, []):
            counts[count_name][match["homeTeam"]] += 1
            counts[count_name][match["awayTeam"]] += 1

    champion = bracket["final"][0]["winner"]
    counts["champion"][champion] += 1


def summarize_probabilities(teams, counts, simulations, model_name):
    rows = []
    for team in teams:
        rows.append(
            {
                "team": team,
                "championProbability": counts["champion"][team] / simulations,
                "finalProbability": counts["final"][team] / simulations,
                "semiFinalProbability": counts["semi_final"][team] / simulations,
                "quarterFinalProbability": counts["quarter_final"][team] / simulations,
                "roundOf32Probability": counts["round_of_32"][team] / simulations,
                "qualificationProbability": counts["qualification"][team] / simulations,
            }
        )

    rows.sort(key=lambda row: row["championProbability"], reverse=True)
    return {
        "simulationCount": simulations,
        "modelName": model_name,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "teams": rows,
    }


def build_team_ranks(groups, rankings):
    return {
        team: get_latest_rank(rankings, team, pd.Timestamp("2026-06-11"))
        for team in sorted(groups["team"].unique())
    }


def run_simulation(simulations=10_000, random_seed=42):
    groups = pd.read_csv(WORLDCUP_GROUPS_FILE)
    fixtures = pd.read_csv(WORLDCUP_FIXTURES_FILE)
    fixtures["neutral"] = fixtures["neutral"].astype(str).str.lower().isin(["true", "1", "yes"])
    knockout_template = pd.read_csv(WORLDCUP_KNOCKOUT_TEMPLATE_FILE)
    artifacts = load_artifacts()
    context = {
        **artifacts,
        "matches": load_matches(),
        "rankings": load_rankings(),
        "prediction_cache": {},
        "knockout_cache": {},
    }
    rng = np.random.default_rng(random_seed)
    teams = sorted(groups["team"].unique())
    context["teams"] = teams
    context["feature_cache"] = {}
    context["h2h_cache"] = {}
    team_ranks = build_team_ranks(groups, context["rankings"])
    group_template = build_group_template(groups, team_ranks)
    fixture_records = precompute_group_predictions(fixtures, context)
    precompute_knockout_predictions(teams, context)
    knockout_template_records = knockout_template.sort_values("match_no").to_dict(orient="records")
    counts = defaultdict(Counter)
    representative_group_result = None
    representative_bracket = None

    for simulation_index in range(simulations):
        group_result = simulate_group_stage(group_template, fixture_records, rng)
        bracket = simulate_knockout(group_result, knockout_template_records, context, rng)
        update_counts(counts, group_result, bracket)

        if simulation_index == 0:
            representative_group_result = group_result
            representative_bracket = bracket

    champion_probabilities = summarize_probabilities(
        teams,
        counts,
        simulations,
        context["model_name"],
    )
    group_stage_report = {
        "simulationCount": simulations,
        "representativeRun": 1,
        "generatedAt": champion_probabilities["generatedAt"],
        **representative_group_result,
    }
    knockout_report = {
        "simulationCount": simulations,
        "representativeRun": 1,
        "generatedAt": champion_probabilities["generatedAt"],
        "bracket": representative_bracket,
        "predictedChampion": representative_bracket["final"][0]["winner"],
    }

    for path, payload in [
        (CHAMPION_PROBABILITIES_FILE, champion_probabilities),
        (GROUP_STAGE_SIMULATION_FILE, group_stage_report),
        (KNOCKOUT_BRACKET_FILE, knockout_report),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    return {
        "championProbabilities": champion_probabilities,
        "groupStage": group_stage_report,
        "knockoutBracket": knockout_report,
    }


def main():
    parser = argparse.ArgumentParser(description="Simulate the FIFA World Cup 2026 tournament.")
    parser.add_argument("--simulations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_simulation(args.simulations, args.seed)
    top_team = result["championProbabilities"]["teams"][0]
    print(
        json.dumps(
            {
                "simulationCount": args.simulations,
                "predictedChampion": top_team["team"],
                "championProbability": top_team["championProbability"],
                "representativeChampion": result["knockoutBracket"]["predictedChampion"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
