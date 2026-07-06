import streamlit as st
from datetime import datetime
import pandas as pd

@st.dialog("Notifikasi Sistem")
def popup_sukses(pesan, judul="🚨 Aksi Berhasil"):
    st.markdown(f"### {judul}")
    st.success(pesan)
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    if "notif_audit" in st.session_state:
        info_notif = st.session_state["notif_audit"]
        del st.session_state["notif_audit"]
        popup_sukses(info_notif["pesan"], info_notif["judul"])

    kolom1, kolom2 = st.columns(2)
    with kolom1:
        bulan_pilihan = st.selectbox(
            "Pilih Bulan", 
            options=["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                     "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
            index=datetime.now().month - 1
        )
        list_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                      "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        angka_bulan = str(list_bulan.index(bulan_pilihan) + 1).zfill(2)

    with kolom2:
        list_tahun = list(range(2026, 2051))
        tahun_default = datetime.now().year
        tahun_pilihan = st.selectbox(
            "Pilih Tahun",
            options=list_tahun,
            index=list_tahun.index(tahun_default)
        )
    
    # =========================================================================
    # --- BAGIAN 1: TABEL MUTASI LOGISTIK SPAREPART ---
    # =========================================================================
    st.markdown("###")
    st.subheader(f"📦 Riwayat Penggunaan Sparepart ({bulan_pilihan} {tahun_pilihan})")
    
    query_audit_master = """
    SELECT 
        t.id AS 'ID Transaksi',
        t.created_at AS 'Tanggal & Jam',
        s.code AS 'Kode Part',
        s.name AS 'Nama Barang',
        t.type AS 'Jenis (IN/OUT)',
        t.quantity AS 'Jumlah (Pcs)',
        t.pic_name AS 'Teknisi / Penanggung Jawab',
        t.purpose AS 'Keterangan / Tujuan'
    FROM stock_transactions t
    JOIN spareparts s ON t.sparepart_id = s.id
    ORDER BY t.created_at ASC
    """
    
    df_audit_all = jalankan_query(query_audit_master)
    
    if df_audit_all.empty:
        st.info("Belum ada riwayat transaksi mutasi barang di gudang logistik.")
        df_audit = pd.DataFrame()
    else:
        df_audit_all['Tanggal_DT'] = pd.to_datetime(df_audit_all['Tanggal & Jam'], errors='coerce')
        df_audit = df_audit_all[
            (df_audit_all['Tanggal_DT'].dt.strftime('%m') == angka_bulan) & 
            (df_audit_all['Tanggal_DT'].dt.strftime('%Y') == str(tahun_pilihan))
        ].copy()
        
        if not df_audit.empty:
            df_audit = df_audit.drop(columns=['Tanggal_DT'])

    if df_audit.empty:
        st.info(f"Tidak ada riwayat transaksi logistik barang pada bulan {bulan_pilihan} {tahun_pilihan}.")
    else:
        df_audit = df_audit.reset_index(drop=True)
        df_audit.index = df_audit.index + 1

        if {'ID Transaksi', 'Kode Part', 'Nama Barang', 'Tanggal & Jam'}.issubset(df_audit.columns):
            cols = ['Tanggal & Jam', 'Nama Barang', 'Kode Part']
            cols += [c for c in df_audit.columns if c not in ['Tanggal & Jam', 'Nama Barang', 'Kode Part', 'ID Transaksi']]
            cols += ['ID Transaksi']
            df_audit = df_audit[cols]

        st.write(f"Menampilkan **{len(df_audit)} transaksi barang**:")
        st.dataframe(df_audit, use_container_width=True)
        
        csv_data = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Laporan Transaksi (CSV)",
            data=csv_data,
            file_name=f"Laporan_Stok_{bulan_pilihan}_{tahun_pilihan}.csv",
            mime="text/csv",
            key="dl_transaksi"
        )
        
        st.markdown("---")
        st.subheader("⚠️ Pembatalan / Hapus Transaksi Logistik")
        list_id_transaksi = df_audit['ID Transaksi'].tolist()
        id_hapus_pilihan = st.selectbox("Pilih ID Transaksi yang Ingin Dihapus", options=list_id_transaksi)
        detail_hapus = df_audit[df_audit['ID Transaksi'] == id_hapus_pilihan].iloc[0]
        st.warning(f"Anda memilih menghapus transaksi ID **{id_hapus_pilihan}** ({detail_hapus['Nama Barang']}).")
        
        if st.button("Hapus Transaksi Logistik Ini"):
            sql_delete = "DELETE FROM stock_transactions WHERE id = ?"
            sukses, pesan = eksekusi_sql(sql_delete, (int(id_hapus_pilihan),))
            if sukses:
                st.session_state["notif_audit"] = {"pesan": f"Transaksi ID {id_hapus_pilihan} BERHASIL dihapus!", "judul": "🚨 Transaksi Dibatalkan"}
                st.rerun()

    # =========================================================================
    # --- BAGIAN 2: TABEL RIWAYAT SERVIS (VERSI ORIGINAL 1 SPAREPART) ---
    # =========================================================================
    st.markdown("---")
    st.subheader(f"🛠️ Riwayat Servis & Perbaikan Alat ({bulan_pilihan} {tahun_pilihan})")
    
    query_servis_induk = """
    SELECT 
        m.id AS 'ID Servis',
        m.entry_date AS 'Waktu Masuk',
        m.device_name AS 'Nama Alat',
        m.device_code AS 'Kode Alat',
        m.damage_info AS 'Kerusakan',
        m.completion_date AS 'Waktu Selesai',
        m.action_taken AS 'Tindakan Perbaikan'
    FROM maintenance_logs m
    ORDER BY m.entry_date ASC
    """
    
    df_servis_all = jalankan_query(query_servis_induk)
    
    if df_servis_all.empty:
        st.info("Tidak ada aktivitas servis/perbaikan mesin yang tercatat di sistem.")
    else:
        # Kode di bawah ini sudah diperbaiki penutupan tanda kurungnya (Anti SyntaxError)
        df_servis_all['Waktu Masuk DT'] = pd.to_datetime(df_servis_all['Waktu Masuk'], errors='coerce')
        
        df_servis = df_servis_all[
            (df_servis_all['Waktu Masuk DT'].dt.strftime('%m') == angka_bulan) & 
            (df_servis_all['Waktu Masuk DT'].dt.strftime('%Y') == str(tahun_pilihan))
        ].copy()
        
        if not df_servis.empty:
            df_servis = df_servis.drop(columns=['Waktu Masuk DT'])

        if df_servis.empty:
            st.info(f"Tidak ada riwayat aktivitas servis mesin pada bulan {bulan_pilihan} {tahun_pilihan}.")
        else:
            if 'ID Servis' in df_servis.columns:
                cols = [c for c in df_servis.columns if c != 'ID Servis'] + ['ID Servis']
                df_servis = df_servis[cols]

            df_servis = df_servis.reset_index(drop=True)
            df_servis.index = df_servis.index + 1

            st.write(f"Menampilkan **{len(df_servis)} riwayat perbaikan mesin**:")
            st.dataframe(df_servis, use_container_width=True)
            
            csv_servis = df_servis.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Laporan Servis (CSV)",
                data=csv_servis,
                file_name=f"Laporan_Servis_{bulan_pilihan}_{tahun_pilihan}.csv",
                mime="text/csv",
                key="dl_servis"
            )
            
            st.markdown("---")
            st.subheader("🗑️ Hapus Riwayat / Data Servis")
            list_id_servis = df_servis['ID Servis'].tolist()
            id_servis_hapus = st.selectbox("Pilih ID Servis yang Ingin Dihapus", options=list_id_servis)
            
            if st.button("❌ Hapus Log Servis Ini"):
                sukses_del, pesan_del = eksekusi_sql("DELETE FROM maintenance_logs WHERE id = ?", (int(id_servis_hapus),))
                if sukses_del:
                    st.session_state["notif_audit"] = {
                        "pesan": f"Data riwayat servis ID {id_servis_hapus} BERHASIL dihapus!",
                        "judul": "🗑️ Log Servis Dihapus"
                    }
                    st.rerun()