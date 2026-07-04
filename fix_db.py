import sqlite3

# Menghubungkan ke database yang sudah ada
conn = sqlite3.connect('gudang.db')
cursor = conn.cursor()

print("Membuat tabel stock_transactions yang kurang...")

# Membuat tabel transaksi stok yang terlewat
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

conn.commit()
conn.close()
print("Selesai! Tabel berhasil ditambahkan.")