@echo off
chcp 65001 >nul
echo ============================================================
echo    Планировщик питания - Запуск на Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python найден
python --version
echo.

REM Install dependencies if needed
echo Проверка зависимостей...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Установка зависимостей...
    pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart
) else (
    echo ✓ Зависимости установлены
)
echo.

REM Initialize database and create sample data
echo Инициализация базы данных...
python -c "from models.database import init_db; from services.core_services import *; db = init_db(); print('✓ База данных готова')"
echo.

echo ============================================================
echo    ЗАПУСК ВЕБ-СЕРВЕРА
echo ============================================================
echo.
echo Откройте браузер: http://localhost:8080
echo.
echo Нажмите Ctrl+C для остановки сервера
echo.

REM Start the web server
python web/app.py

pause
