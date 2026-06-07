from sqlalchemy import create_engine
import pandas as pd
import os
import traceback
from sqlalchemy.exc import SQLAlchemyError

DB_URL = "postgresql://football:football@localhost:5432/football_db"
FPL_DIR = "data/FPL/2025"
UNDERSTAT_DIR = "data/EPL/2025"


def get_engine():
    return create_engine(DB_URL)


def load_csv(filepath, table_name, engine):
    try:
        df = pd.read_csv(filepath)
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
        )
        print(f"{table_name} loaded successfully — {len(df)} rows")
    except SQLAlchemyError as e:
        print(f"Database error: {e.__class__.__name__}")
        print(f"Details: {e.orig if hasattr(e, 'orig') else e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()


def run_load():
    engine = get_engine()
    print("Loading FPL data...")
    load_csv(f"{FPL_DIR}/players/players_raw.csv", "fpl_players_raw", engine)
    load_csv(f"{FPL_DIR}/players/cleaned_players.csv", "fpl_cleaned_players", engine)
    load_csv(f"{FPL_DIR}/fixtures/fixtures.csv", "fpl_fixtures", engine)
    load_csv(f"{FPL_DIR}/teams/teams.csv", "fpl_teams", engine)
    load_csv(f"{FPL_DIR}/managers/top_managers.csv", "fpl_managers", engine)
    load_csv(f"{UNDERSTAT_DIR}/players/players.csv", "understat_players", engine)
    for stat_type in ["standard", "shooting", "misc", "keeper", "playing_time"]:
        load_csv(f"{FPL_DIR}/fbref/{stat_type}.csv", f"fbref_{stat_type}", engine)
    print("Loading GW data...")
    gw_dfs = []
    for gw_file in sorted(os.listdir(f"{FPL_DIR}/gws")):
        if gw_file.startswith("gw_") and gw_file.endswith(".csv"):
            df = pd.read_csv(os.path.join(FPL_DIR, "gws", gw_file))
            gw_dfs.append(df)
    combined_gw = pd.concat(gw_dfs, ignore_index=True)
    combined_gw.to_sql("fpl_gw", engine, if_exists="replace", index=False)
    print(f"fpl_gw loaded — {len(combined_gw)} rows")


if __name__ == "__main__":
    run_load()
