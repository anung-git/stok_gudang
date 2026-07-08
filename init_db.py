import sqlite3


def ensure_sparepart_location_column(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(spareparts)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'location' not in columns:
        cursor.execute("ALTER TABLE spareparts ADD COLUMN location TEXT")


def inisialisasi_database():
    conn = sqlite3.connect('gudang.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spareparts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        min_stock INTEGER DEFAULT 0,
        location TEXT
    )
    ''')
    ensure_sparepart_location_column(conn)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sparepart_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('IN', 'OUT')) NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        pic_name TEXT NOT NULL,
        purpose TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        FOREIGN KEY (sparepart_id) REFERENCES spareparts(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date TEXT NOT NULL,
        device_name TEXT NOT NULL,
        device_code TEXT NOT NULL,
        damage_info TEXT NOT NULL,
        completion_date TEXT,
        action_taken TEXT,
        notes TEXT,
        sparepart_id INTEGER,
        sparepart_qty INTEGER DEFAULT 0,
        FOREIGN KEY (sparepart_id) REFERENCES spareparts(id) ON DELETE SET NULL
    )
    ''')

    try:
        cursor.execute("INSERT INTO categories (name) VALUES ('Mekanikal'), ('Elektrikal')")
        cursor.execute("INSERT INTO spareparts (code, name, min_stock, location) VALUES ('B-01', 'Baut M12 x 50', 10, 'Rak A'), ('S-02', 'Sensor Proximity M12', 2, 'Rak B')")
        conn.commit()
        print("Database berhasil dibuat dan diisi data contoh!")
    except sqlite3.IntegrityError:
        conn.commit()
        print("Database sudah ada sebelumnya.")

    conn.close()


if __name__ == "__main__":
    inisialisasi_database()