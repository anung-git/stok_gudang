import streamlit as st
import sqlite3
import pandas as pd
from init_db import inisialisasi_database

# ==================== 100% OFFLINE CONFIGURATION ====================
st.set_page_config(page_title="Stok & Servis Gudang", layout="wide")
st.title("Sistem Servis dan Sparepart Larissa Simanjuntak")

# ==================== INITIALIZE DATABASE & TABLES ====================
# Semua pembuatan tabel dipusatkan di init_db.py
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
    "Servis & Perbaikan Alat",
    "Stok Aktual & Pencarian Sparepart",
    "Transaksi Sparepart (Masuk/Keluar)",
    "Tambah Master Sparepart",
    "Riwayat Servis dan Sparepart"
])

# ==================== IMPORT MODULAR TABS ====================
# Memanggil modul-modul file python dari dalam folder tabs/
from tabs import stok_aktual, transaksi, servis_alat, master_barang, audit_bulanan

# Mendistribusikan logika fungsi database ke masing-masing file tab
with tab1:
    servis_alat.show(jalankan_query, eksekusi_sql)

with tab2:
    stok_aktual.show(jalankan_query)

with tab3:
    transaksi.show(jalankan_query, eksekusi_sql)

with tab4:
    master_barang.show(jalankan_query, eksekusi_sql)

with tab5:
    audit_bulanan.show(jalankan_query, eksekusi_sql)