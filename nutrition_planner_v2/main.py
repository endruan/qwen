# main.py - Основной сервер приложения
from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, extract
from datetime import datetime, date, timedelta
from typing import List, Optional
import json
import os
from pathlib import Path

from models import (
    Ingredient, Recipe, RecipeIngredient, MealPlan, MealPlanItem, 
    UserProfile, BodyMeasurement, WeightLog, Supplement,
    init_db, get_db, engine, Base
)

app = FastAPI(title="Nutrition Planner")

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"
UPLOAD_DIR = BASE_DIR / "uploads"

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR / "uploads", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize database
init_db()

# ==================== USER PROFILE ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile(
            current_weight=80, target_weight=75, height=180, age=30,
            gender="male", activity_level="moderate",
            target_calories=2200, target_protein=160, target_fat=75, target_carbs=220
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Get weight history for chart
    weight_logs = db.query(WeightLog).order_by(WeightLog.date).all()
    weight_data = [{"date": str(log.date), "weight": log.weight} for log in weight_logs]
    
    # Get measurements
    measurements = db.query(BodyMeasurement).order_by(BodyMeasurement.date.desc()).first()
    
    today = date.today()
    plan = db.query(MealPlan).filter(MealPlan.date == today).options(
        joinedload(MealPlan.items).joinedload(MealPlanItem.recipe)
    ).first()
    
    daily_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "cost": 0}
    if plan:
        for item in plan.items:
            daily_totals["calories"] += item.recipe.total_calories * item.servings_count
            daily_totals["protein"] += item.recipe.total_protein * item.servings_count
            daily_totals["fat"] += item.recipe.total_fat * item.servings_count
            daily_totals["carbs"] += item.recipe.total_carbs * item.servings_count
            daily_totals["cost"] += item.recipe.total_cost * item.servings_count
    
    # BMI calculation
    bmi = 0
    if profile.height > 0:
        bmi = profile.current_weight / ((profile.height / 100) ** 2)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "profile": profile,
        "daily_totals": daily_totals,
        "weight_data": json.dumps(weight_data),
        "measurements": measurements,
        "bmi": round(bmi, 1),
        "today": today,
        "active_page": "dashboard"
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    measurements = db.query(BodyMeasurement).order_by(BodyMeasurement.date.desc()).limit(10).all()
    weight_logs = db.query(WeightLog).order_by(WeightLog.date.desc()).limit(30).all()
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": profile,
        "measurements": measurements,
        "weight_logs": weight_logs,
        "active_page": "profile"
    })

@app.post("/api/profile/update")
async def update_profile(
    current_weight: float = Form(0),
    target_weight: float = Form(0),
    height: int = Form(0),
    age: int = Form(30),
    gender: str = Form("male"),
    activity_level: str = Form("moderate"),
    target_calories: int = Form(2000),
    target_protein: float = Form(150),
    target_fat: float = Form(70),
    target_carbs: float = Form(200),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).first()
    if not profile:
        profile = UserProfile()
        db.add(profile)
    
    profile.current_weight = current_weight
    profile.target_weight = target_weight
    profile.height = height
    profile.age = age
    profile.gender = gender
    profile.activity_level = activity_level
    profile.target_calories = target_calories
    profile.target_protein = target_protein
    profile.target_fat = target_fat
    profile.target_carbs = target_carbs
    
    db.commit()
    return {"status": "success"}

@app.post("/api/weight/add")
async def add_weight(
    weight: float = Form(0),
    date_str: str = Form(None),
    db: Session = Depends(get_db)
):
    log_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    log = WeightLog(user_id=1, date=log_date, weight=weight)
    db.add(log)
    
    # Update current weight in profile
    profile = db.query(UserProfile).first()
    if profile:
        profile.current_weight = weight
    
    db.commit()
    return {"status": "success"}

