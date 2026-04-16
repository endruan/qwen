# ✅ Исправление ошибки для Windows 10

## Проблема
Ошибка `TypeError: unhashable type: 'dict'` возникала из-за изменений в API Jinja2Templates в новых версиях Starlette/FastAPI.

## Решение
Обновлен файл `web/app.py` - теперь используется правильный синтаксис для `TemplateResponse`:

**БЫЛО (не работало):**
```python
return templates.TemplateResponse("dashboard.html", {
    "request": request,
    "stats": stats,
    ...
})
```

**СТАЛО (работает):**
```python
context = {
    "request": request,
    "stats": stats,
    ...
}
return templates.TemplateResponse(name="dashboard.html", context=context)
```

## Инструкция по запуску на Windows 10

### Шаг 1: Установите зависимости
Откройте командную строку (cmd) и выполните:
```bash
pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart
```

### Шаг 2: Запустите веб-сервер
Перейдите в папку проекта и запустите:
```bash
cd nutrition_planner
python web/app.py
```

Или используйте готовый скрипт:
```bash
python run_combined.py
```

### Шаг 3: Откройте в браузере
- **Веб-интерфейс**: http://localhost:8080
- **API документация**: http://localhost:8000/docs

## Проверка работы
Все страницы должны открываться без ошибок:
- ✅ http://localhost:8080/ - Панель управления
- ✅ http://localhost:8080/ingredients - Ингредиенты
- ✅ http://localhost:8080/recipes - Рецепты
- ✅ http://localhost:8080/meal-planner - Планировщик питания
- ✅ http://localhost:8080/shopping-list - Список покупок

## Если возникают проблемы

### Ошибка "address already in use"
Порт 8080 уже занят. Завершите процесс или используйте другой порт:
```bash
python web/app.py --port 8081
```

### Ошибка импорта модулей
Переустановите зависимости:
```bash
pip uninstall fastapi uvicorn sqlalchemy jinja2
pip install fastapi uvicorn sqlalchemy jinja2 aiofiles python-multipart
```

### Ошибка базы данных
Удалите файл базы данных и перезапустите:
```bash
del nutrition.db
python web/app.py
```

## Поддержка Telegram бота и Android
Приложение включает REST API на порту 8000, которое можно использовать для:
- Telegram бота
- Мобильного приложения на Android
- Других клиентов

API документация доступна по адресу: http://localhost:8000/docs
