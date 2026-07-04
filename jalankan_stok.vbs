Set WinScriptHost = CreateObject("WScript.Shell")
' Ganti jalur di bawah ini sesuai dengan lokasi folder aplikasi Anda yang sebenarnya
WinScriptHost.CurrentDirectory = "C:\jalur\ke\folder\aplikasi-anda"
WinScriptHost.Run "streamlit run app.py", 0, False
Set WinScriptHost = Nothing