@app.post("/api/measurements/add")
async def add_measurements(
    chest: float = Form(0),
    waist: float = Form(0),
    hips: float = Form(0),
    bicep: float = Form(0),
    thigh: float = Form(0),
    date_str: str = Form(None),
    db: Session = Depends(get_db)
):
    log_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    measurement = BodyMeasurement(
        user_id=1, date=log_date,
        chest=chest, waist=waist, hips=hips, bicep=bicep, thigh=thigh
    )
    db.add(measurement)
    db.commit()
    return {"status": "success"}

# ==================== INGREDIENTS ====================

@app.get("/ingredients", response_class=HTMLResponse)
async def ingredients_page(request: Request, db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).all()
    return templates.TemplateResponse("ingredients.html", {
        "request": request,
        "ingredients": ingredients,
        "active_page": "ingredients"
    })

@app.post("/api/ingredients/add")
async def add_ingredient(
    name: str = Form(...),
    calories: float = Form(0),
    protein: float = Form(0),
    fat: float = Form(0),
    carbs: float = Form(0),
    price_per_unit: float = Form(0),
    package_size: float = Form(100),
    unit_type: str = Form("г"),
    db: Session = Depends(get_db)
):
    try:
        ingredient = Ingredient(
            name=name,
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            price_per_unit=price_per_unit,
            package_size=package_size,
            unit_type=unit_type
        )
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        return {"status": "success", "id": ingredient.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ingredients/update/{ingredient_id}")
async def update_ingredient(
    ingredient_id: int,
    name: str = Form(...),
    calories: float = Form(0),
    protein: float = Form(0),
    fat: float = Form(0),
    carbs: float = Form(0),
    price_per_unit: float = Form(0),
    package_size: float = Form(100),
    unit_type: str = Form("г"),
    db: Session = Depends(get_db)
):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    ingredient.name = name
    ingredient.calories = calories
    ingredient.protein = protein
    ingredient.fat = fat
    ingredient.carbs = carbs
    ingredient.price_per_unit = price_per_unit
    ingredient.package_size = package_size
    ingredient.unit_type = unit_type
    
    db.commit()
    return {"status": "success"}

@app.delete("/api/ingredients/delete/{ingredient_id}")
async def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(ingredient)
    db.commit()
    return {"status": "success"}

@app.get("/api/ingredients")
async def get_ingredients(db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "calories": i.calories,
            "protein": i.protein,
            "fat": i.fat,
            "carbs": i.carbs,
            "price_per_unit": i.price_per_unit,
            "package_size": i.package_size,
            "unit_type": i.unit_type,
            "price_per_100g": (i.price_per_unit / i.package_size * 100) if i.package_size > 0 else 0
        }
        for i in ingredients
    ]

# ==================== RECIPES ====================

