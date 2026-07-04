@echo off
:: Pindah ke folder lokasi aplikasi Anda berada (Ganti jalur di bawah ini)
cd /d "D:\aplikasi-stok"

:: Menjalankan streamlit (Gunakan baris bawah jika tidak pakai venv)
streamlit run app.py

:: JIKA Anda pakai Virtual Environment (env_stok), ganti baris di atas dengan ini:
:: call env_stok\Scripts\activate && streamlit run app.py