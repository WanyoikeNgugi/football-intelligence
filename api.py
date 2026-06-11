from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
import pandas as pd
import math

app = FastAPI(title="Football Intelligence API", version="1.0.0")
DB_URL = "postgresql://football:football@localhost:5432/football_db"
engine = create_engine(DB_URL)


def clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


def df_to_json(df):
    records = df.to_dict(orient="records")
    return [{k: clean_nan(v) for k, v in row.items()} for row in records]


@app.get("/")
def root():
    return {"message": "Football Intelligence API", "version": "1.0.0"}


@app.get("/players")
def get_players(page: int = 1, limit: int = 100):
    offset = (page - 1) * limit
    with engine.connect() as conn:
        df = pd.read_sql(
            text("select * from mart_player_value limit :limit offset :offset"),
            conn,
            params={"limit": limit, "offset": offset},
        )
    return df_to_json(df)


@app.get("/players/search")
def get_player_by_name(name: str):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("select * from mart_player_value where player_name ILIKE :name"),
            conn,
            params={"name": f"%{name}%"},
        )
    if df.empty:
        raise HTTPException(status_code=404, detail="Player not found")
    return df_to_json(df)


@app.get("/players/position/{position}")
def players_position(position: str):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("select * from mart_player_value where player_position = :position"),
            conn,
            params={"position": position.upper()},
        )
    if df.empty:
        raise HTTPException(
            status_code=404, detail=f"No players found for position {position}"
        )
    return df_to_json(df)


@app.get("/players/{player_id}")
def get_player(player_id: int):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("select * from mart_player_value where player_id = :id"),
            conn,
            params={"id": player_id},
        )
    if df.empty:
        raise HTTPException(status_code=404, detail="Player not found")
    return df_to_json(df)[0]


@app.get("/undervalued")
def get_undervalued_players():
    with engine.connect() as conn:
        df = pd.read_sql(
            "select * from mart_player_value where is_undervalued = true order by points_per_million desc",
            conn,
        )
    return df_to_json(df)


@app.get("/historical/{player_name}")
def get_player_historical(player_name: str):
    with engine.connect() as conn:
        df = pd.read_sql(
            text(
                "select * from mart_historical_player_performance where player_name = :player_name"
            ),
            conn,
            params={"player_name": player_name},
        )
    if df.empty:
        raise HTTPException(status_code=404, detail="Player not found")
    return df_to_json(df)


@app.get("/top-players")
def get_top_players(limit: int = 10):
    with engine.connect() as conn:
        df = pd.read_sql(
            text(
                "select * from mart_player_value order by total_points desc limit :limit"
            ),
            conn,
            params={"limit": limit},
        )
    return df_to_json(df)


@app.get("/gw/{gw}")
def get_gameweek(gw: int):
    with engine.connect() as conn:
        df = pd.read_sql(
            text("select * from stg_fpl_gw where gw = :gw"), conn, params={"gw": gw}
        )
    if df.empty:
        raise HTTPException(status_code=404, detail="game week not found")
    return df_to_json(df)
