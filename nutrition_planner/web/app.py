from fastapi import FastAPI, Request, Form, HTTPException, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import Optional
import json
import os
from pathlib import Path

from models.database import init_db, get_db, User, DATABASE_URL
from services.services import UserService, IngredientService, RecipeService, MealPlanService, ShoppingListService

# Инициализация приложения
app = FastAPI(title="Nutrition Planner")

# Пути
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"

# Создаем директории
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Шаблоны
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Инициализация БД
init_db()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_current_user(db: Session):
    """Получить текущего пользователя (пока один пользователь по умолчанию)"""
    user_service = UserService(db)
    return user_service.get_or_create_user()

# ==================== МАРШРУТЫ ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Главная панель"""
    user = get_current_user(db)
    user_service = UserService(db)
    
    # Получаем замеры
    measurements = user_service.get_measurements_history(user.id, days=30)
    
    # Рассчитываем ИМТ
    bmi = 0
    bmi_category = ""
    if user.weight and user.height:
        bmi = user_service.calculate_bmi(user.weight, user.height)
        bmi_category = user_service.get_bmi_category(bmi)
    
    # План на сегодня
    meal_plan_service = MealPlanService(db)
    today_plan = meal_plan_service.get_day_plan(date.today())
    
    # Цели
    targets = {
        'calories': user.target_calories,
        'protein': user.target_protein,
        'fat': user.target_fat,
        'carbs': user.target_carbs
    }
    
    # Остаток до цели
    remaining = {
        'calories': targets['calories'] - today_plan['_totals']['calories'],
        'protein': targets['protein'] - today_plan['_totals']['protein'],
        'fat': targets['fat'] - today_plan['_totals']['fat'],
        'carbs': targets['carbs'] - today_plan['_totals']['carbs']
    }
    
    context = {
        "request": request,
        "user": user,
        "today": date.today(),
        "bmi": round(bmi, 1),
        "bmi_category": bmi_category,
        "measurements": measurements,
        "today_plan": today_plan,
        "targets": targets,
        "remaining": remaining,
        "active_page": "dashboard"
    }
    
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    """Профиль пользователя"""
    user = get_current_user(db)
    user_service = UserService(db)
    
    measurements = user_service.get_measurements_history(user.id, days=90)
    supplements = user_service.get_supplements(user.id)
    
    bmi = 0
    if user.weight and user.height:
        bmi = user_service.calculate_bmi(user.weight, user.height)
    
    context = {
        "request": request,
        "user": user,
        "bmi": round(bmi, 1),
        "measurements": measurements,
        "supplements": supplements,
        "active_page": "profile"
    }
    
    return templates.TemplateResponse("profile.html", context)

@app.post("/profile/update")
async def update_profile(
    request: Request,
    name: str = Form(None),
    weight: float = Form(None),
    height: float = Form(None),
    age: int = Form(None),
    gender: str = Form(None),
    activity_level: str = Form(None),
    target_calories: int = Form(None),
    target_protein: float = Form(None),
    target_fat: float = Form(None),
    target_carbs: float = Form(None),
    db: Session = Depends(get_db)
):
    """Обновление профиля"""
    user = get_current_user(db)
    user_service = UserService(db)
    
    update_data = {}
    if name: update_data['name'] = name
    if weight: update_data['weight'] = weight
    if height: update_data['height'] = height
    if age: update_data['age'] = age
    if gender: update_data['gender'] = gender
    if activity_level: update_data['activity_level'] = activity_level
    if target_calories: update_data['target_calories'] = target_calories
    if target_protein: update_data['target_protein'] = target_protein
    if target_fat: update_data['target_fat'] = target_fat
    if target_carbs: update_data['target_carbs'] = target_carbs
    
    user_service.update_user(user.id, **update_data)
    
    return RedirectResponse(url="/profile", status_code=303)

