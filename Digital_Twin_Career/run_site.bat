@echo off
echo --- Digital Twin Career Engine Launcher (Streamlit) ---
echo.

:: Force UTF-8 mode for Python to avoid ASCII encoding errors with Cyrillic
set PYTHONUTF8=1

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit /b
)

echo [INFO] Installing Streamlit if missing...
python -m pip install streamlit -q

echo [INFO] Starting Streamlit Dashboard...
python -m streamlit run app/app.py

pause
