@echo off
rem
chcp 65001 >nul

rem
powershell -NoProfile -Command "Get-Content -Raw -Encoding UTF8 'banner.txt'"

rem Sync VERSION from app/version.py
for /f "tokens=2 delims== " %%v in ('findstr "__version__" app\version.py') do set APP_VERSION=%%v
set APP_VERSION=%APP_VERSION:"=%

echo %APP_VERSION% > VERSION

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
