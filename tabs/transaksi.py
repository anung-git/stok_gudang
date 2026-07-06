import streamlit as st
from datetime import datetime

@st.dialog("Notifikasi Transaksi")
def popup_sukses_transaksi(pesan):
    st.markdown("### Transaksi Berhasil!")
    st.success(pesan)
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    st.header("Input Transaksi Logistik (Masuk / Keluar)")

    if "notif_transaksi" in st.session_state:
        pesan_saved = st.session_state["notif_transaksi"]
        del st.session_state["notif_transaksi"]
        popup_sukses_transaksi(pesan_saved)

    # Ambil data master sparepart untuk pilihan dropdown
    df_spareparts = jalankan_query("SELECT id, code, name FROM spareparts")
    
    if df_spareparts.empty:
        st.warning("Belum ada data barang di Master Gudang. Silakan isi tab 'Tambah Master Barang' terlebih dahulu.")
        return

    # Buat teks gabungan untuk tampilan pilihan di selectbox
    df_spareparts['display'] = df_spareparts['code'] + " - " + df_spareparts['name']

    # --- FORM INPUT TRANSAKSI ---
    st.subheader("Detail Mutasi Barang")
    
    # 1. Kolom Utama untuk Data Barang & PIC
    col1, col2 = st.columns(2)
    with col1:
        pilihan_barang = st.selectbox("Pilih Barang / Sparepart", options=df_spareparts['display'].tolist())
        jenis_transaksi = st.selectbox("Jenis Transaksi", options=["IN (Barang Masuk / Restock)", "OUT (Barang Keluar / Pakai)"])
        qty = st.number_input("Jumlah Barang (Pcs)", min_value=1, value=1)
    
    with col2:
        pic = st.text_input("Nama Penanggung Jawab / PIC", placeholder="Contoh: Ahmad (Logistik) / Dani (Teknisi)")
        tujuan = st.text_area("Keterangan Tujuan / Sumber Barang", placeholder="Contoh: Pembelian dari Supplier X / Digunakan untuk Rak B", height=115)

    # 2. Input Tunggal Tanggal & Jam Berdiri Sendiri (Satu Baris Penuh seperti Form Servis)
    tgl_jam_transaksi = st.datetime_input("Tanggal & Jam Transaksi", value=datetime.now(), key="tgl_jam_trx")

    st.markdown("###")
    # CSS Akurat untuk memaksa tombol transaksi menjadi hijau
    st.markdown("""
        <style>
        /* Mengunci elemen tombol berdasarkan atribut key di dalam Streamlit */
        div[data-testid="stButton"] button {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            width: 100% !important;
            transition: background-color 0.3s ease !important;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #218838 !important;
            color: white !important;
        }
        /* Memastikan teks di dalam tombol tetap putih bersih */
        div[data-testid="stButton"] button p {
            color: white !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Tombol Utama
    tombol_simpan = st.button("SIMPAN TRANSAKSI BARANG", use_container_width=True)
    if tombol_simpan:
        if not pic:
            st.error("Nama Penanggung Jawab (PIC) wajib diisi!")
            return

        # Ambil ID asli dari sparepart yang dipilih
        detail_barang = df_spareparts[df_spareparts['display'] == pilihan_barang].iloc[0]
        sparepart_id = int(detail_barang['id'])
        nama_barang_terpilih = detail_barang['name']

        # Ekstrak jenis transaksi (ambil kode IN atau OUT saja)
        tipe_kode = "IN" if "IN" in jenis_transaksi else "OUT"

        # Query SQL untuk menyimpan data transaksi
        sql_insert = """
        INSERT INTO stock_transactions (sparepart_id, type, quantity, pic_name, purpose, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            sparepart_id,
            tipe_kode,
            qty,
            pic,
            tujuan,
            tgl_jam_transaksi.strftime('%Y-%m-%d %H:%M:%S') # Format datetime SQL standar
        )

        sukses, pesan_err = eksekusi_sql(sql_insert, params)

        if sukses:
            st.session_state["notif_transaksi"] = f"Transaksi {tipe_kode} untuk barang '{nama_barang_terpilih}' sebanyak {qty} Pcs berhasil dicatat!"
            st.rerun()
        else:
            st.error(f"❌ Gagal menyimpan transaksi: {pesan_err}")