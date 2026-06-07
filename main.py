from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://football:football@localhost:5432/football_db")

with engine.connect() as conn:
    df = pd.read_sql(
        """
        select player_name, season, position
        from int_vaastav_player_history
        where player_name = 'Ian Maatsen'
    """,
        conn,
    )
    print(df)
