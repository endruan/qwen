"""
FastAPI REST API for Nutrition Planner.
Provides endpoints for integration with Telegram bot, Android app, or web frontend.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date, datetime
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_db
from services.core_services import (
    IngredientService,
    RecipeService,
    MealPlanService,
    ShoppingListService
)

# Create FastAPI app
app = FastAPI(
    title="Nutrition Planner API",
    description="API for meal planning, recipe management, and shopping list generation",
    version="1.0.0"
)

# Enable CORS for mobile app and web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = init_db()
    try:
        yield db
    finally:
        db.close()


# ==================== Pydantic Models ====================

class IngredientCreate(BaseModel):
    name: str
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    price_per_100g: float
    unit: Optional[str] = 'г'


class IngredientResponse(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    price_per_100g: float
    unit: str
    
    class Config:
        from_attributes = True


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = ''
    instructions: Optional[str] = ''
    prep_time_minutes: Optional[int] = 0
    servings: Optional[int] = 1


class RecipeIngredientAdd(BaseModel):
    ingredient_id: int
    quantity_grams: float


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    instructions: Optional[str]
    prep_time_minutes: int
    servings: int
    
    class Config:
        from_attributes = True


class MealPlanAdd(BaseModel):
    recipe_id: int
    meal_type: str


class MealPlanResponse(BaseModel):
    id: int
    date: date
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class ShoppingListItemResponse(BaseModel):
    ingredient_id: int
    name: str
    quantity_needed: float
    unit: str
    estimated_price: float
    is_purchased: bool
    
    class Config:
        from_attributes = True


# ==================== Ingredient Endpoints ====================

@app.post("/ingredients/", response_model=IngredientResponse)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    """Create a new ingredient."""
    service = IngredientService(db)
    return service.create_ingredient(
        name=ingredient.name,
        calories=ingredient.calories,
        protein=ingredient.protein,
        fat=ingredient.fat,
        carbohydrates=ingredient.carbohydrates,
        price_per_100g=ingredient.price_per_100g,
        unit=ingredient.unit
    )


@app.get("/ingredients/", response_model=List[IngredientResponse])
def get_all_ingredients(db: Session = Depends(get_db)):
    """Get all ingredients."""
    service = IngredientService(db)
    return service.get_all_ingredients()


@app.get("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Get ingredient by ID."""
    service = IngredientService(db)
    ingredient = service.get_ingredient_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@app.get("/ingredients/search/", response_model=List[IngredientResponse])
def search_ingredients(q: str, db: Session = Depends(get_db)):
    """Search ingredients by name."""
    service = IngredientService(db)
    return service.search_ingredients(q)


# ==================== Recipe Endpoints ====================

@app.post("/recipes/", response_model=RecipeResponse)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    """Create a new recipe."""
    service = RecipeService(db)
    return service.create_recipe(
        name=recipe.name,
        description=recipe.description,
        instructions=recipe.instructions,
        prep_time_minutes=recipe.prep_time_minutes,
        servings=recipe.servings
    )


