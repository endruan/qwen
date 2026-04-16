"""
Demo script to showcase the Nutrition Planner functionality.
Creates sample data and demonstrates all features.
"""

import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db
from services.core_services import (
    IngredientService,
    RecipeService,
    MealPlanService,
    ShoppingListService
)


def create_sample_data(db):
    """Create sample ingredients and recipes."""
    print("📦 Creating sample data...")
    
    ingredient_service = IngredientService(db)
    recipe_service = RecipeService(db)
    
    # Create sample ingredients
    ingredients_data = [
        {"name": "Куриная грудка", "calories": 165, "protein": 31, "fat": 3.6, "carbohydrates": 0, "price_per_100g": 0.25},
        {"name": "Рис белый", "calories": 130, "protein": 2.7, "fat": 0.3, "carbohydrates": 28, "price_per_100g": 0.08},
        {"name": "Яйца", "calories": 155, "protein": 13, "fat": 11, "carbohydrates": 1.1, "price_per_100g": 0.20},
        {"name": "Овсянка", "calories": 389, "protein": 16.9, "fat": 6.9, "carbohydrates": 66, "price_per_100g": 0.06},
        {"name": "Бананы", "calories": 89, "protein": 1.1, "fat": 0.3, "carbohydrates": 23, "price_per_100g": 0.12},
        {"name": "Творог", "calories": 98, "protein": 11, "fat": 4.3, "carbohydrates": 3.4, "price_per_100g": 0.15},
        {"name": "Гречка", "calories": 110, "protein": 4.2, "fat": 1.1, "carbohydrates": 21, "price_per_100g": 0.07},
        {"name": "Лосось", "calories": 208, "protein": 20, "fat": 13, "carbohydrates": 0, "price_per_100g": 0.80},
        {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbohydrates": 7, "price_per_100g": 0.18},
        {"name": "Оливковое масло", "calories": 884, "protein": 0, "fat": 100, "carbohydrates": 0, "price_per_100g": 0.50},
        {"name": "Молоко", "calories": 42, "protein": 3.4, "fat": 1, "carbohydrates": 5, "price_per_100g": 0.05},
        {"name": "Хлеб цельнозерновой", "calories": 265, "protein": 13, "fat": 3.5, "carbohydrates": 45, "price_per_100g": 0.10},
        {"name": "Авокадо", "calories": 160, "protein": 2, "fat": 15, "carbohydrates": 9, "price_per_100g": 0.30},
        {"name": "Орехи грецкие", "calories": 654, "protein": 15, "fat": 65, "carbohydrates": 14, "price_per_100g": 0.60},
        {"name": "Яблоки", "calories": 52, "protein": 0.3, "fat": 0.2, "carbohydrates": 14, "price_per_100g": 0.10},
    ]
    
    created_ingredients = {}
    for ing_data in ingredients_data:
        try:
            ingredient = ingredient_service.create_ingredient(**ing_data)
            created_ingredients[ing_data["name"]] = ingredient
            print(f"  ✓ Добавлен ингредиент: {ingredient.name}")
        except Exception as e:
            # Ingredient might already exist
            existing = ingredient_service.search_ingredients(ing_data["name"])[0]
            created_ingredients[ing_data["name"]] = existing
            print(f"  ⚠ Ингредиент уже существует: {ing_data['name']}")
    
    # Create sample recipes
    recipes_data = [
        {
            "name": "Омлет с овощами",
            "description": "Завтрак из яиц с овощами",
            "ingredients": [
                {"name": "Яйца", "quantity": 150},
                {"name": "Молоко", "quantity": 50},
                {"name": "Брокколи", "quantity": 100}
            ]
        },
        {
            "name": "Овсяная каша с бананом",
            "description": "Полезный завтрак",
            "ingredients": [
                {"name": "Овсянка", "quantity": 80},
                {"name": "Молоко", "quantity": 200},
                {"name": "Бананы", "quantity": 100}
            ]
        },
        {
            "name": "Курица с рисом",
            "description": "Классический обед",
            "ingredients": [
                {"name": "Куриная грудка", "quantity": 200},
                {"name": "Рис белый", "quantity": 100},
                {"name": "Оливковое масло", "quantity": 10}
            ]
        },
        {
            "name": "Гречка с лососем",
            "description": "Полезный ужин",
            "ingredients": [
                {"name": "Гречка", "quantity": 100},
                {"name": "Лосось", "quantity": 150},
                {"name": "Брокколи", "quantity": 150}
            ]
        },
        {
            "name": "Творог с фруктами",
            "description": "Легкий перекус",
            "ingredients": [
                {"name": "Творог", "quantity": 200},
                {"name": "Бананы", "quantity": 100},
                {"name": "Орехи грецкие", "quantity": 30}
            ]
        },
        {
            "name": "Сэндвич с авокадо",
            "description": "Быстрый завтрак",
            "ingredients": [
                {"name": "Хлеб цельнозерновой", "quantity": 100},
                {"name": "Авокадо", "quantity": 100},
                {"name": "Яйца", "quantity": 100}
            ]
        },
        {
            "name": "Салат с яблоком и орехами",
            "description": "Витаминный перекус",
            "ingredients": [
                {"name": "Яблоки", "quantity": 150},
                {"name": "Орехи грецкие", "quantity": 50},
                {"name": "Творог", "quantity": 100}
            ]
        }
    ]
    
    created_recipes = {}
    for recipe_data in recipes_data:
        try:
            recipe = recipe_service.create_recipe(
                name=recipe_data["name"],
                description=recipe_data["description"]
            )
            
            for ing_item in recipe_data["ingredients"]:
                ingredient = created_ingredients.get(ing_item["name"])
                if ingredient:
                    recipe_service.add_ingredient_to_recipe(
                        recipe.id,
                        ingredient.id,
                        ing_item["quantity"]
                    )
            
            created_recipes[recipe_data["name"]] = recipe
            print(f"  ✓ Добавлен рецепт: {recipe.name}")
        except Exception as e:
            print(f"  ⚠ Ошибка при создании рецепта {recipe_data['name']}: {e}")
    
    return created_ingredients, created_recipes


def create_weekly_plan(db, recipes):
    """Create a sample weekly meal plan."""
    print("\n📅 Creating weekly meal plan...")
    
    meal_plan_service = MealPlanService(db)
    today = date.today()
    
    meal_types = ['breakfast', 'second_breakfast', 'lunch', 'snack', 'dinner', 'second_snack']
    recipe_list = list(recipes.values())
    
    for day_offset in range(7):
        current_date = today + timedelta(days=day_offset)
        day_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][day_offset]
        print(f"\n  {day_name} ({current_date.strftime('%d.%m')}):")
        
        for i, meal_type in enumerate(meal_types):
            if i < len(recipe_list):
                recipe = recipe_list[i % len(recipe_list)]
                meal_plan_service.add_recipe_to_meal(current_date, recipe.id, meal_type)
                print(f"    {meal_type}: {recipe.name}")
    
    print("\n  ✓ План на неделю создан!")


