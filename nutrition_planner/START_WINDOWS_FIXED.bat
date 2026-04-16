@echo off
chcp 65001 >nul
echo ============================================================
echo   Nutrition Planner - Веб-интерфейс для Windows
echo ============================================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo [OK] Python найден
echo.

REM Установка зависимостей
echo [INFO] Проверка зависимостей...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Установка FastAPI и зависимостей...
    pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart
) else (
    echo [OK] Зависимости установлены
)
echo.

REM Инициализация базы данных
echo [INFO] Инициализация базы данных...
python -c "from models.database import init_db; init_db()" 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Возможна проблема с базой данных, но продолжаем...
)
echo.

REM Запуск сервера
echo ============================================================
echo   Запуск веб-сервера...
echo   Откройте браузер: http://localhost:8080
echo   Для остановки нажмите: Ctrl+C
echo ============================================================
echo.

cd /d "%~dp0"
python web\app.py

pause