@app.get("/recipes", response_class=HTMLResponse)
async def recipes_page(request: Request, db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    return templates.TemplateResponse("recipes.html", {
        "request": request,
        "recipes": recipes,
        "active_page": "recipes"
    })

@app.get("/api/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    ingredients = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).options(joinedload(RecipeIngredient.ingredient)).all()
    
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "image_url": recipe.image_url,
        "servings": recipe.servings,
        "total_calories": recipe.total_calories,
        "total_protein": recipe.total_protein,
        "total_fat": recipe.total_fat,
        "total_carbs": recipe.total_carbs,
        "total_cost": recipe.total_cost,
        "ingredients": [
            {
                "id": ri.ingredient.id,
                "name": ri.ingredient.name,
                "quantity": ri.quantity,
                "calories": ri.ingredient.calories,
                "protein": ri.ingredient.protein,
                "fat": ri.ingredient.fat,
                "carbs": ri.ingredient.carbs
            }
            for ri in ingredients
        ]
    }

@app.post("/api/recipes/create")
async def create_recipe(
    name: str = Form(...),
    description: str = Form(""),
    instructions: str = Form(""),
    servings: int = Form(1),
    image_url: str = Form(None),
    ingredients_json: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        ingredients_data = json.loads(ingredients_json)
        
        # Calculate totals
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_cost = 0
        
        for ing in ingredients_data:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ing["id"]).first()
            if ingredient:
                qty = ing["quantity"]
                # Calculate per 100g/ml basis
                factor = qty / 100
                
                total_calories += ingredient.calories * factor
                total_protein += ingredient.protein * factor
                total_fat += ingredient.fat * factor
                total_carbs += ingredient.carbs * factor
                
                # Calculate cost
                if ingredient.package_size > 0:
                    price_per_g = ingredient.price_per_unit / ingredient.package_size
                    total_cost += price_per_g * qty
        
        recipe = Recipe(
            name=name,
            description=description,
            instructions=instructions,
            image_url=image_url,
            servings=servings,
            total_calories=total_calories,
            total_protein=total_protein,
            total_fat=total_fat,
            total_carbs=total_carbs,
            total_cost=total_cost
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        
        # Add ingredients
        for ing in ingredients_data:
            recipe_ing = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing["id"],
                quantity=ing["quantity"]
            )
            db.add(recipe_ing)
        
        db.commit()
        return {"status": "success", "id": recipe.id}
    except Exception as e:
        db.rollback()
        print(f"Error creating recipe: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/recipes/update/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    name: str = Form(...),
    description: str = Form(""),
    instructions: str = Form(""),
    servings: int = Form(1),
    image_url: str = Form(None),
    ingredients_json: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        ingredients_data = json.loads(ingredients_json)
        
        # Delete old ingredients
        db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id).delete()
        
        # Calculate totals
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_cost = 0
        
        for ing in ingredients_data:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ing["id"]).first()
            if ingredient:
                qty = ing["quantity"]
                factor = qty / 100
                
                total_calories += ingredient.calories * factor
                total_protein += ingredient.protein * factor
                total_fat += ingredient.fat * factor
                total_carbs += ingredient.carbs * factor
                
                if ingredient.package_size > 0:
                    price_per_g = ingredient.price_per_unit / ingredient.package_size
                    total_cost += price_per_g * qty
            
            recipe_ing = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing["id"],
                quantity=ing["quantity"]
            )
            db.add(recipe_ing)
        
        recipe.name = name
        recipe.description = description
        recipe.instructions = instructions
        recipe.servings = servings
        recipe.image_url = image_url
        recipe.total_calories = total_calories
        recipe.total_protein = total_protein
        recipe.total_fat = total_fat
        recipe.total_carbs = total_carbs
        recipe.total_cost = total_cost
        
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        print(f"Error updating recipe: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/recipes/delete/{recipe_id}")
async def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.commit()
    return {"status": "success"}

@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return {"status": "success", "url": f"/uploads/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MEAL PLANNER ====================

@app.get("/meal-planner", response_class=HTMLResponse)
async def meal_planner_page(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    
    # Get or create plans for the week
    week_plans = []
    for i in range(7):
        day_date = today + timedelta(days=i)
        plan = db.query(MealPlan).filter(MealPlan.date == day_date).options(
            joinedload(MealPlan.items).joinedload(MealPlanItem.recipe)
        ).first()
        
        if not plan:
            plan = MealPlan(date=day_date)
            db.add(plan)
            db.commit()
            db.refresh(plan)
        
        day_data = {
            "date": day_date,
            "plan": plan,
            "items": plan.items,
            "totals": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "cost": 0}
        }
        
        for item in plan.items:
            day_data["totals"]["calories"] += item.recipe.total_calories * item.servings_count
            day_data["totals"]["protein"] += item.recipe.total_protein * item.servings_count
            day_data["totals"]["fat"] += item.recipe.total_fat * item.servings_count
            day_data["totals"]["carbs"] += item.recipe.total_carbs * item.servings_count
            day_data["totals"]["cost"] += item.recipe.total_cost * item.servings_count
        
        week_plans.append(day_data)
    
    recipes = db.query(Recipe).all()
    
    return templates.TemplateResponse("meal_planner.html", {
        "request": request,
        "week_plans": week_plans,
        "recipes": recipes,
        "today": today,
        "active_page": "meal-planner"
    })

@app.post("/api/meal-plan/add")
async def add_meal_plan_item(
    date_str: str = Form(...),
    recipe_id: int = Form(...),
    meal_type: str = Form(...),
    servings_count: float = Form(1.0),
    db: Session = Depends(get_db)
):
    try:
        plan_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        plan = db.query(MealPlan).filter(MealPlan.date == plan_date).first()
        if not plan:
            plan = MealPlan(date=plan_date)
            db.add(plan)
            db.commit()
            db.refresh(plan)
        
        item = MealPlanItem(
            plan_id=plan.id,
            recipe_id=recipe_id,
            meal_type=meal_type,
            servings_count=servings_count
        )
        db.add(item)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/meal-plan/remove/{item_id}")
async def remove_meal_plan_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MealPlanItem).filter(MealPlanItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "success"}

