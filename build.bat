@echo off
echo Building PII Shield...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "PII-Shield" ^
  --add-data "src/patterns.py;." ^
  --add-data "src/engine.py;." ^
  --add-data "src/file_handler.py;." ^
  --add-data "src/audit.py;." ^
  src/main.py
echo.
echo Done! Check the dist/ folder for PII-Shield.exe
pause
