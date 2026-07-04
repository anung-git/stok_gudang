import streamlit as st
import sqlite3
import pandas as pd

# Konfigurasi Tampilan (100% Offline)
st.set_page_config(page_title="Stok Sparepart", page_icon="📦", layout="wide")
st.title("📦 Sistem Inventaris Sparepart Internal")

# Hubungkan Fungsi Pembantu Global
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
        return False, "Data ini terikat dengan riwayat transaksi. Hapus riwayat transaksinya terlebih dahulu di Tab Audit."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Membuat 4 Halaman/Tab dengan Emoji Offline
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Stok Aktual & Pencarian", 
    "🔄 Transaksi (Masuk/Keluar)", 
    "➕ Tambah Master Barang",
    "📊 Laporan Audit Bulanan"
])

# Import file tab dari folder tabs
from tabs import stok_aktual, transaksi, master_barang, audit_bulanan

# Panggil fungsi masing-masing tab dengan mengoper fungsi database-nya
with tab1:
    stok_aktual.show(jalankan_query)

with tab2:
    transaksi.show(jalankan_query, eksekusi_sql)

with tab3:
    master_barang.show(jalankan_query, eksekusi_sql)

with tab4:
    audit_bulanan.show(jalankan_query, eksekusi_sql)