# Nutrition Planner - Планировщик питания

Приложение для планирования питания на неделю и месяц с расчетом КБЖУ, стоимости и автоматической генерацией списка покупок.

## 🚀 Возможности

- **База рецептов** - добавление и управление рецептами
- **База ингредиентов** - хранение ингредиентов с КБЖУ и ценами
- **Планирование питания** - 6 приемов пищи в день:
  - Завтрак (breakfast)
  - Второй завтрак (second_breakfast)
  - Обед (lunch)
  - Перекус (snack)
  - Ужин (dinner)
  - Второй перекус (second_snack)
- **Расчет КБЖУ** - автоматический расчет калорий, белков, жиров, углеводов
- **Расчет стоимости** - подсчет стоимости каждого приема пищи и дня
- **Список покупок** - автоматическая генерация на основе плана питания
- **REST API** - для интеграции с мобильными приложениями
- **Telegram бот** - готовая интеграция для Telegram

## 📁 Структура проекта

```
nutrition_planner/
├── __init__.py              # Инициализация пакета
├── models/
│   ├── __init__.py
│   └── database.py          # SQLAlchemy модели
├── services/
│   ├── __init__.py
│   └── core_services.py     # Бизнес-логика
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI REST API
│   └── telegram_bot.py      # Telegram бот
├── data/                     # Данные (база данных)
├── requirements.txt          # Зависимости
├── run_server.py            # Запуск API сервера
└── run_bot.py               # Запуск Telegram бота
```

## 🛠 Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:

**Запуск REST API:**
```bash
python run_server.py
```

API будет доступно по адресу: http://localhost:8000

**Запуск Telegram бота:**
```bash
python run_bot.py
```

(Не забудьте указать ваш токен Telegram бота)

## 📡 API Endpoints

### Ингредиенты
- `GET /ingredients/` - получить все ингредиенты
- `POST /ingredients/` - создать ингредиент
- `GET /ingredients/{id}` - получить ингредиент по ID
- `GET /ingredients/search/?q=query` - поиск ингредиентов

### Рецепты
- `GET /recipes/` - получить все рецепты
- `POST /recipes/` - создать рецепт
- `POST /recipes/{id}/ingredients/` - добавить ингредиент к рецепту
- `GET /recipes/{id}` - получить рецепт с КБЖУ
- `GET /recipes/search/?q=query` - поиск рецептов

### План питания
- `GET /meal-plans/{date}/` - получить план на день
- `POST /meal-plans/{date}/` - добавить рецепт в план
- `GET /meal-plans/week/{start_date}` - план на неделю
- `GET /meal-plans/month/{year}/{month}` - план на месяц
- `DELETE /meal-plans/{date}/{meal_type}/{recipe_id}` - удалить рецепт из плана

### Список покупок
- `GET /shopping-list/generate/{start_date}` - сгенерировать список
- `POST /shopping-list/save/` - сохранить список
- `GET /shopping-list/recent/` - недавние списки
- `POST /shopping-list/{id}/purchase/` - отметить как купленное

## 🤖 Telegram бот команды

- `/start` - приветствие
- `/menu` - меню на сегодня
- `/week` - план на неделю
- `/recipes` - список рецептов
- `/shopping` - список покупок
- `/ingredients` - ингредиенты
- `/help` - помощь

## 📱 Интеграция с Android

Приложение предоставляет REST API, которое можно использовать для создания Android приложения:

1. Используйте Retrofit или Volley для HTTP запросов
2. Все endpoints возвращают JSON
3. Поддерживается CORS для мобильных приложений

Пример запроса для получения плана на день:
```kotlin
@GET("meal-plans/{date}")
suspend fun getDailyPlan(@Path("date") date: String): DailyPlanResponse
```

## 💡 Пример использования

```python
from models.database import init_db
from services.core_services import (
    IngredientService, 
    RecipeService, 
    MealPlanService,
    ShoppingListService
)
from datetime import date

# Инициализация БД
db = init_db()

# Создание ингредиентов
ingredient_service = IngredientService(db)
chicken = ingredient_service.create_ingredient(
    name="Куриная грудка",
    calories=165,
    protein=31,
    fat=3.6,
    carbohydrates=0,
    price_per_100g=0.25
)

rice = ingredient_service.create_ingredient(
    name="Рис",
    calories=130,
    protein=2.7,
    fat=0.3,
    carbohydrates=28,
    price_per_100g=0.08
)

# Создание рецепта
recipe_service = RecipeService(db)
recipe = recipe_service.create_recipe(
    name="Курица с рисом",
    description="Простое и вкусное блюдо"
)

# Добавление ингредиентов к рецепту
recipe_service.add_ingredient_to_recipe(recipe.id, chicken.id, 200)  # 200г курицы
recipe_service.add_ingredient_to_recipe(recipe.id, rice.id, 100)  # 100г риса

# Расчет КБЖУ рецепта
nutrition = recipe_service.calculate_recipe_nutrition(recipe.id)
print(f"КБЖУ: {nutrition}")

# Добавление в план питания
meal_plan_service = MealPlanService(db)
today = date.today()
meal_plan_service.add_recipe_to_meal(today, recipe.id, 'lunch')

# Получение плана на день
daily_plan = meal_plan_service.get_meals_by_type(today)
daily_nutrition = meal_plan_service.calculate_daily_nutrition(today)
print(f"План на день: {daily_nutrition}")

# Генерация списка покупок
shopping_service = ShoppingListService(db)
shopping_list = shopping_service.generate_shopping_list_from_week(today)
print(f"Список покупок: {shopping_list}")
```

## 🔧 Конфигурация

По умолчанию используется SQLite база данных `nutrition_planner.db`.

Для изменения базы данных отредактируйте `models/database.py`:
```python
def init_db(database_url='sqlite:///nutrition_planner.db'):
```

Для PostgreSQL:
```python
database_url='postgresql://user:password@localhost/dbname'
```

## 📝 Лицензия

MIT License

## 👥 Авторы

Разработано для планирования питания с возможностью интеграции в Telegram бот и мобильное приложение Android.
