import streamlit as st

# 1. Deklarasikan fungsi Pop-up Window (Modal Dialog) di bagian atas
@st.dialog("Notifikasi Sistem")
def popup_sukses(pesan, judul="Aksi Berhasil"):
    st.markdown(f"### {judul}")
    st.success(pesan)
    st.write("Perubahan data master barang telah disimpan secara permanen ke database.")
    if st.button("Oke, Tutup"):
        st.rerun()

def show(jalankan_query, eksekusi_sql):
    st.header("Daftarkan Jenis Sparepart Baru")
    
    # 2. Cek memori setelah rerun untuk memunculkan Pop-up Window
    if "notif_master" in st.session_state:
        info_notif = st.session_state["notif_master"]
        del st.session_state["notif_master"] # Segera hapus memori agar tidak berulang
        popup_sukses(info_notif["pesan"])

    kode_baru = st.text_input("Kode Part Baru (Harus Unik)", placeholder="Contoh: S8050, LM317, 100uF/63V")
    nama_baru = st.text_input("Nama Sparepart Baru", placeholder="Contoh: Resistor, Transistor, Kapasitor")
    stok_min = st.number_input("Batas Stok Minimum untuk Peringatan", min_value=0, value=2)
    
    tombol_simpan = st.button("Daftarkan Barang")
    
    if tombol_simpan:
        if kode_baru and nama_baru:
            sql_barang = "INSERT INTO spareparts (code, name, min_stock) VALUES (?, ?, ?)"
            sukses, pesan = eksekusi_sql(sql_barang, (kode_baru, nama_baru, stok_min))
            
            if sukses:
                st.session_state["notif_master"] = {
                    "pesan": f"Master barang baru dengan nama '{nama_baru}' BERHASIL didaftarkan!"
                }
                st.rerun()
            else:
                st.error("Gagal! Kode Part tersebut kemungkinan sudah terdaftar di sistem.")
        else:
            st.warning("Mohon lengkapi Kode Part dan Nama Barang.")

    st.markdown("---")
    st.subheader("Kelola / Edit / Hapus Master Barang")
    
    df_master = jalankan_query("SELECT id, code, name, min_stock FROM spareparts")
    
    if not df_master.empty:
        df_master['display'] = df_master['code'] + " - " + df_master['name']
        barang_kelola = st.selectbox("Pilih Barang yang Akan Diedit / Dihapus", options=df_master['display'].tolist())
        
        detail_barang = df_master[df_master['display'] == barang_kelola].iloc[0]
        id_edit = int(detail_barang['id'])
        
        st.write(f"**Mode Modifikasi data untuk ID: {id_edit}**")
        edit_nama = st.text_input("Ubah Nama Barang", value=detail_barang['name'])
        edit_min_stock = st.number_input("Ubah Batas Stok Minimum", min_value=0, value=int(detail_barang['min_stock']))
        
        kol1, kol2 = st.columns(2)
        with kol1:
            tombol_update = st.button("Simpan Perubahan Master")
            if tombol_update:
                sql_update = "UPDATE spareparts SET name = ?, min_stock = ? WHERE id = ?"
                sukses, pesan = eksekusi_sql(sql_update, (edit_nama, edit_min_stock, id_edit))
                if sukses:
                    st.session_state["notif_master"] = {
                        "pesan": f"Data master untuk '{edit_nama}' BERHASIL diperbarui!"
                    }
                    st.rerun()
                else:
                    st.error(f"Gagal memperbarui: {pesan}")
                    
        with kol2:
            tombol_hapus_master = st.button("Hapus Barang Ini dari Sistem")
            if tombol_hapus_master:
                sql_delete_master = "DELETE FROM spareparts WHERE id = ?"
                sukses, pesan = eksekusi_sql(sql_delete_master, (id_edit,))
                if sukses:
                    st.session_state["notif_master"] = {
                        "pesan": f"Barang '{detail_barang['name']}' BERHASIL dihapus total dari sistem!"
                    }
                    st.rerun()
                else:
                    # Gagal karena terikat relasi database (ditolak foreign key)
                    st.error(f"{pesan}")
    else:
        st.info("Belum ada barang terdaftar yang bisa dikelola.")