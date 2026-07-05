import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_SOURCE = BASE_DIR / "gudang.db"
BACKUP_DIR = BASE_DIR / "backup db"


def backup_database():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = BACKUP_DIR / f"gudang_backup_{timestamp}.db"

    shutil.copy2(DB_SOURCE, backup_file)
    print(f"Backup berhasil dibuat: {backup_file}")
    return str(backup_file)


if __name__ == "__main__":
    backup_database()
