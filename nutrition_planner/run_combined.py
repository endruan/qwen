#!/usr/bin/env python3
"""
Combined server for Nutrition Planner.
Runs both the REST API and Web frontend on different ports.
"""

import sys
import os
import threading
import time
import webbrowser

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db, Base
from services.core_services import IngredientService, RecipeService, MealPlanService


def create_sample_data():
    """Create sample data for demonstration."""
    db = init_db()
    
    ingredient_service = IngredientService(db)
    recipe_service = RecipeService(db)
    meal_plan_service = MealPlanService(db)
    
    # Check if data already exists
    if ingredient_service.get_all_ingredients():
        print("Sample data already exists.")
        return
    
    print("Creating sample data...")
    
    # Create ingredients
    ingredients_data = [
        {"name": "Куриная грудка", "calories": 165, "protein": 31, "fat": 3.6, "carbohydrates": 0, "price_per_100g": 0.25, "unit": "г"},
        {"name": "Рис", "calories": 130, "protein": 2.7, "fat": 0.3, "carbohydrates": 28, "price_per_100g": 0.08, "unit": "г"},
        {"name": "Яйца", "calories": 155, "protein": 13, "fat": 11, "carbohydrates": 1.1, "price_per_100g": 0.15, "unit": "г"},
        {"name": "Овсянка", "calories": 389, "protein": 17, "fat": 7, "carbohydrates": 66, "price_per_100g": 0.06, "unit": "г"},
        {"name": "Банан", "calories": 89, "protein": 1.1, "fat": 0.3, "carbohydrates": 23, "price_per_100g": 0.12, "unit": "г"},
        {"name": "Творог", "calories": 98, "protein": 11, "fat": 4.3, "carbohydrates": 3.4, "price_per_100g": 0.10, "unit": "г"},
        {"name": "Гречка", "calories": 343, "protein": 13, "fat": 3.4, "carbohydrates": 72, "price_per_100g": 0.07, "unit": "г"},
        {"name": "Лосось", "calories": 208, "protein": 20, "fat": 13, "carbohydrates": 0, "price_per_100g": 0.45, "unit": "г"},
        {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbohydrates": 7, "price_per_100g": 0.15, "unit": "г"},
        {"name": "Молоко", "calories": 42, "protein": 3.4, "fat": 1, "carbohydrates": 5, "price_per_100g": 0.05, "unit": "мл"},
        {"name": "Сыр", "calories": 402, "protein": 25, "fat": 33, "carbohydrates": 1.3, "price_per_100g": 0.35, "unit": "г"},
        {"name": "Хлеб цельнозерновой", "calories": 250, "protein": 13, "fat": 3.5, "carbohydrates": 41, "price_per_100g": 0.08, "unit": "г"},
        {"name": "Авокадо", "calories": 160, "protein": 2, "fat": 15, "carbohydrates": 9, "price_per_100g": 0.20, "unit": "г"},
        {"name": "Оливковое масло", "calories": 884, "protein": 0, "fat": 100, "carbohydrates": 0, "price_per_100g": 0.30, "unit": "мл"},
        {"name": "Орехи грецкие", "calories": 654, "protein": 15, "fat": 65, "carbohydrates": 14, "price_per_100g": 0.40, "unit": "г"},
    ]
    
    created_ingredients = {}
    for ing_data in ingredients_data:
        ing = ingredient_service.create_ingredient(**ing_data)
        created_ingredients[ing.name] = ing
        print(f"  ✓ Ingredient: {ing.name}")
    
    # Create recipes
    recipes_data = [
        {
            "name": "Овсянка с бананом",
            "description": "Полезный завтрак для энергии на весь день",
            "instructions": "1. Сварить овсянку на молоке\n2. Добавить нарезанный банан\n3. Посыпать орехами",
            "prep_time_minutes": 10,
            "servings": 1,
            "ingredients": [
                ("Овсянка", 80),
                ("Молоко", 200),
                ("Банан", 100),
                ("Орехи грецкие", 30)
            ]
        },
        {
            "name": "Омлет с сыром",
            "description": "Белковый завтрак",
            "instructions": "1. Взбить яйца с молоком\n2. Вылить на сковороду\n3. Посыпать сыром и запечь",
            "prep_time_minutes": 15,
            "servings": 1,
            "ingredients": [
                ("Яйца", 150),
                ("Молоко", 50),
                ("Сыр", 50)
            ]
        },
        {
            "name": "Курица с рисом",
            "description": "Классический обед",
            "instructions": "1. Отварить рис\n2. Приготовить куриную грудку\n3. Подавать вместе",
            "prep_time_minutes": 30,
            "servings": 1,
            "ingredients": [
                ("Куриная грудка", 200),
                ("Рис", 100),
                ("Оливковое масло", 10)
            ]
        },
        {
            "name": "Гречка с лососем",
            "description": "Полезный ужин",
            "instructions": "1. Отварить гречку\n2. Запечь лосось\n3. Подать с брокколи",
            "prep_time_minutes": 35,
            "servings": 1,
            "ingredients": [
                ("Гречка", 100),
                ("Лосось", 150),
                ("Брокколи", 150)
            ]
        },
        {
            "name": "Творог с фруктами",
            "description": "Легкий перекус",
            "instructions": "Просто смешайте творог с нарезанными фруктами",
            "prep_time_minutes": 5,
            "servings": 1,
            "ingredients": [
                ("Творог", 200),
                ("Банан", 100)
            ]
        },
        {
            "name": "Сэндвич с авокадо",
            "description": "Быстрый завтрак или перекус",
            "instructions": "1. Поджарить хлеб\n2. Размять авокадо\n3. Намазать на хлеб",
            "prep_time_minutes": 10,
            "servings": 1,
            "ingredients": [
                ("Хлеб цельнозерновой", 100),
                ("Авокадо", 100),
                ("Яйца", 50)
            ]
        }
    ]
    
    from datetime import date, timedelta
    
    for recipe_data in recipes_data:
        ingredients_list = recipe_data.pop("ingredients")
        
        recipe = recipe_service.create_recipe(**recipe_data)
        print(f"  ✓ Recipe: {recipe.name}")
        
        # Add ingredients to recipe
        for ing_name, quantity in ingredients_list:
            if ing_name in created_ingredients:
                recipe_service.add_ingredient_to_recipe(recipe.id, created_ingredients[ing_name].id, quantity)
    
    # Create meal plan for current week
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    all_recipes = recipe_service.get_all_recipes()
    
    meal_types = ['breakfast', 'second_breakfast', 'lunch', 'snack', 'dinner', 'second_snack']
    
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        
        for j, meal_type in enumerate(meal_types):
            if j < len(all_recipes):
                meal_plan_service.add_recipe_to_meal(day_date, all_recipes[j].id, meal_type)
    
    print(f"\n✓ Sample data created successfully!")
    print(f"  - {len(created_ingredients)} ingredients")
    print(f"  - {len(recipes_data)} recipes")
    print(f"  - Meal plan for the week")


def run_api_server():
    """Run the REST API server."""
    from api.main import app
    import uvicorn
    print("\n🚀 Starting REST API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


def run_web_server():
    """Run the Web frontend server."""
    from web.app import app
    import uvicorn
    print("\n🌐 Starting Web frontend on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


def open_browser():
    """Open browser after servers start."""
    time.sleep(2)
    webbrowser.open("http://localhost:8080")
    print("\n✨ Opening web interface in browser...")


if __name__ == "__main__":
    print("=" * 60)
    print("       NUTRITION PLANNER - Starting Servers")
    print("=" * 60)
    
    # Initialize database
    print("\n📦 Initializing database...")
    db = init_db()
    print("✓ Database ready")
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 60)
    print("Starting servers...")
    print("=" * 60)
    
    # Start API server in a thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Small delay before starting web server
    time.sleep(1)
    
    # Start web server in a thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Open browser
    open_browser()
    
    print("\n" + "=" * 60)
    print("Servers are running!")
    print("=" * 60)
    print("\n📍 Web Interface: http://localhost:8080")
    print("🔌 REST API:      http://localhost:8000")
    print("📖 API Docs:     http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all servers\n")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down servers...")
        sys.exit(0)
