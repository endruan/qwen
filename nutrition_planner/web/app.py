"""
Web frontend for Nutrition Planner using FastAPI with Jinja2 templates.
Provides a modern, responsive web interface for meal planning.
"""

from fastapi import FastAPI, Request, Query, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date, timedelta
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

# Create FastAPI app for web frontend
app = FastAPI(title="Nutrition Planner Web")

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Setup templates
templates_path = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=templates_path)

# Dependency to get database session
def get_db():
    db = init_db()
    try:
        yield db
    finally:
        db.close()


# Meal type names and icons
MEAL_NAMES = {
    'breakfast': 'Завтрак',
    'second_breakfast': 'Второй завтрак',
    'lunch': 'Обед',
    'snack': 'Перекус',
    'dinner': 'Ужин',
    'second_snack': 'Второй перекус'
}

MEAL_ICONS = {
    'breakfast': '🍳',
    'second_breakfast': '🥐',
    'lunch': '🍲',
    'snack': '🍎',
    'dinner': '🍽️',
    'second_snack': '🥛'
}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page."""
    today = date.today()
    
    # Get statistics
    ingredient_service = IngredientService(db)
    recipe_service = RecipeService(db)
    meal_plan_service = MealPlanService(db)
    
    all_ingredients = ingredient_service.get_all_ingredients()
    all_recipes = recipe_service.get_all_recipes()
    
    # Get weekly meal plans
    week_start = today - timedelta(days=today.weekday())
    weekly_plans = meal_plan_service.get_weekly_meal_plan(week_start)
    
    # Calculate stats
    stats = {
        'total_recipes': len(all_recipes),
        'total_ingredients': len(all_ingredients),
        'planned_days': len(weekly_plans),
        'week_cost': 0.0
    }
    
    # Calculate week cost
    for plan_date in weekly_plans.keys():
        nutrition = meal_plan_service.calculate_daily_nutrition(plan_date)
        stats['week_cost'] += nutrition['daily_total']['price']
    
    # Prepare week days for calendar
    week_days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        plan = weekly_plans.get(day_date)
        meals = meal_plan_service.get_meals_by_type(day_date) if plan else {}
        meal_count = sum(len(m) for m in meals.values())
        
        week_days.append({
            'date': str(day_date),
            'day_num': day_date.day,
            'is_today': day_date == today,
            'has_plan': meal_count > 0,
            'meal_count': meal_count
        })
    
    # Get today's meals
    today_meals = meal_plan_service.get_meals_by_type(today)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "week_days": week_days,
        "today_date": today.strftime("%d.%m.%Y"),
        "today_meals": today_meals,
        "meal_names": MEAL_NAMES,
        "meal_icons": MEAL_ICONS,
        "active_page": "dashboard"
    })


@app.get("/ingredients", response_class=HTMLResponse)
async def ingredients_page(request: Request, db: Session = Depends(get_db)):
    """Ingredients management page."""
    ingredient_service = IngredientService(db)
    ingredients = ingredient_service.get_all_ingredients()
    
    return templates.TemplateResponse("ingredients.html", {
        "request": request,
        "ingredients": ingredients,
        "active_page": "ingredients"
    })


@app.get("/recipes", response_class=HTMLResponse)
async def recipes_page(request: Request, db: Session = Depends(get_db)):
    """Recipes management page."""
    recipe_service = RecipeService(db)
    ingredient_service = IngredientService(db)
    
    recipes = recipe_service.get_all_recipes()
    all_ingredients = ingredient_service.get_all_ingredients()
    
    # Calculate nutrition for each recipe
    recipe_nutrition = {}
    for recipe in recipes:
        recipe_nutrition[recipe.id] = recipe_service.calculate_recipe_nutrition(recipe.id)
    
    return templates.TemplateResponse("recipes.html", {
        "request": request,
        "recipes": recipes,
        "all_ingredients": all_ingredients,
        "recipe_nutrition": recipe_nutrition,
        "active_page": "recipes"
    })


@app.get("/meal-planner", response_class=HTMLResponse)
async def meal_planner_page(
    request: Request,
    date_param: str = Query(default=None),
    db: Session = Depends(get_db)
):
    """Meal planner page."""
    meal_plan_service = MealPlanService(db)
    recipe_service = RecipeService(db)
    
    # Determine selected date
    if date_param:
        selected_date = date.fromisoformat(date_param)
    else:
        selected_date = date.today()
    
    # Get week start (Monday)
    week_start = selected_date - timedelta(days=selected_date.weekday())
    
    # Prepare week days
    week_days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        week_days.append({
            'date': str(day_date),
            'day_num': day_date.day,
            'day_name': day_date.strftime("%a"),
            'is_today': day_date == date.today(),
            'is_selected': day_date == selected_date
        })
    
    # Get meals for selected date
    meals_by_type = meal_plan_service.get_meals_by_type(selected_date)
    daily_nutrition = meal_plan_service.calculate_daily_nutrition(selected_date)
    
    # Calculate meal totals
    meal_totals = daily_nutrition.get('by_meal', {})
    
    # Get all recipes for the modal
    all_recipes = recipe_service.get_all_recipes()
    
    return templates.TemplateResponse("meal_planner.html", {
        "request": request,
        "selected_date": selected_date.strftime("%d.%m.%Y"),
        "week_days": week_days,
        "meals_by_type": meals_by_type,
        "daily_nutrition": daily_nutrition,
        "meal_totals": meal_totals,
        "all_recipes": all_recipes,
        "meal_names": MEAL_NAMES,
        "meal_icons": MEAL_ICONS,
        "active_page": "meal-planner"
    })


@app.get("/shopping-list", response_class=HTMLResponse)
async def shopping_list_page(
    request: Request,
    date_param: str = Query(default=None),
    db: Session = Depends(get_db)
):
    """Shopping list page."""
    shopping_service = ShoppingListService(db)
    meal_plan_service = MealPlanService(db)
    
    # Determine week start
    if date_param:
        week_start = date.fromisoformat(date_param)
    else:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=6)
    
    # Generate shopping list
    shopping_list_data = shopping_service.generate_shopping_list_from_week(week_start)
    
    # Get recent saved items
    saved_items = shopping_service.get_recent_shopping_list(100)
    
    # Process shopping list
    shopping_list = []
    total_price = 0.0
    
    for item in shopping_list_data:
        shopping_list.append({
            'id': item.get('ingredient_id'),
            'name': item.get('name'),
            'quantity_needed': item.get('quantity_needed', 0),
            'unit': item.get('unit', 'г'),
            'estimated_price': item.get('price', 0),
            'is_purchased': False
        })
        total_price += item.get('price', 0)
    
    # Count purchased items from saved list
    purchased_count = sum(1 for item in saved_items if item.is_purchased)
    
    # Group items by category (simple grouping by first letter for now)
    grouped_items = {}
    for item in shopping_list:
        first_letter = item['name'][0].upper()
        if first_letter not in grouped_items:
            grouped_items[first_letter] = []
        grouped_items[first_letter].append({
            'name': item['name'],
            'quantity': item['quantity_needed'],
            'unit': item['unit']
        })
    
    return templates.TemplateResponse("shopping_list.html", {
        "request": request,
        "shopping_list": shopping_list,
        "week_start": week_start.strftime("%d.%m.%Y"),
        "week_end": week_end.strftime("%d.%m.%Y"),
        "total_price": total_price,
        "purchased_count": purchased_count,
        "grouped_items": grouped_items,
        "active_page": "shopping-list"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
