from sqlalchemy import create_engine
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

    train = df[df["season"].isin(["2022-23", "2023-24"])]
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


def predict_next3(artifact=None):
    if artifact is None:
        artifact = load_model()

    df = load_current_gw_data()
    df = build_features(df, for_training=False)

    df["position_encoded"] = df["position"].map(artifact["position_map"])
    df["was_home"] = df["was_home"].astype(int)

    latest_gw = df["gw"].max()
    remaining = 38 - latest_gw
    if remaining < 3:
        print(
            f"warning: only {remaining} gameweeks remain — "
            f"3-GW target is partially undefined"
        )
    latest = df[df["gw"] == latest_gw].copy()

    X = latest[artifact["features"]].fillna(artifact["medians"])
    latest["predicted_next3"] = artifact["model"].predict(X)

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


if __name__ == "__main__":
    df = load_gw_data()
    df = build_features(df)
    model, features, medians, metrics = train_gw_predictor(df)
    save_model(model, features, medians, metrics)

    preds = predict_next3()
    print(f"\npredictions for GW{preds['gw'].iloc[0]}, {len(preds)} players\n")
    print(preds.head(20).to_string(index=False))
