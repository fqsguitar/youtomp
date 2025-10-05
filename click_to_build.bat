@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if exist "venv39\Scripts\activate.bat" (
    call "venv39\Scripts\activate.bat"
)

echo [YouToMP] Finalizando instâncias antigas...
taskkill /im YouToMP.exe /f >nul 2>&1
timeout /t 1 /nobreak >nul
if exist "dist\YouToMP.exe" del /f /q "dist\YouToMP.exe" >nul 2>&1

echo [YouToMP] Iniciando build com PyInstaller...

pyinstaller --noconsole --onefile --noconfirm --clean ^
  --name YouToMP ^
  --icon "yt_mp3_converter_multi_res.ico" ^
  --add-data "yt_mp3_converter_multi_res.ico;." ^
  --add-data "Flags\br.png;Flags" ^
  --add-data "Flags\us.png;Flags" ^
  --add-binary "bin\yt-dlp.exe;bin" ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  "YouToMP.py"

echo.
if exist "dist\YouToMP.exe" (
  echo [YouToMP] Build finalizado! O executavel esta em "dist\YouToMP.exe"
) else (
  echo [YouToMP] Falha no build. Verifique o log acima.
)
pause
endlocal
