@echo off
echo --- Digital Twin Career Engine: Setup ---
echo.
echo Installing necessary libraries...
echo This may take a minute.
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
if %errorlevel% neq 0 (
    echo [ERROR] Something went wrong during installation.
) else (
    echo [SUCCESS] Everything is ready! 
    echo Now you can run the project using run_site.bat
)
pause
