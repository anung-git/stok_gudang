import streamlit as st
from datetime import datetime

@st.dialog("Notifikasi Servis")
def popup_sukses_servis(pesan):
    st.markdown("### 🛠️ Perbaikan Dicatat!")
    st.success(pesan)
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    st.header("🔧 Input Data Servis & Perbaikan Alat")

    if "notif_servis" in st.session_state:
        pesan_saved = st.session_state["notif_servis"]
        del st.session_state["notif_servis"]
        popup_sukses_servis(pesan_saved)

    # --- FORM UTAMA ---
    st.subheader("📝 Informasi Alat & Kerusakan")
    
    col1, col2 = st.columns(2)
    with col1:
        nama_alat = st.text_input("Nama Alat / Mesin", placeholder="Contoh: Mesin Packing A")
        kode_alat = st.text_input("Kode / ID Alat", placeholder="Contoh: MC-PK-01")
    with col2:
        tgl_masuk = st.datetime_input("Tanggal & Jam Masuk", value=datetime.now(), key="tgl_msk")
        tgl_selesai = st.datetime_input("Tanggal & Jam Selesai Perbaikan", value=datetime.now(), key="tgl_sls")

    kerusakan = st.text_area("Detail Kerusakan", placeholder="Jelaskan kendala atau kerusakan yang terjadi...")
    tindakan = st.text_area("Tindakan Perbaikan", placeholder="Apa saja yang dilakukan untuk memperbaiki?")

    # =========================================================================
    # --- KEMBALI KE VERSI AWAL: HANYA BISA PILIH 1 SPAREPART ---
    # =========================================================================
    st.markdown("---")
    st.subheader("⚙️ Suku Cadang / Sparepart yang Digunakan")
    
    # Ambil data sparepart yang tersedia
    df_sp = jalankan_query("SELECT id, code, name FROM spareparts")
    
    sparepart_id_terpilih = None
    qty_terpakai = 0
    
    if df_sp.empty:
        st.warning("Data suku cadang di database kosong.")
    else:
        # Buat daftar pilihan, tambahkan opsi "Tanpa Ganti Sparepart" di paling atas
        list_pilihan = ["-- Tanpa Ganti Sparepart (Hanya Jasa / Perbaikan Teknis) --"]
        for _, row in df_sp.iterrows():
            list_pilihan.append(f"{row['code']} - {row['name']}")
            
        pilihan_user = st.selectbox("Pilih Suku Cadang:", options=list_pilihan)
        
        # Jika user memilih sparepart (bukan opsi "Tanpa Ganti")
        if pilihan_user != list_pilihan[0]:
            code_part = pilihan_user.split(" - ")[0]
            row_terpilih = df_sp[df_sp['code'] == code_part].iloc[0]
            sparepart_id_terpilih = int(row_terpilih['id'])
            
            qty_terpakai = st.number_input(
                f"Jumlah yang digunakan untuk {row_terpilih['name']} (Pcs):", 
                min_value=1, 
                value=1, 
                step=1
            )

    st.markdown("###")

    # Tombol Simpan Hijau Standar
    st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
        }
        div[data-testid="stButton"] button p {
            color: white !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("💾 SIMPAN DATA SERVIS", use_container_width=True):
        if not nama_alat or not kode_alat or not kerusakan:
            st.error("❌ Nama Alat, Kode Alat, dan Detail Kerusakan wajib diisi!")
            return

        # 1. Masukkan data ke log induk perbaikan mesin (maintenance_logs)
        sql_servis = """
        INSERT INTO maintenance_logs 
        (entry_date, device_name, device_code, damage_info, completion_date, action_taken, sparepart_id, sparepart_qty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params_servis = (
            tgl_masuk.strftime('%Y-%m-%d %H:%M:%S'),
            nama_alat,
            kode_alat,
            kerusakan,
            tgl_selesai.strftime('%Y-%m-%d %H:%M:%S'),
            tindakan,
            sparepart_id_terpilih,  # Berisi ID jika ada, atau None jika tanpa sparepart
            qty_terpakai
        )
        
        sukses_servis, pesan_err = eksekusi_sql(sql_servis, params_servis)

        if sukses_servis:
            # Ambil ID log servis yang baru saja masuk
            df_last_id = jalankan_query("SELECT last_insert_rowid() AS id")
            last_log_id = int(df_last_id['id'].iloc[0])

            # 2. Jika ada sparepart yang digunakan, jalankan proses potong stok otomatis
            if sparepart_id_terpilih is not None and qty_terpakai > 0:
                # A. Catat ke tabel jembatan relasi (maintenance_details) agar sinkron dengan audit Anda
                eksekusi_sql(
                    "INSERT INTO maintenance_details (maintenance_id, sparepart_id, quantity) VALUES (?, ?, ?)",
                    (last_log_id, sparepart_id_terpilih, qty_terpakai)
                )
                
                # B. Masukkan ke log transaksi gudang sebagai barang keluar (OUT)
                eksekusi_sql(
                    """
                    INSERT INTO stock_transactions (sparepart_id, type, quantity, pic_name, purpose, created_at)
                    VALUES (?, 'OUT', ?, 'Teknisi Servis', ?, ?)
                    """,
                    (sparepart_id_terpilih, qty_terpakai, f"Servis Mesin: {nama_alat} ({kode_alat})", tgl_selesai.strftime('%Y-%m-%d %H:%M:%S'))
                )

                # C. POTONG STOK DI TABEL UTAMA (Mendeteksi nama kolom kuantitas Anda secara aman)
                df_cek_kolom = jalankan_query("PRAGMA table_info(spareparts)")
                if not df_cek_kolom.empty:
                    list_kolom_db = df_cek_kolom['name'].tolist()
                    for kandidat in ['quantity', 'stok', 'qty', 'stock']:
                        if kandidat in list_kolom_db:
                            query_potong = f"UPDATE spareparts SET {kandidat} = {kandidat} - ? WHERE id = ?"
                            eksekusi_sql(query_potong, (qty_terpakai, sparepart_id_terpilih))
                            break

            st.session_state["notif_servis"] = f"Data servis untuk alat '{nama_alat}' berhasil disimpan dan stok langsung terpotong!"
            st.rerun()
        else:
            st.error(f"❌ Gagal menyimpan data servis: {pesan_err}")