@app.post("/recipes/{recipe_id}/ingredients/")
def add_ingredient_to_recipe(
    recipe_id: int,
    ingredient_data: RecipeIngredientAdd,
    db: Session = Depends(get_db)
):
    """Add an ingredient to a recipe."""
    service = RecipeService(db)
    success = service.add_ingredient_to_recipe(
        recipe_id=recipe_id,
        ingredient_id=ingredient_data.ingredient_id,
        quantity_grams=ingredient_data.quantity_grams
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add ingredient")
    return {"status": "success"}


@app.get("/recipes/", response_model=List[RecipeResponse])
def get_all_recipes(db: Session = Depends(get_db)):
    """Get all recipes."""
    service = RecipeService(db)
    return service.get_all_recipes()


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get recipe by ID with nutrition info."""
    service = RecipeService(db)
    recipe = service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    nutrition = service.calculate_recipe_nutrition(recipe_id)
    
    return {
        "recipe": recipe,
        "nutrition": nutrition
    }


@app.get("/recipes/search/", response_model=List[RecipeResponse])
def search_recipes(q: str, db: Session = Depends(get_db)):
    """Search recipes by name."""
    service = RecipeService(db)
    return service.search_recipes(q)


# ==================== Meal Plan Endpoints ====================

@app.post("/meal-plans/{plan_date}/")
def add_recipe_to_meal(
    plan_date: date,
    meal_data: MealPlanAdd,
    db: Session = Depends(get_db)
):
    """Add a recipe to a specific meal on a given date."""
    service = MealPlanService(db)
    try:
        success = service.add_recipe_to_meal(
            plan_date=plan_date,
            recipe_id=meal_data.recipe_id,
            meal_type=meal_data.meal_type
        )
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/meal-plans/{plan_date}/")
def get_daily_meal_plan(plan_date: date, db: Session = Depends(get_db)):
    """Get meal plan for a specific date with meals grouped by type."""
    service = MealPlanService(db)
    meals = service.get_meals_by_type(plan_date)
    nutrition = service.calculate_daily_nutrition(plan_date)
    
    return {
        "date": plan_date,
        "meals": meals,
        "nutrition": nutrition
    }


@app.get("/meal-plans/week/{start_date}")
def get_weekly_meal_plan(start_date: date, db: Session = Depends(get_db)):
    """Get meal plans for a week starting from start_date."""
    service = MealPlanService(db)
    weekly_plans = service.get_weekly_meal_plan(start_date)
    
    result = {}
    for plan_date, plan in weekly_plans.items():
        nutrition = service.calculate_daily_nutrition(plan_date)
        result[str(plan_date)] = {
            "meals": service.get_meals_by_type(plan_date),
            "nutrition": nutrition
        }
    
    return result


@app.get("/meal-plans/month/{year}/{month}")
def get_monthly_meal_plan(year: int, month: int, db: Session = Depends(get_db)):
    """Get meal plans for a specific month."""
    service = MealPlanService(db)
    monthly_plans = service.get_monthly_meal_plan(year, month)
    
    result = {}
    for plan_date, plan in monthly_plans.items():
        nutrition = service.calculate_daily_nutrition(plan_date)
        result[str(plan_date)] = {
            "meals": service.get_meals_by_type(plan_date),
            "nutrition": nutrition
        }
    
    return result


@app.delete("/meal-plans/{plan_date}/{meal_type}/{recipe_id}")
def remove_recipe_from_meal(
    plan_date: date,
    meal_type: str,
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """Remove a recipe from a specific meal."""
    service = MealPlanService(db)
    success = service.remove_recipe_from_meal(plan_date, recipe_id, meal_type)
    if not success:
        raise HTTPException(status_code=404, detail="Meal plan or recipe not found")
    return {"status": "success"}


# ==================== Shopping List Endpoints ====================

@app.get("/shopping-list/generate/{start_date}")
def generate_shopping_list(start_date: date, db: Session = Depends(get_db)):
    """Generate shopping list from weekly meal plan."""
    service = ShoppingListService(db)
    shopping_list = service.generate_shopping_list_from_week(start_date)
    return {"shopping_list": shopping_list}


@app.post("/shopping-list/save/")
def save_shopping_list(
    start_date: date,
    db: Session = Depends(get_db)
):
    """Generate and save shopping list to database."""
    gen_service = ShoppingListService(db)
    shopping_list = gen_service.generate_shopping_list_from_week(start_date)
    saved_items = gen_service.save_shopping_list(shopping_list)
    
    return {
        "status": "success",
        "items_count": len(saved_items)
    }


@app.get("/shopping-list/recent/")
def get_recent_shopping_list(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent shopping list items."""
    service = ShoppingListService(db)
    items = service.get_recent_shopping_list(limit)
    
    return {
        "items": [
            {
                "id": item.id,
                "ingredient_name": item.ingredient.name,
                "quantity_needed": item.quantity_needed,
                "unit": item.ingredient.unit,
                "estimated_price": item.estimated_price,
                "is_purchased": bool(item.is_purchased),
                "created_date": str(item.created_date)
            }
            for item in items
        ]
    }


@app.post("/shopping-list/{item_id}/purchase/")
def mark_as_purchased(item_id: int, db: Session = Depends(get_db)):
    """Mark a shopping list item as purchased."""
    service = ShoppingListService(db)
    success = service.mark_as_purchased(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    return {"status": "success"}


# ==================== Health Check ====================

@app.get("/")
def root():
    """Root endpoint - health check."""
    return {
        "message": "Nutrition Planner API is running",
        "version": "1.0.0",
        "endpoints": {
            "ingredients": "/ingredients/",
            "recipes": "/recipes/",
            "meal_plans": "/meal-plans/{date}/",
            "shopping_list": "/shopping-list/"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
