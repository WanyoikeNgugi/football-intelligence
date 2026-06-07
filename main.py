from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://football:football@localhost:5432/football_db")
with engine.connect() as conn:
    df = pd.read_sql("select * from fbref_standard limit 1", conn)
    print(df.columns.tolist())
