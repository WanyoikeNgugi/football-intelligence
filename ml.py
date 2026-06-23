from sqlalchemy import create_engine
import pandas as pd

DB_URL = "postgresql://football:football@localhost:5432/football_db"
engine = create_engine(DB_URL)


def load_data():
    with engine.connect() as conn:
        df = pd.read_sql("select * from mart_player_value", conn)
    return df


# def train_points_predictor(df):
