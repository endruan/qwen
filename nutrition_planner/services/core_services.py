"""
Service layer for business logic operations.
Handles ingredient management, recipe management, meal planning, and shopping list generation.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from models.database import Ingredient, Recipe, MealPlan, ShoppingListItem, recipe_ingredients_assoc as recipe_ingredients, meal_plan_recipes, recipe_ingredients_assoc


class IngredientService:
    """Service for managing ingredients."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_ingredient(self, name: str, calories: float, protein: float, 
                         fat: float, carbohydrates: float, price_per_100g: float,
                         unit: str = 'г') -> Ingredient:
        """Create a new ingredient."""
        ingredient = Ingredient(
            name=name,
            calories=calories,
            protein=protein,
            fat=fat,
            carbohydrates=carbohydrates,
            price_per_100g=price_per_100g,
            unit=unit
        )
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient
    
    def get_all_ingredients(self) -> List[Ingredient]:
        """Get all ingredients."""
        return self.db.query(Ingredient).order_by(Ingredient.name).all()
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get ingredient by ID."""
        return self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    
    def search_ingredients(self, query: str) -> List[Ingredient]:
        """Search ingredients by name."""
        return self.db.query(Ingredient).filter(
            Ingredient.name.ilike(f'%{query}%')
        ).all()
    
    def update_ingredient(self, ingredient_id: int, **kwargs) -> Optional[Ingredient]:
        """Update ingredient fields."""
        ingredient = self.get_ingredient_by_id(ingredient_id)
        if ingredient:
            for key, value in kwargs.items():
                if hasattr(ingredient, key):
                    setattr(ingredient, key, value)
            self.db.commit()
            self.db.refresh(ingredient)
        return ingredient
    
    def delete_ingredient(self, ingredient_id: int) -> bool:
        """Delete an ingredient."""
        ingredient = self.get_ingredient_by_id(ingredient_id)
        if ingredient:
            self.db.delete(ingredient)
            self.db.commit()
            return True
        return False


class RecipeService:
    """Service for managing recipes."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_recipe(self, name: str, description: str = '', instructions: str = '',
                     prep_time_minutes: int = 0, servings: int = 1) -> Recipe:
        """Create a new recipe."""
        recipe = Recipe(
            name=name,
            description=description,
            instructions=instructions,
            prep_time_minutes=prep_time_minutes,
            servings=servings
        )
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe
    
    def add_ingredient_to_recipe(self, recipe_id: int, ingredient_id: int, 
                                quantity_grams: float) -> bool:
        """Add an ingredient to a recipe with specified quantity."""
        # Check if relationship already exists
        existing = self.db.query(recipe_ingredients).filter(
            and_(
                recipe_ingredients.c.recipe_id == recipe_id,
                recipe_ingredients.c.ingredient_id == ingredient_id
            )
        ).first()
        
        if existing:
            # Update quantity
            self.db.execute(
                recipe_ingredients.update().where(
                    and_(
                        recipe_ingredients.c.recipe_id == recipe_id,
                        recipe_ingredients.c.ingredient_id == ingredient_id
                    )
                ).values(quantity=quantity_grams)
            )
        else:
            # Insert new relationship
            self.db.execute(
                recipe_ingredients.insert().values(
                    recipe_id=recipe_id,
                    ingredient_id=ingredient_id,
                    quantity=quantity_grams
                )
            )
        
        self.db.commit()
        return True
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by ID with ingredients."""
        return self.db.query(Recipe).options(
            joinedload(Recipe.ingredients)
        ).filter(Recipe.id == recipe_id).first()
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all recipes."""
        return self.db.query(Recipe).options(
            joinedload(Recipe.ingredients)
        ).all()
    
    def search_recipes(self, query: str) -> List[Recipe]:
        """Search recipes by name or description."""
        return self.db.query(Recipe).filter(
            Recipe.name.ilike(f'%{query}%')
        ).all()
    
    def calculate_recipe_nutrition(self, recipe_id: int) -> Dict:
        """Calculate total KBZHU and price for a recipe."""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return {}
        
        # Get ingredient quantities from association table
        assoc_query = self.db.query(
            recipe_ingredients.c.ingredient_id,
            recipe_ingredients.c.quantity
        ).filter(recipe_ingredients.c.recipe_id == recipe_id).all()
        
        total = {
            'calories': 0.0,
            'protein': 0.0,
            'fat': 0.0,
            'carbohydrates': 0.0,
            'price': 0.0,
            'total_weight': 0.0
        }
        
        for ingredient_id, quantity in assoc_query:
            ingredient = self.db.query(Ingredient).filter(
                Ingredient.id == ingredient_id
            ).first()
            
            if ingredient:
                nutrition = ingredient.get_nutrition_for_quantity(quantity)
                total['calories'] += nutrition['calories']
                total['protein'] += nutrition['protein']
                total['fat'] += nutrition['fat']
                total['carbohydrates'] += nutrition['carbohydrates']
                total['price'] += nutrition['price']
                total['total_weight'] += quantity
        
        return total
    
    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe."""
        recipe = self.get_recipe_by_id(recipe_id)
        if recipe:
            self.db.delete(recipe)
            self.db.commit()
            return True
        return False


class MealPlanService:
    """Service for managing meal plans."""
    
    MEAL_TYPES = [
        'breakfast',
        'second_breakfast',
        'lunch',
        'snack',
        'dinner',
        'second_snack'
    ]
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_meal_plan(self, plan_date: date, notes: str = '') -> MealPlan:
        """Create a new meal plan for a specific date."""
        # Check if meal plan already exists for this date
        existing = self.db.query(MealPlan).filter(
            MealPlan.date == plan_date
        ).first()
        
        if existing:
            return existing
        
        meal_plan = MealPlan(date=plan_date, notes=notes)
        self.db.add(meal_plan)
        self.db.commit()
        self.db.refresh(meal_plan)
        return meal_plan
    
    def add_recipe_to_meal(self, plan_date: date, recipe_id: int, 
                          meal_type: str) -> bool:
        """Add a recipe to a specific meal type for a date."""
        if meal_type not in self.MEAL_TYPES:
            raise ValueError(f"Invalid meal type: {meal_type}")
        
        # Get or create meal plan
        meal_plan = self.db.query(MealPlan).filter(
            MealPlan.date == plan_date
        ).first()
        
        if not meal_plan:
            meal_plan = self.create_meal_plan(plan_date)
        
        # Check if this recipe is already added for this meal type
        existing = self.db.query(meal_plan_recipes).filter(
            and_(
                meal_plan_recipes.c.meal_plan_id == meal_plan.id,
                meal_plan_recipes.c.recipe_id == recipe_id,
                meal_plan_recipes.c.meal_type == meal_type
            )
        ).first()
        
        if existing:
            return True  # Already added
        
        # Add the recipe to the meal
        self.db.execute(
            meal_plan_recipes.insert().values(
                meal_plan_id=meal_plan.id,
                recipe_id=recipe_id,
                meal_type=meal_type
            )
        )
        self.db.commit()
        return True
    
    def get_meal_plan_by_date(self, plan_date: date) -> Optional[MealPlan]:
        """Get meal plan for a specific date."""
        return self.db.query(MealPlan).options(
            joinedload(MealPlan.recipes)
        ).filter(MealPlan.date == plan_date).first()
    
    def get_weekly_meal_plan(self, start_date: date) -> Dict[date, MealPlan]:
        """Get meal plans for a week starting from start_date."""
        end_date = start_date + timedelta(days=6)
        
        meal_plans = self.db.query(MealPlan).options(
            joinedload(MealPlan.recipes)
        ).filter(
            and_(
                MealPlan.date >= start_date,
                MealPlan.date <= end_date
            )
        ).all()
        
        return {mp.date: mp for mp in meal_plans}
    
    def get_monthly_meal_plan(self, year: int, month: int) -> Dict[date, MealPlan]:
        """Get meal plans for a specific month."""
        from sqlalchemy import func
        
        meal_plans = self.db.query(MealPlan).options(
            joinedload(MealPlan.recipes)
        ).filter(
            and_(
                func.strftime('%Y', MealPlan.date) == str(year),
                func.strftime('%m', MealPlan.date) == str(month).zfill(2)
            )
        ).all()
        
        return {mp.date: mp for mp in meal_plans}
    
    def get_meals_by_type(self, plan_date: date) -> Dict[str, List[Dict]]:
        """Get all meals grouped by type for a specific date."""
        meal_plan = self.get_meal_plan_by_date(plan_date)
        
        meals = {meal_type: [] for meal_type in self.MEAL_TYPES}
        
        if not meal_plan:
            return meals
        
        # Query the association table directly to get meal types
        associations = self.db.query(
            meal_plan_recipes.c.recipe_id,
            meal_plan_recipes.c.meal_type
        ).filter(
            meal_plan_recipes.c.meal_plan_id == meal_plan.id
        ).all()
        
        for recipe_id, meal_type in associations:
            recipe = self.db.query(Recipe).options(
                joinedload(Recipe.ingredients)
            ).filter(Recipe.id == recipe_id).first()
            
            if recipe:
                recipe_service = RecipeService(self.db)
                nutrition = recipe_service.calculate_recipe_nutrition(recipe.id)
                
                meals[meal_type].append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'nutrition': nutrition
                })
        
        return meals
    
    def calculate_daily_nutrition(self, plan_date: date) -> Dict:
        """Calculate total KBZHU and price for all meals on a specific date."""
        meals = self.get_meals_by_type(plan_date)
        
        daily_total = {
            'calories': 0.0,
            'protein': 0.0,
            'fat': 0.0,
            'carbohydrates': 0.0,
            'price': 0.0
        }
        
        meal_totals = {}
        
        for meal_type, recipes in meals.items():
            meal_total = {
                'calories': 0.0,
                'protein': 0.0,
                'fat': 0.0,
                'carbohydrates': 0.0,
                'price': 0.0
            }
            
            for recipe in recipes:
                nutrition = recipe['nutrition']
                meal_total['calories'] += nutrition['calories']
                meal_total['protein'] += nutrition['protein']
                meal_total['fat'] += nutrition['fat']
                meal_total['carbohydrates'] += nutrition['carbohydrates']
                meal_total['price'] += nutrition['price']
                
                daily_total['calories'] += nutrition['calories']
                daily_total['protein'] += nutrition['protein']
                daily_total['fat'] += nutrition['fat']
                daily_total['carbohydrates'] += nutrition['carbohydrates']
                daily_total['price'] += nutrition['price']
            
            meal_totals[meal_type] = meal_total
        
        return {
            'daily_total': daily_total,
            'by_meal': meal_totals
        }
    
    def remove_recipe_from_meal(self, plan_date: date, recipe_id: int, 
                               meal_type: str) -> bool:
        """Remove a recipe from a specific meal."""
        meal_plan = self.get_meal_plan_by_date(plan_date)
        if not meal_plan:
            return False
        
        self.db.execute(
            meal_plan_recipes.delete().where(
                and_(
                    meal_plan_recipes.c.meal_plan_id == meal_plan.id,
                    meal_plan_recipes.c.recipe_id == recipe_id,
                    meal_plan_recipes.c.meal_type == meal_type
                )
            )
        )
        self.db.commit()
        return True


class ShoppingListService:
    """Service for generating and managing shopping lists."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def generate_shopping_list_from_week(self, start_date: date) -> List[Dict]:
        """Generate a shopping list based on weekly meal plan."""
        meal_plan_service = MealPlanService(self.db)
        weekly_plans = meal_plan_service.get_weekly_meal_plan(start_date)
        
        # Aggregate all ingredients needed
        ingredient_totals = {}  # ingredient_id -> {'quantity': float, 'price': float}
        
        for plan_date, meal_plan in weekly_plans.items():
            # Get all recipes for this day
            associations = self.db.query(
                meal_plan_recipes.c.recipe_id
            ).filter(
                meal_plan_recipes.c.meal_plan_id == meal_plan.id
            ).all()
            
            for (recipe_id,) in associations:
                # Get ingredients for this recipe from the association table
                recipe_ingreds = self.db.query(
                    recipe_ingredients_assoc.c.ingredient_id,
                    recipe_ingredients_assoc.c.quantity
                ).filter(
                    recipe_ingredients_assoc.c.recipe_id == recipe_id
                ).all()
                
                for ingredient_id, quantity in recipe_ingreds:
                    if ingredient_id not in ingredient_totals:
                        ingredient_totals[ingredient_id] = {
                            'quantity': 0.0,
                            'price': 0.0
                        }
                    
                    ingredient_totals[ingredient_id]['quantity'] += quantity
                    
                    # Calculate price
                    ingredient = self.db.query(Ingredient).filter(
                        Ingredient.id == ingredient_id
                    ).first()
                    
                    if ingredient:
                        price = ingredient.price_per_100g * (quantity / 100.0)
                        ingredient_totals[ingredient_id]['price'] += price
        
        # Build shopping list
        shopping_list = []
        for ingredient_id, totals in ingredient_totals.items():
            ingredient = self.db.query(Ingredient).filter(
                Ingredient.id == ingredient_id
            ).first()
            
            if ingredient:
                shopping_list.append({
                    'ingredient_id': ingredient.id,
                    'name': ingredient.name,
                    'quantity_needed': totals['quantity'],
                    'unit': ingredient.unit,
                    'estimated_price': totals['price'],
                    'price_per_100g': ingredient.price_per_100g
                })
        
        # Sort by estimated price (most expensive first)
        shopping_list.sort(key=lambda x: x['estimated_price'], reverse=True)
        
        return shopping_list
    
    def save_shopping_list(self, shopping_list: List[Dict], 
                          created_date: date = None) -> List[ShoppingListItem]:
        """Save generated shopping list to database."""
        if created_date is None:
            created_date = date.today()
        
        saved_items = []
        
        for item in shopping_list:
            shopping_item = ShoppingListItem(
                ingredient_id=item['ingredient_id'],
                quantity_needed=item['quantity_needed'],
                estimated_price=item['estimated_price'],
                created_date=created_date
            )
            self.db.add(shopping_item)
            saved_items.append(shopping_item)
        
        self.db.commit()
        
        for item in saved_items:
            self.db.refresh(item)
        
        return saved_items
    
    def get_recent_shopping_list(self, limit: int = 5) -> List[ShoppingListItem]:
        """Get recent shopping list items."""
        return self.db.query(ShoppingListItem).options(
            joinedload(ShoppingListItem.ingredient)
        ).order_by(
            ShoppingListItem.created_date.desc(),
            ShoppingListItem.id.desc()
        ).limit(limit).all()
    
    def mark_as_purchased(self, item_id: int) -> bool:
        """Mark a shopping list item as purchased."""
        item = self.db.query(ShoppingListItem).filter(
            ShoppingListItem.id == item_id
        ).first()
        
        if item:
            item.is_purchased = 1
            self.db.commit()
            return True
        return False
    
    def clear_shopping_list(self, before_date: date = None) -> int:
        """Clear old shopping list items."""
        query = self.db.query(ShoppingListItem)
        if before_date:
            deleted = query.filter(
                ShoppingListItem.created_date < before_date
            ).delete()
        else:
            deleted = query.delete()
        
        self.db.commit()
        return deleted
