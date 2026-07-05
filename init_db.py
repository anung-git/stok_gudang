import sqlite3

# Membuat file database bernama gudang.db
conn = sqlite3.connect('gudang.db')
cursor = conn.cursor()

# Membuat tabel kategori
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

# Membuat tabel sparepart
cursor.execute('''
CREATE TABLE IF NOT EXISTS spareparts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    min_stock INTEGER DEFAULT 0
)
''')

# Membuat tabel transaksi stok yang diperlukan oleh aplikasi
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

# Isi data contoh (dummy data) agar tidak kosong saat pertama dibuka
try:
    cursor.execute("INSERT INTO categories (name) VALUES ('Mekanikal'), ('Elektrikal')")
    cursor.execute("INSERT INTO spareparts (code, name, min_stock) VALUES ('B-01', 'Baut M12 x 50', 10), ('S-02', 'Sensor Proximity M12', 2)")
    conn.commit()
    print("Database berhasil dibuat dan diisi data contoh!")
except sqlite3.IntegrityError:
    conn.commit()
    print("Database sudah ada sebelumnya.")

conn.close()