from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://football:football@localhost:5432/football_db")

with engine.connect() as conn:
    # undervalued players
    df = pd.read_sql(
        """
        select player_name, player_position, price, total_points, 
               points_per_million, us_xg, us_xa, is_undervalued
        from mart_player_value
        where is_undervalued = true
        order by points_per_million desc
        limit 10
    """,
        conn,
    )
    print("=== TOP UNDERVALUED PLAYERS ===")
    print(df.to_string())

    # top points scorers
    df2 = pd.read_sql(
        """
        select player_name, position, price, total_points, avg_points_per_gw
        from mart_player_points
        order by total_points desc
        limit 10
    """,
        conn,
    )
    print("\n=== TOP POINTS SCORERS ===")
    print(df2.to_string())

    # historical performance
    df3 = pd.read_sql(
        """
        select player_name, total_points, career_avg_points_per_gw, 
               seasons_played, career_goals, career_assists
        from mart_historical_player_performance
        where seasons_played >= 3
        order by career_avg_points_per_gw desc
        limit 10
    """,
        conn,
    )
    print("\n=== MOST CONSISTENT PLAYERS (3+ SEASONS) ===")
    print(df3.to_string())
