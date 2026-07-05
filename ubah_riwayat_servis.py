import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "gudang.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ubah_bulan_servis(target_bulan="05", target_tahun="2026"):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, entry_date, completion_date FROM maintenance_logs WHERE strftime('%m', entry_date) = '04'"
        ).fetchall()

        print(f"Ditemukan {len(rows)} data servis di bulan April")

        for row in rows:
            entry_dt = datetime.fromisoformat(row["entry_date"]) if isinstance(row["entry_date"], str) else row["entry_date"]
            completion_dt = None
            if row["completion_date"]:
                completion_dt = datetime.fromisoformat(row["completion_date"]) if isinstance(row["completion_date"], str) else row["completion_date"]

            if completion_dt is not None:
                # Pindah ke bulan Mei dengan selisih 1 bulan
                if completion_dt.month == 4:
                    completion_dt = completion_dt.replace(year=int(target_tahun), month=5)
                else:
                    completion_dt = completion_dt.replace(year=int(target_tahun), month=5)
            else:
                completion_dt = entry_dt.replace(year=int(target_tahun), month=5)

            new_entry = entry_dt.replace(year=int(target_tahun), month=5)
            new_completion = completion_dt

            conn.execute(
                "UPDATE maintenance_logs SET entry_date = ?, completion_date = ? WHERE id = ?",
                (new_entry.strftime('%Y-%m-%d %H:%M:%S'), new_completion.strftime('%Y-%m-%d %H:%M:%S'), row["id"])
            )

        conn.commit()
        print("Perubahan selesai.")


if __name__ == "__main__":
    ubah_bulan_servis()
