import os
import sys
import shutil

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from typing import List, Optional
import uuid
import json

from database import get_db, init_db
from models import Ingredient, Recipe, RecipeIngredient, MealPlan, UserProfile, WeightLog, Supplement

app = FastAPI()

# Добавляем min/max функции в Jinja2 environment
from jinja2 import Environment, FileSystemLoader

# Настройка путей
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
templates.env.globals['min'] = min
templates.env.globals['max'] = max

# --- Helper Functions ---
def calculate_recipe_nutrition(recipe_id, db: Session):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        return {"cal": 0, "p": 0, "f": 0, "c": 0, "cost": 0, "servings": 1}
    
    total_cal = total_p = total_f = total_c = total_cost = 0
    
    for ri in recipe.ingredients:
        ing = ri.ingredient
        # Расчет стоимости за единицу веса
        if ing.package_weight and ing.package_weight > 0:
            unit_price = ing.price / ing.package_weight
        else:
            unit_price = 0
        cost = unit_price * ri.weight
        
        # Расчет КБЖУ (данные в ингредиентах на 100г)
        factor = ri.weight / 100.0
        total_cal += ing.calories * factor
        total_p += ing.protein * factor
        total_f += ing.fat * factor
        total_c += ing.carbs * factor
        total_cost += cost
        
    return {
        "cal": round(total_cal, 1), 
        "p": round(total_p, 1), 
        "f": round(total_f, 1), 
        "c": round(total_c, 1), 
        "cost": round(total_cost, 2), 
        "servings": recipe.servings
    }

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(target_calories=2000, target_protein=150, target_fat=70, target_carbs=200)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Получаем план на сегодня
    plans = db.query(MealPlan).filter(MealPlan.date == today).all()
    
    daily_stats = {"cal": 0, "p": 0, "f": 0, "c": 0, "cost": 0, "meals": []}
    
    meal_types = ["breakfast", "second_breakfast", "lunch", "snack", "dinner", "second_snack"]
    meal_titles = {
        "breakfast": "Завтрак", 
        "second_breakfast": "2-й завтрак", 
        "lunch": "Обед", 
        "snack": "Перекус", 
        "dinner": "Ужин", 
        "second_snack": "2-й перекус"
    }

    for m_type in meal_types:
        meal_items = [p for p in plans if p.meal_type == m_type]
        meal_total = {"cal": 0, "p": 0, "f": 0, "c": 0, "cost": 0, "food_items": [], "supplements": []}
        
        for item in meal_items:
            stats = calculate_recipe_nutrition(item.recipe_id, db)
            # Умножаем на кол-во порций в плане
            multiplier = item.servings_count
            meal_total["cal"] += stats["cal"] * multiplier
            meal_total["p"] += stats["p"] * multiplier
            meal_total["f"] += stats["f"] * multiplier
            meal_total["c"] += stats["c"] * multiplier
            meal_total["cost"] += stats["cost"] * multiplier
            
            meal_total["food_items"].append({
                "name": item.recipe.name,
                "servings": item.servings_count,
                "stats": stats
            })
            
        # Добавляем добавки для примера
        if m_type == "breakfast":
            meal_total["supplements"] = ["Витамин D3 (2000 ME)", "Омега-3"]
        elif m_type == "lunch":
            meal_total["supplements"] = ["Креатин (5г)"]

        daily_stats["cal"] += meal_total["cal"]
        daily_stats["p"] += meal_total["p"]
        daily_stats["f"] += meal_total["f"]
        daily_stats["c"] += meal_total["c"]
        daily_stats["cost"] += meal_total["cost"]
        
        daily_stats["meals"].append({"type": m_type, "title": meal_titles[m_type], **meal_total})

    context = {
        "request": request,
        "today": today,
        "profile": profile,
        "daily_stats": daily_stats,
        "targets": {
            "cal": profile.target_calories, 
            "p": profile.target_protein, 
            "f": profile.target_fat, 
            "c": profile.target_carbs
        },
        "active_page": "dashboard"
    }
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    logs = db.query(WeightLog).order_by(WeightLog.date.desc()).limit(10).all()
    
    context = {
        "request": request,
        "profile": profile,
        "logs": logs,
        "today": date.today(),
        "active_page": "profile"
    }
    return templates.TemplateResponse("profile.html", context)

@app.post("/profile/update")
async def update_profile(
    request: Request,
    weight: float = Form(...),
    waist: float = Form(None),
    chest: float = Form(None),
    bicep: float = Form(None),
    hips: float = Form(None),
    target_calories: int = Form(...),
    target_protein: float = Form(...),
    target_fat: float = Form(...),
    target_carbs: float = Form(...),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)
    
    profile.current_weight = weight
    profile.waist = waist if waist else None
    profile.chest = chest if chest else None
    profile.bicep = bicep if bicep else None
    profile.hips = hips if hips else None
    profile.target_calories = target_calories
    profile.target_protein = target_protein
    profile.target_fat = target_fat
    profile.target_carbs = target_carbs
    
    # Логируем вес
    log = WeightLog(date=date.today(), weight=weight, waist=waist, chest=chest, bicep=bicep)
    db.add(log)
    
    db.commit()
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/ingredients", response_class=HTMLResponse)
async def ingredients_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(Ingredient).all()
    context = {
        "request": request, 
        "ingredients": items,
        "active_page": "ingredients"
    }
    return templates.TemplateResponse("ingredients.html", context)

@app.post("/ingredients/add")
async def add_ingredient(
    name: str = Form(...),
    calories: float = Form(...),
    protein: float = Form(...),
    fat: float = Form(...),
    carbs: float = Form(...),
    price: float = Form(...),
    package_weight: float = Form(...),
    unit: str = Form("г"),
    db: Session = Depends(get_db)
):
    try:
        ing = Ingredient(
            name=name, 
            calories=calories, 
            protein=protein, 
            fat=fat, 
            carbs=carbs,
            price=price, 
            package_weight=package_weight, 
            unit=unit
        )
        db.add(ing)
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка сохранения")
    return RedirectResponse(url="/ingredients", status_code=303)

