@echo off
rem
chcp 65001 >nul

rem
powershell -NoProfile -Command "Get-Content -Raw -Encoding UTF8 'banner.txt'"

echo.
echo ===============================
echo Cleaning old build artifacts...
echo ===============================
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo ===============================
echo Building EXE...
echo ===============================
python -m PyInstaller --clean main.spec

echo ===============================
echo Build finished.
echo ===============================
pause
