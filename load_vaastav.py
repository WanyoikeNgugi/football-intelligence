from sqlalchemy import create_engine
import pandas as pd
import os
import traceback
from sqlalchemy.exc import SQLAlchemyError

DB_URL = "postgresql://football:football@localhost:5432/football_db"
VAASTAV_DIR = r"C:\Users\Dell\Fantasy-Premier-League\data"
SEASONS = [
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
]


def get_engine():
    return create_engine(DB_URL)


def load_historical_gw(engine):
    combined_merged_dw = []
    for season in SEASONS:
        merged_df = pd.read_csv(
            os.path.join(VAASTAV_DIR, season, "gws", "merged_gw.csv"),
            encoding="latin-1",
        )
        merged_df["season"] = season
        combined_merged_dw.append(merged_df)
        print(f"{season} loaded — {len(merged_df)} rows")
    combined_df = pd.concat(combined_merged_dw, ignore_index=True)
    try:
        combined_df.to_sql(
            name="vaastav_merged_gw", con=engine, if_exists="replace", index=False
        )
        print(f"vaastav_merged_gw loaded — {len(combined_df)} rows")
    except SQLAlchemyError as e:
        print(f"Database error: {e.__class__.__name__}")
        print(f"Details: {e.orig if hasattr(e, 'orig') else e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()


def load_historical_players(engine):
    combined_players = []
    for season in SEASONS:
        players_df = pd.read_csv(
            os.path.join(VAASTAV_DIR, season, "players_raw.csv"), encoding="latin-1"
        )
        players_df["season"] = season
        combined_players.append(players_df)
        print(f"{season} loaded - {len(players_df)} rows")
    combined_df = pd.concat(combined_players, ignore_index=True)
    try:
        combined_df.to_sql(
            name="vaastav_players_raw", con=engine, if_exists="replace", index=False
        )
        print(f"vaastav_players loaded - {len(combined_df)} rows")
    except SQLAlchemyError as e:
        print(f"Database error: {e.__class__.__name__}")
        print(f"Details: {e.orig if hasattr(e, 'orig') else e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()


def load_historical_fixtures(engine):
    combined_fixtures = []
    for season in SEASONS:
        try:
            fixtures_df = pd.read_csv(
                os.path.join(VAASTAV_DIR, season, "fixtures.csv"), encoding="latin-1"
            )
            fixtures_df["season"] = season
            combined_fixtures.append(fixtures_df)
            print(f"{season} loaded - {len(fixtures_df)} rows")
        except Exception as e:
            print(f"{season} fixtures not found — skipping: {e}")
            continue
    combined_df = pd.concat(combined_fixtures, ignore_index=True)
    try:
        combined_df.to_sql(
            name="vaastav_fixtures", con=engine, if_exists="replace", index=False
        )
        print(f"vaastav_fixtures loaded - {len(combined_df)} rows")
    except SQLAlchemyError as e:
        print(f"Database error: {e.__class__.__name__}")
        print(f"Details: {e.orig if hasattr(e, 'orig') else e}")
    except Exception as e:
        print(f"Unexpected erro: {e}")
        traceback.print_exc()


def run_load():
    engine = get_engine()
    load_historical_gw(engine)
    load_historical_players(engine)
    load_historical_fixtures(engine)


if __name__ == "__main__":
    run_load()
