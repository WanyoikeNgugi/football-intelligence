from sqlalchemy import create_engine, text
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import joblib
from datetime import datetime
from pathlib import Path

MODEL_DIR = Path("models")

DB_URL = "postgresql://football:football@localhost:5432/football_db"
engine = create_engine(DB_URL)

POSITION_MAP = {"GK": 0, "GKP": 0, "DEF": 1, "MID": 2, "FWD": 3, "AM": 2}


def load_gw_data():
    with engine.connect() as conn:
        df = pd.read_sql(
            """
            select * from stg_vaastav_gw
            where season in ('2022-23', '2023-24', '2024-25')
            """,
            conn,
        )
    return df


def load_current_gw_data():
    with engine.connect() as conn:
        df = pd.read_sql(
            """
            select
                player_id, name as player_name, position, team,
                gw, total_points, minutes, bps, ict_index,
                expected_goals, expected_assists, value, selected,
                was_home, opponent_team
            from stg_fpl_gw
            """,
            conn,
        )
    df["season"] = "2025-26"
    return df


def build_opponent_strength(df):
    """
    Average FPL points each team concedes, from prior gameweeks only.
    Higher = more generous opponent = better fixture.
    """
    played = df[df["minutes"] > 0]

    conceded = (
        played.groupby(["season", "opponent_team", "gw"])["total_points"]
        .mean()
        .reset_index()
        .rename(columns={"total_points": "pts_conceded_gw"})
        .sort_values(["season", "opponent_team", "gw"])
    )

    g = conceded.groupby(["season", "opponent_team"])

    conceded["opp_conceded_todate"] = g["pts_conceded_gw"].transform(
        lambda s: s.shift(1).expanding().mean()
    )
    conceded["opp_conceded_5"] = g["pts_conceded_gw"].transform(
        lambda s: s.shift(1).rolling(5, min_periods=1).mean()
    )

    return conceded[
        ["season", "opponent_team", "gw", "opp_conceded_todate", "opp_conceded_5"]
    ]


def build_features(df, for_training=True):
    df = df.sort_values(["player_name", "season", "gw"]).copy()
    g = df.groupby(["player_name", "season"])

    for col in [
        "total_points",
        "minutes",
        "bps",
        "ict_index",
        "expected_goals",
        "expected_assists",
    ]:
        df[f"roll_{col}_3"] = g[col].transform(
            lambda s: s.shift(1).rolling(3, min_periods=1).mean()
        )

    for col in ["total_points", "minutes"]:
        df[f"roll_{col}_5"] = g[col].transform(
            lambda s: s.shift(1).rolling(5, min_periods=1).mean()
        )

    if for_training:
        df["target_next3"] = g["total_points"].transform(
            lambda s: s.rolling(3, min_periods=3).sum().shift(-3)
        )

    opp = build_opponent_strength(df)
    df = df.merge(opp, on=["season", "opponent_team", "gw"], how="left")

    df = df[df["roll_total_points_3"].notna()]
    df = df[df["roll_minutes_3"] >= 15]

    if for_training:
        df = df[df["target_next3"].notna()]

    return df


