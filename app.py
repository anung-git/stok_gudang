import streamlit as st
import sqlite3
import pandas as pd

# ==================== 100% OFFLINE CONFIGURATION ====================
st.set_page_config(page_title="Stok & Servis Gudang", page_icon="📦", layout="wide")
st.title("📦 Sistem Manajemen Inventaris & Perbaikan Internal")

# ==================== INITIALIZE DATABASE & TABLES ====================
def inisialisasi_database():
    conn = sqlite3.connect('gudang.db')
    cursor = conn.cursor()
    
    # 1. Pastikan tabel master spareparts ada
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spareparts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        min_stock INTEGER DEFAULT 2
    );
    """)
    
    # 2. Pastikan tabel transaksi stok ada
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sparepart_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'IN' atau 'OUT'
        quantity INTEGER NOT NULL,
        pic_name TEXT NOT NULL,
        purpose TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sparepart_id) REFERENCES spareparts(id)
    );
    """)
    
    # 3. BARU: Pastikan tabel log servis alat ada
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date DATETIME NOT NULL,
        device_name TEXT NOT NULL,
        device_code TEXT NOT NULL,
        damage_info TEXT NOT NULL,
        completion_date DATETIME,
        action_taken TEXT,
        notes TEXT,
        sparepart_id INTEGER,
        sparepart_qty INTEGER DEFAULT 0,
        FOREIGN KEY (sparepart_id) REFERENCES spareparts(id)
    );
    """)


    # Masukkan ini di area fungsi inisialisasi database Anda
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maintenance_id INTEGER,
        sparepart_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (maintenance_id) REFERENCES maintenance_logs(id),
        FOREIGN KEY (sparepart_id) REFERENCES spareparts(id)
    );
    """)
        
    conn.commit()
    conn.close()

# Jalankan pembuatan database otomatis saat script di-run
inisialisasi_database()

# ==================== GLOBAL HELPER FUNCTIONS ====================
def jalankan_query(query, params=()):
    conn = sqlite3.connect('gudang.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def eksekusi_sql(sql, params=()):
    conn = sqlite3.connect('gudang.db')
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON;") 
        cursor.execute(sql, params)
        conn.commit()
        return True, "Berhasil!"
    except sqlite3.IntegrityError:
        return False, "Data ini terikat dengan riwayat transaksi/servis yang ada. Hapus data terkait terlebih dahulu."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ==================== INTERFACE TABS CONFIGURATION ====================
# Membuat 5 Halaman/Tab Mandiri (Menambahkan Tab Servis Alat)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Stok Aktual & Pencarian", 
    "🔄 Transaksi (Masuk/Keluar)", 
    "🔧 Servis & Perbaikan Alat",  # <-- Tab Baru Anda
    "➕ Tambah Master Barang",
    "📊 Laporan Audit Bulanan"
])

# ==================== IMPORT MODULAR TABS ====================
# Memanggil modul-modul file python dari dalam folder tabs/
from tabs import stok_aktual, transaksi, servis_alat, master_barang, audit_bulanan

# Mendistribusikan logika fungsi database ke masing-masing file tab
with tab1:
    stok_aktual.show(jalankan_query)

with tab2:
    transaksi.show(jalankan_query, eksekusi_sql)

with tab3:
    servis_alat.show(jalankan_query, eksekusi_sql) # <-- Mengaktifkan Tab Servis Baru

with tab4:
    master_barang.show(jalankan_query, eksekusi_sql)

with tab5:
    audit_bulanan.show(jalankan_query, eksekusi_sql)