@app.post("/profile/add-measurement")
async def add_measurement(
    request: Request,
    date_str: str = Form(None),
    weight: float = Form(None),
    chest: float = Form(None),
    waist: float = Form(None),
    hips: float = Form(None),
    bicep: float = Form(None),
    thigh: float = Form(None),
    neck: float = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Добавление замера"""
    user = get_current_user(db)
    user_service = UserService(db)
    
    measurement_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    
    user_service.add_measurement(
        user_id=user.id,
        date=measurement_date,
        weight=weight,
        chest=chest,
        waist=waist,
        hips=hips,
        bicep=bicep,
        thigh=thigh,
        neck=neck,
        notes=notes
    )
    
    return RedirectResponse(url="/profile", status_code=303)

@app.post("/profile/add-supplement")
async def add_supplement(
    request: Request,
    name: str = Form(...),
    dosage: str = Form(None),
    frequency: str = Form(None),
    time_of_day: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Добавление добавки"""
    user = get_current_user(db)
    user_service = UserService(db)
    
    user_service.add_supplement(
        user_id=user.id,
        name=name,
        dosage=dosage,
        frequency=frequency,
        time_of_day=time_of_day,
        notes=notes
    )
    
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/ingredients", response_class=HTMLResponse)
async def ingredients(request: Request, db: Session = Depends(get_db)):
    """Страница ингредиентов"""
    ingredient_service = IngredientService(db)
    ingredients = ingredient_service.get_all()
    
    context = {
        "request": request,
        "ingredients": ingredients,
        "active_page": "ingredients"
    }
    
    return templates.TemplateResponse("ingredients.html", context)

@app.post("/ingredients/create")
async def create_ingredient(
    request: Request,
    name: str = Form(...),
    calories_per_100g: float = Form(0),
    protein_per_100g: float = Form(0),
    fat_per_100g: float = Form(0),
    carbs_per_100g: float = Form(0),
    price_per_package: float = Form(0),
    package_weight: float = Form(1000),
    unit: str = Form("г"),
    category: str = Form(None),
    db: Session = Depends(get_db)
):
    """Создание ингредиента"""
    ingredient_service = IngredientService(db)
    
    ingredient_service.create(
        name=name,
        calories_per_100g=calories_per_100g,
        protein_per_100g=protein_per_100g,
        fat_per_100g=fat_per_100g,
        carbs_per_100g=carbs_per_100g,
        price_per_package=price_per_package,
        package_weight=package_weight,
        unit=unit,
        category=category
    )
    
    return RedirectResponse(url="/ingredients", status_code=303)

@app.post("/ingredients/update/{ingredient_id}")
async def update_ingredient(
    request: Request,
    ingredient_id: int,
    name: str = Form(...),
    calories_per_100g: float = Form(0),
    protein_per_100g: float = Form(0),
    fat_per_100g: float = Form(0),
    carbs_per_100g: float = Form(0),
    price_per_package: float = Form(0),
    package_weight: float = Form(1000),
    unit: str = Form("г"),
    category: str = Form(None),
    db: Session = Depends(get_db)
):
    """Обновление ингредиента"""
    ingredient_service = IngredientService(db)
    
    ingredient_service.update(
        ingredient_id=ingredient_id,
        name=name,
        calories_per_100g=calories_per_100g,
        protein_per_100g=protein_per_100g,
        fat_per_100g=fat_per_100g,
        carbs_per_100g=carbs_per_100g,
        price_per_package=price_per_package,
        package_weight=package_weight,
        unit=unit,
        category=category
    )
    
    return RedirectResponse(url="/ingredients", status_code=303)

@app.get("/recipes", response_class=HTMLResponse)
async def recipes(request: Request, db: Session = Depends(get_db)):
    """Страница рецептов"""
    recipe_service = RecipeService(db)
    ingredient_service = IngredientService(db)
    
    recipes = recipe_service.get_all()
    ingredients = ingredient_service.get_all()
    
    context = {
        "request": request,
        "recipes": recipes,
        "ingredients": ingredients,
        "active_page": "recipes"
    }
    
    return templates.TemplateResponse("recipes.html", context)

@app.post("/recipes/create")
async def create_recipe(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    servings: int = Form(1),
    prep_time: int = Form(None),
    cook_time: int = Form(None),
    category: str = Form(None),
    photo: UploadFile = File(None),
    ingredients_json: str = Form("[]"),
    db: Session = Depends(get_db)
):
    """Создание рецепта"""
    recipe_service = RecipeService(db)
    
    # Обработка фото
    photo_path = None
    if photo and photo.filename:
        photo_path = f"uploads/{photo.filename}"
        file_location = UPLOADS_DIR / photo.filename
        with open(file_location, "wb") as f:
            f.write(await photo.read())
    
    # Парсинг ингредиентов
    ingredients_data = json.loads(ingredients_json) if ingredients_json else []
    
    recipe_service.create(
        name=name,
        description=description,
        servings=servings,
        prep_time=prep_time,
        cook_time=cook_time,
        category=category,
        photo_path=photo_path,
        ingredients_data=ingredients_data
    )
    
    return RedirectResponse(url="/recipes", status_code=303)

@app.get("/recipes/{recipe_id}", response_class=HTMLResponse)
async def view_recipe(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    """Просмотр рецепта"""
    recipe_service = RecipeService(db)
    ingredient_service = IngredientService(db)
    
    recipe = recipe_service.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    
    ingredients = ingredient_service.get_all()
    
    context = {
        "request": request,
        "recipe": recipe,
        "ingredients": ingredients,
        "active_page": "recipes"
    }
    
    return templates.TemplateResponse("recipe_detail.html", context)

@app.get("/meal-planner", response_class=HTMLResponse)
async def meal_planner(request: Request, db: Session = Depends(get_db)):
    """Планировщик питания"""
    meal_plan_service = MealPlanService(db)
    recipe_service = RecipeService(db)
    
    # Получаем план на неделю
    week_plan = meal_plan_service.get_week_plan()
    recipes = recipe_service.get_all()
    
    context = {
        "request": request,
        "week_plan": week_plan,
        "recipes": recipes,
        "meal_types": [
            ('breakfast', '🌅 Завтрак'),
            ('second_breakfast', '☕ Второй завтрак'),
            ('lunch', '🍲 Обед'),
            ('snack', '🥜 Перекус'),
            ('dinner', '🌙 Ужин'),
            ('second_snack', '🍵 Второй перекус')
        ],
        "active_page": "meal-planner"
    }
    
    return templates.TemplateResponse("meal_planner.html", context)

@app.post("/meal-planner/add-recipe")
async def add_recipe_to_meal(
    request: Request,
    date_str: str = Form(...),
    meal_type: str = Form(...),
    recipe_id: int = Form(...),
    servings: float = Form(1),
    db: Session = Depends(get_db)
):
    """Добавить рецепт в план питания"""
    meal_plan_service = MealPlanService(db)
    
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    meal_plan = meal_plan_service.create_or_get_meal_plan(target_date, meal_type)
    meal_plan_service.add_recipe_to_meal(meal_plan.id, recipe_id, servings)
    
    return RedirectResponse(url="/meal-planner", status_code=303)

@app.post("/meal-planner/remove-recipe/{mp_recipe_id}")
async def remove_recipe_from_meal(
    request: Request,
    mp_recipe_id: int,
    db: Session = Depends(get_db)
):
    """Удалить рецепт из плана питания"""
    meal_plan_service = MealPlanService(db)
    meal_plan_service.remove_recipe_from_meal(mp_recipe_id)
    
    return RedirectResponse(url="/meal-planner", status_code=303)

@app.get("/shopping-list", response_class=HTMLResponse)
async def shopping_list(request: Request, db: Session = Depends(get_db)):
    """Список покупок"""
    shopping_list_service = ShoppingListService(db)
    shopping_list = shopping_list_service.generate_from_week_plan()
    
    total_cost = sum(item['cost'] for item in shopping_list)
    
    context = {
        "request": request,
        "shopping_list": shopping_list,
        "total_cost": total_cost,
        "active_page": "shopping-list"
    }
    
    return templates.TemplateResponse("shopping_list.html", context)

@app.get("/shopping-list/export")
async def export_shopping_list(db: Session = Depends(get_db)):
    """Экспорт списка покупок"""
    shopping_list_service = ShoppingListService(db)
    shopping_list = shopping_list_service.generate_from_week_plan()
    message = shopping_list_service.export_to_telegram(shopping_list)
    
    return {"message": message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