def train_gw_predictor(df):
    df = df.copy()
    df["position_encoded"] = df["position"].map(POSITION_MAP)
    df["was_home"] = df["was_home"].astype(int)

    FEATURES = [
        "roll_total_points_3",
        "roll_minutes_3",
        "roll_bps_3",
        "roll_ict_index_3",
        "roll_expected_goals_3",
        "roll_expected_assists_3",
        "roll_total_points_5",
        "roll_minutes_5",
        "value",
        "selected",
        "was_home",
        "position_encoded",
        "opp_conceded_todate",
        "opp_conceded_5",
    ]
    LABEL = "target_next3"
    # NOTE: test set is now inside training data — printed metrics are
    # in-sample and optimistic. Real validation is via live scored
    # predictions in model_predictions (see performance_summary()).
    train = df[df["season"].isin(["2022-23", "2023-24", "2024-25"])]
    test = df[df["season"] == "2024-25"]

    X_train, y_train = train[FEATURES], train[LABEL]
    X_test, y_test = test[FEATURES], test[LABEL]

    medians = X_train.median()
    X_train = X_train.fillna(medians)
    X_test = X_test.fillna(medians)

    print(f"train: {len(X_train)} rows | test: {len(X_test)} rows\n")

    model = RandomForestRegressor(
        n_estimators=100, random_state=42, n_jobs=-1, min_samples_leaf=5
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("=== MODEL ===")
    print(f"MAE:  {mean_absolute_error(y_test, preds):.3f}")
    print(f"RMSE: {root_mean_squared_error(y_test, preds):.3f}")
    print(f"R²:   {r2_score(y_test, preds):.3f}\n")

    baseline = X_test["roll_total_points_3"] * 3
    print("=== BASELINE (just predict 3-GW rolling average) ===")
    print(f"MAE:  {mean_absolute_error(y_test, baseline):.3f}")
    print(f"RMSE: {root_mean_squared_error(y_test, baseline):.3f}")
    print(f"R²:   {r2_score(y_test, baseline):.3f}\n")

    print("=== FEATURE IMPORTANCE ===")
    imp = pd.Series(model.feature_importances_, index=FEATURES)
    print(imp.sort_values(ascending=False).to_string())

    metrics = {
        "mae": mean_absolute_error(y_test, preds),
        "rmse": root_mean_squared_error(y_test, preds),
        "r2": r2_score(y_test, preds),
    }

    return model, FEATURES, medians, metrics


def save_model(model, features, medians, metrics):
    MODEL_DIR.mkdir(exist_ok=True)

    artifact = {
        "model": model,
        "features": features,
        "medians": medians,
        "position_map": POSITION_MAP,
        "target": "target_next3",
        "trained_at": datetime.now().isoformat(),
        "metrics": metrics,
    }

    path = MODEL_DIR / "points_predictor.joblib"
    joblib.dump(artifact, path)
    print(f"saved → {path}")
    return path


def load_model(path=MODEL_DIR / "points_predictor.joblib"):
    return joblib.load(path)


def predict_next3(artifact=None, as_of_gw=None):
    if artifact is None:
        artifact = load_model()

    df = load_current_gw_data()
    df = build_features(df, for_training=False)

    df["position_encoded"] = df["position"].map(artifact["position_map"])
    df["was_home"] = df["was_home"].astype(int)
    target_gw = as_of_gw if as_of_gw is not None else df["gw"].max()
    # latest_gw = df["gw"].max()
    # remaining = 38 - latest_gw
    remaining = 38 - target_gw
    if remaining < 3:
        print(
            f"warning: only {remaining} gameweeks remain — "
            f"3-GW target is partially undefined"
        )
    latest = df[df["gw"] == target_gw].copy()

    X = latest[artifact["features"]].fillna(artifact["medians"])
    latest["predicted_next3"] = artifact["model"].predict(X)
    cal = artifact.get("calibration")
    if cal and cal.get("applied"):
        latest["predicted_raw"] = latest["predicted_next3"]
        latest["predicted_next3"] = latest["predicted_next3"] * cal["factor"]
    return latest[
        [
            "player_id",
            "player_name",
            "position",
            "team",
            "gw",
            "value",
            "predicted_next3",
        ]
    ].sort_values("predicted_next3", ascending=False)


def save_predictions(preds, artifact, season="2025-26"):
    df = preds.copy()
    made_at = int(df["gw"].iloc[0])

    df = df.rename(columns={"gw": "made_at_gw"})
    df["covers_gw_start"] = made_at + 1
    df["covers_gw_end"] = made_at + 3
    df["season"] = season
    df["model_trained_at"] = artifact["trained_at"]

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                delete from model_predictions
                where season = :season and made_at_gw = :gw
                """
            ),
            {"season": season, "gw": made_at},
        )
    df.to_sql("model_predictions", engine, if_exists="append", index=False)
    return len(df)


def evaluate_predictions(season="2025-26"):
    with engine.connect() as conn:
        preds = pd.read_sql(
            text("""
                select * from model_predictions
                where season = :season and actual_next3 is null
            """),
            conn,
            params={"season": season},
        )
        actuals = pd.read_sql(
            "select player_id, gw, total_points from stg_fpl_gw", conn
        )
    if preds.empty:
        return {"status": "nothing to evaluate"}

    max_gw = actuals["gw"].max()
    scored = []

    for _, p in preds.iterrows():
        if p["covers_gw_end"] > max_gw:
            continue

        window = actuals[
            (actuals["player_id"] == p["player_id"])
            & (actuals["gw"] >= p["covers_gw_start"])
            & (actuals["gw"] <= p["covers_gw_end"])
        ]

        if len(window) < 3:
            continue

        scored.append({"id": p["id"], "actual": window["total_points"].sum()})
    if not scored:
        return {"status": "no complete windows yet", "pending": len(preds)}

    with engine.begin() as conn:
        for s in scored:
            conn.execute(
                text("update model_predictions set actual_next3 = :a where id = :i"),
                {"a": float(s["actual"]), "i": int(s["id"])},
            )
    return {"status": "evaluated", "rows_scored": len(scored)}


def performance_summary(season="2025-26"):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                select made_at_gw, predicted_next3, actual_next3
                from model_predictions
                where season = :season and actual_next3 is not null
            """),
            conn,
            params={"season": season},
        )

    if df.empty:
        return {"status": "no scored predictions yet"}

    return {
        "n": len(df),
        "mae": float(mean_absolute_error(df["actual_next3"], df["predicted_next3"])),
        "rmse": float(
            root_mean_squared_error(df["actual_next3"], df["predicted_next3"])
        ),
        "r2": float(r2_score(df["actual_next3"], df["predicted_next3"])),
        "gameweeks": sorted(df["made_at_gw"].unique().tolist()),
    }


