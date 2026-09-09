from sqlalchemy import create_engine, text

ro = create_engine("postgresql://football_ro:football_ro@localhost:5432/football_db")

with ro.connect() as conn:
    print(conn.execute(text("select count(*) from mart_player_value")).scalar())

with ro.connect() as conn:
    try:
        conn.execute(text("delete from model_predictions"))
        print("PROBLEM: write succeeded")
    except Exception as e:
        print(f"correctly refused: {type(e).__name__}")
