from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
import random

from models import Base, Ingredient, Recipe, RecipeIngredient, MealPlan, UserProfile, WeightLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./nutrition.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def create_sample_data():
    db = SessionLocal()
    try:
        print("📦 Создание демо-данных...")
        
        # Проверка наличия данных
        existing = db.query(Ingredient).first()
        if existing:
            print("⚠️ База уже содержит данные. Пропускаем создание демо-данных.")
            return
        
        # Ингредиенты с учетом новой логики цены и упаковки
        ingredients_data = [
            {"name": "Куриная грудка", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "price": 250, "package_weight": 1000, "unit": "г"},
            {"name": "Рис белый", "calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28, "price": 80, "package_weight": 1000, "unit": "г"},
            {"name": "Яйца", "calories": 155, "protein": 13, "fat": 11, "carbs": 1.1, "price": 120, "package_weight": 10, "unit": "шт"},
            {"name": "Овсянка", "calories": 389, "protein": 16.9, "fat": 6.9, "carbs": 66, "price": 60, "package_weight": 500, "unit": "г"},
            {"name": "Бананы", "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23, "price": 120, "package_weight": 1000, "unit": "г"},
            {"name": "Творог 5%", "calories": 121, "protein": 17, "fat": 5, "carbs": 1.8, "price": 150, "package_weight": 500, "unit": "г"},
            {"name": "Гречка", "calories": 343, "protein": 13, "fat": 3.4, "carbs": 72, "price": 70, "package_weight": 900, "unit": "г"},
            {"name": "Лосось", "calories": 208, "protein": 20, "fat": 13, "carbs": 0, "price": 800, "package_weight": 1000, "unit": "г"},
            {"name": "Брокколи", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7, "price": 180, "package_weight": 500, "unit": "г"},
            {"name": "Оливковое масло", "calories": 884, "protein": 0, "fat": 100, "carbs": 0, "price": 400, "package_weight": 500, "unit": "мл"},
            {"name": "Молоко 2.5%", "calories": 52, "protein": 2.8, "fat": 2.5, "carbs": 4.7, "price": 80, "package_weight": 1000, "unit": "мл"},
            {"name": "Хлеб цельнозерновой", "calories": 250, "protein": 8, "fat": 3, "carbs": 45, "price": 100, "package_weight": 400, "unit": "г"},
            {"name": "Авокадо", "calories": 160, "protein": 2, "fat": 14.7, "carbs": 8.5, "price": 150, "package_weight": 200, "unit": "шт"},
            {"name": "Орехи грецкие", "calories": 654, "protein": 15, "fat": 65, "carbs": 14, "price": 300, "package_weight": 200, "unit": "г"},
            {"name": "Яблоки", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14, "price": 100, "package_weight": 1000, "unit": "г"},
        ]
        
        ingredients = []
        for ing_data in ingredients_data:
            ing = Ingredient(**ing_data)
            db.add(ing)
            ingredients.append(ing)
            print(f"  ✓ Добавлен ингредиент: {ing.name}")
        
        db.commit()
        
        # Рецепты
        recipes_data = [
            {
                "name": "Омлет с овощами",
                "description": "<p>Взбейте яйца с молоком, добавьте нарезанные овощи. Жарьте на медленном огне 5-7 минут.</p>",
                "servings": 2,
                "ingredients": [(0, 100), (2, 2), (8, 50), (10, 30)]  # (index_in_ingredients, weight_in_grams)
            },
            {
                "name": "Овсяная каша с бананом",
                "description": "<p>Сварите овсянку на молоке или воде. Добавьте нарезанный банан и орехи.</p>",
                "servings": 1,
                "ingredients": [(3, 80), (4, 100), (13, 20), (10, 100)]
            },
            {
                "name": "Курица с рисом",
                "description": "<p>Отварите рис. Куриную грудку запеките в духовке с брокколи. Подавайте вместе.</p>",
                "servings": 2,
                "ingredients": [(0, 300), (1, 150), (8, 200), (9, 10)]
            },
            {
                "name": "Гречка с лососем",
                "description": "<p>Отварите гречку. Лосось приготовьте на гриле или в духовке. Подавайте с зеленью.</p>",
                "servings": 2,
                "ingredients": [(6, 150), (7, 200), (9, 10)]
            },
            {
                "name": "Творог с фруктами",
                "description": "<p>Смешайте творог с нарезанными яблоками и бананами. Можно добавить немного меда.</p>",
                "servings": 1,
                "ingredients": [(5, 200), (14, 100), (4, 50)]
            },
            {
                "name": "Сэндвич с авокадо",
                "description": "<p>Намажьте размятое авокадо на хлеб. Добавьте яйцо пашот или вареное.</p>",
                "servings": 1,
                "ingredients": [(11, 100), (12, 100), (2, 1)]
            },
            {
                "name": "Салат с яблоком и орехами",
                "description": "<p>Нарежьте яблоки, добавьте измельченные орехи. Заправьте йогуртом или медом.</p>",
                "servings": 1,
                "ingredients": [(14, 150), (13, 30), (5, 100)]
            }
        ]
        
        recipes = []
        for recipe_data in recipes_data:
            recipe = Recipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                servings=recipe_data["servings"]
            )
            db.add(recipe)
            db.flush()
            
            for ing_idx, weight in recipe_data["ingredients"]:
                ri = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredients[ing_idx].id,
                    weight=weight
                )
                db.add(ri)
            
            recipes.append(recipe)
            print(f"  ✓ Добавлен рецепт: {recipe.name}")
        
        db.commit()
        
        # План питания на неделю
        meal_types = ["breakfast", "second_breakfast", "lunch", "snack", "dinner", "second_snack"]
        today = date.today()
        
        print("\n📅 Создание плана питания на неделю...")
        for day_offset in range(7):
            current_date = today + timedelta(days=day_offset)
            day_name = current_date.strftime("%A")
            print(f"\n  {day_name} ({current_date}):")
            
            for i, meal_type in enumerate(meal_types):
                recipe = recipes[i % len(recipes)]
                plan = MealPlan(
                    date=current_date,
                    meal_type=meal_type,
                    recipe_id=recipe.id,
                    servings_count=1.0
                )
                db.add(plan)
                print(f"    {meal_type}: {recipe.name}")
        
        db.commit()
        print("\n  ✓ План на неделю создан!")
        
        # Профиль пользователя по умолчанию
        profile = UserProfile(
            current_weight=75.0,
            target_calories=2200,
            target_protein=150.0,
            target_fat=70.0,
            target_carbs=250.0
        )
        db.add(profile)
        
        # История веса
        for i in range(5):
            log = WeightLog(
                date=today - timedelta(days=i*7),
                weight=75.0 + random.uniform(-1, 1),
                waist=85.0 + random.uniform(-1, 1)
            )
            db.add(log)
        
        db.commit()
        
        print("\n✅ Демо-данные успешно созданы!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    create_sample_data()