def compute_calibration(season="2025-26", min_rows=500):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                select predicted_next3, actual_next3
                from model_predictions
                where season = :season and actual_next3 is not null
            """),
            conn,
            params={"season": season},
        )

    if len(df) < min_rows:
        print(f"only {len(df)} scored rows, need {min_rows} - no calibration")
        return {"factor": 1.0, "n": len(df), "applied": False}

    mean_factor = df["actual_next3"].mean() / df["predicted_next3"].mean()
    median_factor = df["actual_next3"].median() / df["predicted_next3"].median()
    return {
        "factor": 1.0,
        "mean_factor": float(mean_factor),
        "median_factor": float(median_factor),
        "n": len(df),
        "season": season,
        "computed_at": datetime.now().isoformat(),
        "applied": False,
        "note": (
            "No scalar calibration applied. Mean ratio > 1 and median ratio < 1 "
            "indicates prediction compression rather than uniform bias — the model "
            "under-predicts high scorers and slightly over-predicts typical ones. "
            "A multiplier cannot correct this."
        ),
    }


def add_calibration_to_artifact(season="2025-26"):
    artifact = load_model()
    cal = compute_calibration(season)
    artifact["calibration"] = cal

    path = MODEL_DIR / "points_predictor.joblib"
    joblib.dump(artifact, path)
    print(f"calibration factor {cal['factor']:.4f} (n={cal['n']}) → {path}")
    return cal


if __name__ == "__main__":
    add_calibration_to_artifact()

    artifact = load_model()
    with engine.begin() as conn:
        conn.execute(text("delete from model_predictions where season = '2025-26'"))

    for gw in [28, 29, 30, 31, 32]:
        preds = predict_next3(artifact, as_of_gw=gw)
        save_predictions(preds, artifact)

    print(evaluate_predictions())
    print(performance_summary())