# ==================== SHOPPING LIST ====================

@app.get("/shopping-list", response_class=HTMLResponse)
async def shopping_list_page(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=7)
    
    plans = db.query(MealPlan).filter(
        and_(MealPlan.date >= today, MealPlan.date <= end_date)
    ).options(
        joinedload(MealPlan.items).joinedload(MealPlanItem.recipe).joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
    ).all()
    
    shopping_dict = {}
    for plan in plans:
        for item in plan.items:
            for recipe_ing in item.recipe.ingredients:
                ing = recipe_ing.ingredient
                qty_needed = recipe_ing.quantity * item.servings_count
                
                if ing.id not in shopping_dict:
                    shopping_dict[ing.id] = {
                        "name": ing.name,
                        "quantity": 0,
                        "unit_type": ing.unit_type,
                        "estimated_cost": 0
                    }
                
                shopping_dict[ing.id]["quantity"] += qty_needed
                if ing.package_size > 0:
                    shopping_dict[ing.id]["estimated_cost"] += (ing.price_per_unit / ing.package_size) * qty_needed
    
    shopping_list = list(shopping_dict.values())
    total_cost = sum(item["estimated_cost"] for item in shopping_list)
    
    return templates.TemplateResponse("shopping_list.html", {
        "request": request,
        "shopping_list": shopping_list,
        "total_cost": total_cost,
        "active_page": "shopping-list"
    })

@app.get("/api/shopping-list/export")
async def export_shopping_list(db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=7)
    
    plans = db.query(MealPlan).filter(
        and_(MealPlan.date >= today, MealPlan.date <= end_date)
    ).options(
        joinedload(MealPlan.items).joinedload(MealPlanItem.recipe).joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
    ).all()
    
    shopping_dict = {}
    for plan in plans:
        for item in plan.items:
            for recipe_ing in item.recipe.ingredients:
                ing = recipe_ing.ingredient
                qty_needed = recipe_ing.quantity * item.servings_count
                
                if ing.id not in shopping_dict:
                    shopping_dict[ing.id] = {
                        "name": ing.name,
                        "quantity": 0,
                        "unit_type": ing.unit_type
                    }
                
                shopping_dict[ing.id]["quantity"] += qty_needed
    
    text_lines = ["🛒 Список покупок на неделю:\n"]
    for item in shopping_dict.values():
        text_lines.append(f"- {item['name']}: {item['quantity']:.0f} {item['unit_type']}")
    
    return {"text": "\n".join(text_lines)}

# ==================== SUPPLEMENTS ====================

@app.get("/supplements", response_class=HTMLResponse)
async def supplements_page(request: Request, db: Session = Depends(get_db)):
    supplements = db.query(Supplement).all()
    return templates.TemplateResponse("supplements.html", {
        "request": request,
        "supplements": supplements,
        "active_page": "supplements"
    })

@app.post("/api/supplements/add")
async def add_supplement(
    name: str = Form(...),
    dosage: str = Form(""),
    timing: str = Form(""),
    db: Session = Depends(get_db)
):
    supplement = Supplement(name=name, dosage=dosage, timing=timing)
    db.add(supplement)
    db.commit()
    return {"status": "success"}

@app.delete("/api/supplements/delete/{supp_id}")
async def delete_supplement(supp_id: int, db: Session = Depends(get_db)):
    supplement = db.query(Supplement).filter(Supplement.id == supp_id).first()
    if not supplement:
        raise HTTPException(status_code=404, detail="Supplement not found")
    db.delete(supplement)
    db.commit()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