def show_daily_summary(db):
    """Show summary for today."""
    from datetime import date
    
    print("\n📊 Daily Summary for Today:")
    print("=" * 50)
    
    meal_plan_service = MealPlanService(db)
    today = date.today()
    
    meals = meal_plan_service.get_meals_by_type(today)
    nutrition = meal_plan_service.calculate_daily_nutrition(today)
    
    meal_names_ru = {
        'breakfast': '🌅 Завтрак',
        'second_breakfast': '☕ Второй завтрак',
        'lunch': '🍲 Обед',
        'snack': '🥜 Перекус',
        'dinner': '🌙 Ужин',
        'second_snack': '🍵 Второй перекус'
    }
    
    for meal_type, recipes in meals.items():
        if recipes:
            print(f"\n{meal_names_ru.get(meal_type, meal_type)}:")
            for recipe in recipes:
                n = recipe['nutrition']
                print(f"  • {recipe['name']}")
                print(f"    КБЖУ: {n['calories']:.0f} ккал | Б: {n['protein']:.1f}г | Ж: {n['fat']:.1f}г | У: {n['carbohydrates']:.1f}г")
                print(f"    Цена: {n['price']:.2f}₽")
    
    if nutrition['daily_total']['calories'] > 0:
        daily = nutrition['daily_total']
        print("\n" + "=" * 50)
        print("💰 ИТОГО ЗА ДЕНЬ:")
        print(f"  Калории: {daily['calories']:.0f} ккал")
        print(f"  Белки: {daily['protein']:.1f}г")
        print(f"  Жиры: {daily['fat']:.1f}г")
        print(f"  Углеводы: {daily['carbohydrates']:.1f}г")
        print(f"  Стоимость: {daily['price']:.2f}₽")
    else:
        print("\n⚠️  Меню на сегодня пустое!")


def generate_shopping_list(db):
    """Generate and display shopping list."""
    from datetime import date, timedelta
    
    print("\n🛒 Shopping List:")
    print("=" * 50)
    
    shopping_service = ShoppingListService(db)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    shopping_list = shopping_service.generate_shopping_list_from_week(start_of_week)
    
    if not shopping_list:
        print("  Список покупок пуст. Сначала создайте план питания.")
        return
    
    total_price = 0
    for item in shopping_list:
        print(f"\n• {item['name']}")
        print(f"  Количество: {item['quantity_needed']:.0f}{item['unit']}")
        print(f"  Цена: {item['estimated_price']:.2f}₽")
        total_price += item['estimated_price']
    
    print("\n" + "=" * 50)
    print(f"💰 ОБЩАЯ СТОИМОСТЬ: {total_price:.2f}₽")


def main():
    """Main demo function."""
    print("=" * 60)
    print("🍽️  NUTRITION PLANNER - DEMO")
    print("=" * 60)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    db = init_db()
    print("  ✓ Database initialized")
    
    # Create sample data
    ingredients, recipes = create_sample_data(db)
    
    # Create weekly meal plan
    create_weekly_plan(db, recipes)
    
    # Show daily summary
    show_daily_summary(db)
    
    # Generate shopping list
    generate_shopping_list(db)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    print("\n📡 To start the API server, run:")
    print("   python run_server.py")
    print("\n🤖 To start the Telegram bot, run:")
    print("   python run_bot.py")
    print("\n📚 API Documentation available at:")
    print("   http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
