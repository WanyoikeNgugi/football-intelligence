from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://football:football@localhost:5432/football_db')

# list all tables
with engine.connect() as conn:
    tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", conn)
    print(tables)

# preview a table
with engine.connect() as conn:
    df = pd.read_sql("SELECT * FROM fpl_players_raw LIMIT 5", conn)
    print(df)