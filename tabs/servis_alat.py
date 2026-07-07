import streamlit as st
from datetime import datetime

@st.dialog("Notifikasi Servis")
def popup_sukses_servis(pesan):
    st.markdown("### Perbaikan Dicatat!")
    st.success(pesan)
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    st.header("Input Data Servis & Perbaikan Alat")

    if "notif_servis" in st.session_state:
        pesan_saved = st.session_state["notif_servis"]
        del st.session_state["notif_servis"]
        popup_sukses_servis(pesan_saved)

    # --- FORM UTAMA ---
    st.subheader("Informasi Alat & Kerusakan")
    
    col1, col2 = st.columns(2)
    with col1:
        nama_alat = st.text_input("Nama Alat / Mesin", placeholder="Contoh: Frimator")
        kode_alat = st.text_input("Kode / ID Alat", placeholder="Contoh: NC-001")
    with col2:
        tgl_masuk = st.datetime_input("Tanggal & Jam Masuk", value=datetime.now(), key="tgl_msk")
        tgl_selesai = st.datetime_input("Tanggal & Jam Selesai Perbaikan", value=datetime.now(), key="tgl_sls")

    kerusakan = st.text_area("Detail Kerusakan", placeholder="Jelaskan kendala atau kerusakan yang terjadi...")
    tindakan = st.text_area("Tindakan Perbaikan", placeholder="Apa saja yang dilakukan untuk memperbaiki?")

    st.markdown("---")
    st.caption("Catatan: input sparepart dilakukan secara manual sesuai kebutuhan perbaikan.")

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

    if st.button("SIMPAN DATA SERVIS", use_container_width=True):
        if not nama_alat or not kode_alat or not kerusakan:
            st.error("Nama Alat, Kode Alat, dan Detail Kerusakan wajib diisi!")
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
            None,
            0
        )
        
        sukses_servis, pesan_err = eksekusi_sql(sql_servis, params_servis)

        if sukses_servis:
            st.session_state["notif_servis"] = f"Data servis untuk alat '{nama_alat}' berhasil disimpan."
            st.rerun()
        else:
            st.error(f"❌ Gagal menyimpan data servis: {pesan_err}")