@app.get("/recipes", response_class=HTMLResponse)
async def recipes_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(Recipe).all()
    ingredients = db.query(Ingredient).all()
    
    recipes_data = []
    for r in items:
        stats = calculate_recipe_nutrition(r.id, db)
        recipes_data.append({"recipe": r, "stats": stats})
    
    # Преобразуем ингредиенты в JSON для JS
    ingredients_json = json.dumps([{"id": i.id, "name": i.name, "unit": i.unit} for i in ingredients])
        
    context = {
        "request": request, 
        "recipes": recipes_data,
        "ingredients": ingredients,
        "ingredients_json": ingredients_json,
        "active_page": "recipes"
    }
    return templates.TemplateResponse("recipes.html", context)

@app.post("/recipes/add")
async def add_recipe(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    servings: int = Form(1),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Обработка фото
        image_path = None
        if file and file.filename:
            ext = file.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            path = os.path.join(UPLOAD_DIR, filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_path = f"uploads/{filename}"
        
        recipe = Recipe(name=name, description=description, servings=servings, image_path=image_path)
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        # Обработка ингредиентов формы (динамические поля)
        form_data = await request.form()
        for key, value in form_data.items():
            if key.startswith("ing_id_"):
                idx = key.split("_")[-1]
                ing_id = value
                weight = form_data.get(f"weight_{idx}")
                if ing_id and weight and float(weight) > 0:
                    ri = RecipeIngredient(
                        recipe_id=recipe.id, 
                        ingredient_id=int(ing_id), 
                        weight=float(weight)
                    )
                    db.add(ri)
        
        db.commit()
    except Exception as e:
        print(f"Error creating recipe: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении рецепта")
    
    return RedirectResponse(url="/recipes", status_code=303)

@app.get("/meal-planner", response_class=HTMLResponse)
async def meal_planner(request: Request, db: Session = Depends(get_db)):
    # Получаем дату из query params или используем сегодня
    date_str = request.query_params.get("date", str(date.today()))
    try:
        current_date = date.fromisoformat(date_str)
    except:
        current_date = date.today()
    
    plans = db.query(MealPlan).filter(MealPlan.date == current_date).all()
    recipes = db.query(Recipe).all()
    
    # Группировка планов по типам еды
    meal_types = ["breakfast", "second_breakfast", "lunch", "snack", "dinner", "second_snack"]
    meal_titles = {
        "breakfast": "Завтрак", 
        "second_breakfast": "2-й завтрак", 
        "lunch": "Обед", 
        "snack": "Перекус", 
        "dinner": "Ужин", 
        "second_snack": "2-й перекус"
    }
    
    plans_by_meal = {}
    for m_type in meal_types:
        plans_by_meal[m_type] = [p for p in plans if p.meal_type == m_type]
    
    context = {
        "request": request, 
        "current_date": current_date,
        "recipes": recipes,
        "plans_by_meal": plans_by_meal,
        "meal_titles": meal_titles,
        "active_page": "planner"
    }
    return templates.TemplateResponse("meal_planner.html", context)

@app.post("/meal-planner/add")
async def add_meal_plan(
    date_str: str = Form(...),
    meal_type: str = Form(...),
    recipe_id: int = Form(...),
    servings_count: float = Form(1.0),
    db: Session = Depends(get_db)
):
    try:
        plan_date = date.fromisoformat(date_str)
        plan = MealPlan(
            date=plan_date,
            meal_type=meal_type,
            recipe_id=recipe_id,
            servings_count=servings_count
        )
        db.add(plan)
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка добавления в план")
    
    return RedirectResponse(url=f"/meal-planner?date={date_str}", status_code=303)

@app.post("/meal-planner/delete/{plan_id}")
async def delete_meal_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    if plan:
        date_str = str(plan.date)
        db.delete(plan)
        db.commit()
        return RedirectResponse(url=f"/meal-planner?date={date_str}", status_code=303)
    raise HTTPException(status_code=404, detail="План не найден")

@app.get("/shopping-list", response_class=HTMLResponse)
async def shopping_list(request: Request, db: Session = Depends(get_db)):
    # Генерация списка покупок на неделю
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    plans = db.query(MealPlan).filter(
        and_(MealPlan.date >= start_of_week, MealPlan.date <= end_of_week)
    ).all()
    
    shopping_map = {}
    
    for plan in plans:
        recipe = db.query(Recipe).get(plan.recipe_id)
        if not recipe:
            continue
        
        multiplier = plan.servings_count
        
        for ri in recipe.ingredients:
            ing = ri.ingredient
            needed_amount = ri.weight * multiplier
            
            if ing.id not in shopping_map:
                shopping_map[ing.id] = {
                    "name": ing.name, 
                    "amount": 0, 
                    "cost": 0, 
                    "unit": ing.unit
                }
            
            shopping_map[ing.id]["amount"] += needed_amount
            # Расчет стоимости пропорционально весу
            if ing.package_weight and ing.package_weight > 0:
                unit_price = ing.price / ing.package_weight
                shopping_map[ing.id]["cost"] += needed_amount * unit_price

    items = list(shopping_map.values())
    total_cost = sum(i["cost"] for i in items)
    
    context = {
        "request": request,
        "items": items,
        "total_cost": round(total_cost, 2),
        "week_start": start_of_week,
        "week_end": end_of_week,
        "active_page": "shopping"
    }
    return templates.TemplateResponse("shopping_list.html", context)

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8080)
