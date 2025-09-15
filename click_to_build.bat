@echo off
cd /d %~dp0

REM Ativa o venv (se tiver)
if exist venv39\Scripts\activate.bat (
    call venv39\Scripts\activate.bat
)

echo [YouToMP] Iniciando build com PyInstaller...

pyinstaller --noconsole --onefile ^
  --name YouToMP ^
  --icon yt_mp3_converter_multi_res.ico ^
  --add-data "yt_mp3_converter_multi_res.ico;." ^
  --add-data "Flags\br.png;Flags" ^
  --add-data "Flags\us.png;Flags" ^
  --add-binary "yt-dlp.exe;." ^
  --add-binary "ffmpeg/bin/ffmpeg.exe;ffmpeg/bin" ^
  --add-binary "ffmpeg/bin/ffprobe.exe;ffmpeg/bin" ^
  YouToMP3.py

echo.
echo [YouToMP] Build finalizado! O executável está em "dist\YouToMP.exe"
pause
