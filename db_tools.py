import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "gudang.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables():
    with get_connection() as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        return [row["name"] for row in rows]


def show_table(table_name):
    with get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY 1").fetchall()
        return [dict(row) for row in rows]


def run_query(sql, params=()):
    with get_connection() as conn:
        conn.execute(sql, params)
        conn.commit()
        return True


def backup_db(destination=None):
    dest = Path(destination) if destination else Path(__file__).resolve().parent / "backup_db" / "gudang_backup.db"
    dest.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(DB_PATH, dest)
    return str(dest)


if __name__ == "__main__":
    print("Database file:", DB_PATH)
    print("Tables:")
    for name in list_tables():
        print("-", name)
