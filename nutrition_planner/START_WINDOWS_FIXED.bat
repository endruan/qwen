@echo off
chcp 65001 >nul
echo ============================================================
echo    Nutrition Planner - Веб-интерфейс
echo ============================================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден! Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo [OK] Python найден
echo.

REM Установка зависимостей
echo Установка необходимых библиотек...
pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart -q
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить библиотеки!
    pause
    exit /b 1
)
echo [OK] Все библиотеки установлены
echo.

REM Инициализация базы данных
echo Инициализация базы данных...
python -c "from models.database import init_db; init_db()" 2>nul
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: Возможны проблемы с базой данных
) else (
    echo [OK] База данных готова
)
echo.

echo ============================================================
echo Запуск веб-сервера...
echo ============================================================
echo.
echo Откройте в браузере: http://localhost:8080
echo.
echo Для остановки нажмите Ctrl+C
echo ============================================================
echo.

python web/app.py

pause
