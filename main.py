from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://football:football@localhost:5432/football_db")

with engine.connect() as conn:
    print(
        pd.read_sql(
            """
        select season,
               count(*) n,
               count(*) filter (where position is null) nulls,
               count(*) filter (where position = 'AM') am
        from stg_vaastav_gw
        where season in ('2022-23','2023-24','2024-25')
        group by season order by season
    """,
            conn,
        ).to_string()
    )
