from sqlalchemy import create_engine, text

engine = create_engine("postgresql://football:football@localhost:5432/football_db")

tables = [
    "mart_player_value",
    "mart_player_points",
    "mart_historical_player_performance",
    "stg_fpl_gw",
    "stg_vaastav_gw",
    "stg_fpl_teams",
]

with engine.connect() as conn:
    for t in tables:
        conn.execute(text(f"grant select on {t} to football_ro"))
    conn.execute(text("commit"))
    print("granted")
