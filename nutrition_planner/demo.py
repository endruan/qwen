from models.database import init_db, SessionLocal, Ingredient, Recipe, MealPlan, MealPlanRecipe, User
from services.services import IngredientService, RecipeService, MealPlanService, UserService
from datetime import date, timedelta

def run_demo():
    """Создание демо-данных для тестирования"""
    
    print("=" * 60)
    print("🍽️  NUTRITION PLANNER - DEMO")
    print("=" * 60)
    
    # Инициализация БД
    print("\n🔧 Initializing database...")
    init_db()
    print("  ✓ Database initialized")
    
    db = SessionLocal()
    
    try:
        # Создаем ингредиенты
        print("\n📦 Creating sample data...")
        
        ingredient_service = IngredientService(db)
        
        ingredients_data = [
            {"name": "Куриная грудка", "calories_per_100g": 165, "protein_per_100g": 31, "fat_per_100g": 3.6, "carbs_per_100g": 0, "price_per_package": 250, "package_weight": 1000, "unit": "г"},
            {"name": "Рис белый", "calories_per_100g": 130, "protein_per_100g": 2.7, "fat_per_100g": 0.3, "carbs_per_100g": 28, "price_per_package": 80, "package_weight": 1000, "unit": "г"},
            {"name": "Яйца", "calories_per_100g": 155, "protein_per_100g": 13, "fat_per_100g": 11, "carbs_per_100g": 1.1, "price_per_package": 100, "package_weight": 500, "unit": "г"},
            {"name": "Овсянка", "calories_per_100g": 389, "protein_per_100g": 16.9, "fat_per_100g": 6.9, "carbs_per_100g": 66, "price_per_package": 60, "package_weight": 1000, "unit": "г"},
            {"name": "Бананы", "calories_per_100g": 89, "protein_per_100g": 1.1, "fat_per_100g": 0.3, "carbs_per_100g": 23, "price_per_package": 120, "package_weight": 1000, "unit": "г"},
            {"name": "Творог", "calories_per_100g": 121, "protein_per_100g": 18, "fat_per_100g": 5, "carbs_per_100g": 3, "price_per_package": 150, "package_weight": 500, "unit": "г"},
            {"name": "Гречка", "calories_per_100g": 343, "protein_per_100g": 13, "fat_per_100g": 3.4, "carbs_per_100g": 72, "price_per_package": 70, "package_weight": 1000, "unit": "г"},
            {"name": "Лосось", "calories_per_100g": 208, "protein_per_100g": 20, "fat_per_100g": 13, "carbs_per_100g": 0, "price_per_package": 800, "package_weight": 1000, "unit": "г"},
            {"name": "Брокколи", "calories_per_100g": 34, "protein_per_100g": 2.8, "fat_per_100g": 0.4, "carbs_per_100g": 7, "price_per_package": 180, "package_weight": 1000, "unit": "г"},
            {"name": "Оливковое масло", "calories_per_100g": 884, "protein_per_100g": 0, "fat_per_100g": 100, "carbs_per_100g": 0, "price_per_package": 500, "package_weight": 1000, "unit": "мл"},
            {"name": "Молоко", "calories_per_100g": 42, "protein_per_100g": 3.4, "fat_per_100g": 1, "carbs_per_100g": 5, "price_per_package": 100, "package_weight": 1000, "unit": "мл"},
            {"name": "Хлеб цельнозерновой", "calories_per_100g": 265, "protein_per_100g": 13, "fat_per_100g": 3.4, "carbs_per_100g": 57, "price_per_package": 100, "package_weight": 500, "unit": "г"},
            {"name": "Авокадо", "calories_per_100g": 160, "protein_per_100g": 2, "fat_per_100g": 15, "carbs_per_100g": 9, "price_per_package": 150, "package_weight": 200, "unit": "г"},
            {"name": "Орехи грецкие", "calories_per_100g": 654, "protein_per_100g": 15, "fat_per_100g": 65, "carbs_per_100g": 14, "price_per_package": 300, "package_weight": 200, "unit": "г"},
            {"name": "Яблоки", "calories_per_100g": 52, "protein_per_100g": 0.3, "fat_per_100g": 0.2, "carbs_per_100g": 14, "price_per_package": 100, "package_weight": 1000, "unit": "г"},
        ]
        
        for ing_data in ingredients_data:
            try:
                ingredient_service.create(**ing_data)
                print(f"  ✓ Добавлен ингредиент: {ing_data['name']}")
            except Exception as e:
                print(f"  ⚠ {ing_data['name']} уже существует")
        
        # Создаем рецепты
        recipe_service = RecipeService(db)
        
        recipes_data = [
            {
                "name": "Омлет с овощами",
                "description": "<p>Вкусный и полезный завтрак</p>",
                "servings": 2,
                "prep_time": 5,
                "cook_time": 10,
                "ingredients": [
                    {"ingredient_id": 3, "quantity": 200},  # Яйца
                    {"ingredient_id": 11, "quantity": 100},  # Молоко
                    {"ingredient_id": 9, "quantity": 50},    # Брокколи
                ]
            },
            {
                "name": "Овсяная каша с бананом",
                "description": "<p>Классический завтрак</p>",
                "servings": 2,
                "prep_time": 2,
                "cook_time": 15,
                "ingredients": [
                    {"ingredient_id": 4, "quantity": 160},  # Овсянка
                    {"ingredient_id": 5, "quantity": 200},  # Бананы
                    {"ingredient_id": 11, "quantity": 400}, # Молоко
                ]
            },
            {
                "name": "Курица с рисом",
                "description": "<p>Классический обед</p>",
                "servings": 4,
                "prep_time": 10,
                "cook_time": 30,
                "ingredients": [
                    {"ingredient_id": 1, "quantity": 800},  # Куриная грудка
                    {"ingredient_id": 2, "quantity": 400},  # Рис
                    {"ingredient_id": 10, "quantity": 20},  # Оливковое масло
                ]
            },
            {
                "name": "Гречка с лососем",
                "description": "<p>Полезный ужин</p>",
                "servings": 2,
                "prep_time": 5,
                "cook_time": 20,
                "ingredients": [
                    {"ingredient_id": 7, "quantity": 200},  # Гречка
                    {"ingredient_id": 8, "quantity": 300},  # Лосось
                    {"ingredient_id": 9, "quantity": 200},  # Брокколи
                ]
            },
            {
                "name": "Творог с фруктами",
                "description": "<p>Легкий перекус</p>",
                "servings": 2,
                "prep_time": 5,
                "cook_time": 0,
                "ingredients": [
                    {"ingredient_id": 6, "quantity": 400},  # Творог
                    {"ingredient_id": 15, "quantity": 200}, # Яблоки
                    {"ingredient_id": 13, "quantity": 60},  # Орехи
                ]
            },
            {
                "name": "Сэндвич с авокадо",
                "description": "<p>Быстрый перекус</p>",
                "servings": 2,
                "prep_time": 5,
                "cook_time": 0,
                "ingredients": [
                    {"ingredient_id": 12, "quantity": 200}, # Хлеб
                    {"ingredient_id": 13, "quantity": 200}, # Авокадо
                ]
            },
            {
                "name": "Салат с яблоком и орехами",
                "description": "<p>Легкий салат</p>",
                "servings": 2,
                "prep_time": 10,
                "cook_time": 0,
                "ingredients": [
                    {"ingredient_id": 15, "quantity": 300}, # Яблоки
                    {"ingredient_id": 14, "quantity": 60},  # Орехи
                    {"ingredient_id": 6, "quantity": 200},  # Творог
                ]
            }
        ]
        
        for recipe_data in recipes_data:
            ingredients = recipe_data.pop('ingredients')
            try:
                recipe_service.create(ingredients_data=ingredients, **recipe_data)
                print(f"  ✓ Добавлен рецепт: {recipe_data['name']}")
            except Exception as e:
                print(f"  ⚠ Рецепт {recipe_data['name']} уже существует")
        
        # Создаем план питания на неделю
        print("\n📅 Creating weekly meal plan...")
        meal_plan_service = MealPlanService(db)
        
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        meal_types = ['breakfast', 'second_breakfast', 'lunch', 'snack', 'dinner', 'second_snack']
        recipes = recipe_service.get_all()
        
        if len(recipes) >= 6:
            for i in range(7):
                current_date = start_of_week + timedelta(days=i)
                day_name = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][i]
                print(f"\n  {day_name} ({current_date.strftime('%d.%m')}):")
                
                for j, meal_type in enumerate(meal_types):
                    meal_plan = meal_plan_service.create_or_get_meal_plan(current_date, meal_type)
                    
                    # Выбираем рецепт по индексу
                    recipe_index = (i + j) % len(recipes)
                    recipe = recipes[recipe_index]
                    
                    meal_plan_service.add_recipe_to_meal(meal_plan.id, recipe.id, servings=1)
                    print(f"    {meal_type}: {recipe.name}")
            
            print("\n  ✓ План на неделю создан!")
        
        # Показываем итог за сегодня
        print("\n📊 Daily Summary for Today:")
        print("=" * 50)
        
        today_plan = meal_plan_service.get_day_plan(today)
        
        meal_names = {
            'breakfast': '🌅 Завтрак',
            'second_breakfast': '☕ Второй завтрак',
            'lunch': '🍲 Обед',
            'snack': '🥜 Перекус',
            'dinner': '🌙 Ужин',
            'second_snack': '🍵 Второй перекус'
        }
        
        for meal_type, meal_name in meal_names.items():
            print(f"\n{meal_name}:")
            for recipe in today_plan[meal_type].get('recipes', []):
                print(f"  • {recipe['name']}")
                print(f"    КБЖУ: {recipe['calories']:.0f} ккал | Б: {recipe['protein']:.1f}г | Ж: {recipe['fat']:.1f}г | У: {recipe['carbs']:.1f}г")
                print(f"    Цена: {recipe['cost']:.2f}₽")
        
        print("\n" + "=" * 50)
        print("💰 ИТОГО ЗА ДЕНЬ:")
        totals = today_plan['_totals']
        print(f"  Калории: {totals['calories']:.0f} ккал")
        print(f"  Белки: {totals['protein']:.1f}г")
        print(f"  Жиры: {totals['fat']:.1f}г")
        print(f"  Углеводы: {totals['carbs']:.1f}г")
        print(f"  Стоимость: {totals['cost']:.2f}₽")
        
        # Список покупок
        print("\n🛒 Shopping List:")
        print("=" * 50)
        
        shopping_list_service = None
        from services.services import ShoppingListService
        shopping_list_service = ShoppingListService(db)
        shopping_list = shopping_list_service.generate_from_week_plan()
        
        for item in shopping_list:
            print(f"\n• {item['name']}")
            print(f"  Количество: {item['quantity']:.0f}{item['unit']}")
            print(f"  Цена: {item['cost']:.2f}₽")
        
        total_cost = sum(item['cost'] for item in shopping_list)
        print("\n" + "=" * 50)
        print(f"💰 ОБЩАЯ СТОИМОСТЬ: {total_cost:.2f}₽")
        
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    
    print("\n📡 To start the web server, run:")
    print("   cd nutrition_planner")
    print("   python web/app.py")
    print("\n📚 Web Interface available at:")
    print("   http://localhost:8080")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()
