from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..db.database import get_db
from ..schemas.schemas import (
    IngredientCreate, IngredientUpdate, IngredientResponse,
    RecipeCreate, RecipeUpdate, RecipeResponse,
    MealPlanCreate, MealPlanResponse,
    ShoppingListItemResponse
)
from ..services.services import (
    get_ingredients, get_ingredient, create_ingredient, update_ingredient, delete_ingredient,
    get_recipes, get_recipe, create_recipe, update_recipe, delete_recipe,
    get_meal_plans, create_meal_plan, delete_meal_plan,
    generate_shopping_list, get_shopping_list, toggle_shopping_item,
    calculate_daily_nutrition, calculate_user_goals
)
from ..core.deps import get_current_user
from ..models.models import User

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


# Ingredients endpoints
@router.get("/ingredients", response_model=List[IngredientResponse])
def list_ingredients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all ingredients"""
    return get_ingredients(db, skip, limit)


@router.post("/ingredients", response_model=IngredientResponse)
def create_ingredient_endpoint(
    ingredient: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new ingredient"""
    return create_ingredient(db, ingredient)


@router.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient_endpoint(
    ingredient_id: int,
    ingredient_update: IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an ingredient"""
    updated = update_ingredient(db, ingredient_id, ingredient_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return updated


@router.delete("/ingredients/{ingredient_id}")
def delete_ingredient_endpoint(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an ingredient"""
    try:
        success = delete_ingredient(db, ingredient_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        return {"message": "Ingredient deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Recipes endpoints
@router.get("/recipes", response_model=List[RecipeResponse])
def list_recipes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recipes"""
    return get_recipes(db, skip, limit)


@router.post("/recipes", response_model=RecipeResponse)
def create_recipe_endpoint(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recipe with ingredients"""
    try:
        return create_recipe(db, recipe, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recipe by ID - FIXED to properly load ingredients"""
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe_endpoint(
    recipe_id: int,
    recipe_update: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a recipe"""
    updated = update_recipe(db, recipe_id, recipe_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated


@router.delete("/recipes/{recipe_id}")
def delete_recipe_endpoint(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recipe"""
    success = delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted successfully"}


# Meal Plans endpoints
@router.get("/meal-plans", response_model=List[MealPlanResponse])
def list_meal_plans(
    start_date: date = Query(default_factory=date.today),
    end_date: date = Query(default=lambda: date.today()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meal plans for a date range"""
    return get_meal_plans(db, current_user.id, start_date, end_date)


@router.post("/meal-plans", response_model=MealPlanResponse)
def create_meal_plan_endpoint(
    meal_plan: MealPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a meal to the meal plan"""
    return create_meal_plan(db, meal_plan, current_user.id)


@router.delete("/meal-plans/{meal_plan_id}")
def delete_meal_plan_endpoint(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a meal from the meal plan"""
    success = delete_meal_plan(db, meal_plan_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return {"message": "Meal plan deleted successfully"}


# Shopping List endpoints
@router.get("/shopping-list", response_model=List[ShoppingListItemResponse])
def get_shopping_list_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current shopping list"""
    return get_shopping_list(db, current_user.id)


@router.post("/shopping-list/generate", response_model=List[ShoppingListItemResponse])
def generate_shopping_list_endpoint(
    start_date: date = Query(default_factory=date.today),
    end_date: date = Query(default=lambda: date.today() + timedelta(days=7)),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate shopping list from meal plans"""
    return generate_shopping_list(db, current_user.id, start_date, end_date)


@router.put("/shopping-list/{item_id}/toggle", response_model=ShoppingListItemResponse)
def toggle_shopping_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark shopping list item as purchased/not purchased"""
    item = toggle_shopping_item(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")
    return item


# Dashboard nutrition
@router.get("/dashboard/nutrition")
def get_daily_nutrition(
    target_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily nutrition summary"""
    nutrition = calculate_daily_nutrition(db, current_user.id, target_date)
    goals = calculate_user_goals(current_user)
    
    return {
        **nutrition,
        'goals': goals
    }
