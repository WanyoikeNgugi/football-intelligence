from sqlalchemy import create_engine, text

ro = create_engine("postgresql://football_ro:football_ro@localhost:5432/football_db")

with ro.connect() as conn:
    try:
        r = conn.execute(text("select * from customer_transactions limit 1")).fetchall()
        print("PROBLEM: readable —", r)
    except Exception as e:
        print(f"correctly refused: {type(e).__name__}")
