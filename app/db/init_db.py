from pathlib import Path
from app.db.base import get_conn

def init_db():
    sql = Path("migrations/001_init.sql").read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.execute(sql)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
