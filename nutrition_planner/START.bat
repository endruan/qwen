@echo off
chcp 65001 >nul
echo ============================================================
echo    NUTRITION PLANNER - Web Interface
echo ============================================================
echo.

REM Check if database exists, if not create it
if not exist nutrition.db (
    echo [INFO] Creating database with sample data...
    python demo.py
    echo.
)

echo [INFO] Starting web server...
echo [INFO] Open http://localhost:8080 in your browser
echo [INFO] Press Ctrl+C to stop the server
echo ============================================================
echo.

python web/app.py

pause
