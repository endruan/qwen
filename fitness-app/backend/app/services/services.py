from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, timedelta
from ..models.models import (
    User, UserMetric, Ingredient, Recipe, RecipeIngredient,
    MealPlan, ShoppingList, Exercise, Workout, WorkoutExercise
)
from ..schemas.schemas import (
    UserRegister, IngredientCreate, IngredientUpdate,
    RecipeCreate, RecipeUpdate, MealPlanCreate
)
from ..core.security import get_password_hash


# Auth services
def create_user(db: Session, user_data: UserRegister) -> User:
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        height=user_data.height,
        weight=user_data.weight,
        age=user_data.age,
        gender=user_data.gender,
        activity_level=user_data.activity_level,
        goal=user_data.goal
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    from ..core.security import verify_password
    if not verify_password(password, user.password_hash):
        return None
    return user


# Ingredient services
def get_ingredients(db: Session, skip: int = 0, limit: int = 100) -> List[Ingredient]:
    return db.query(Ingredient).offset(skip).limit(limit).all()


def get_ingredient(db: Session, ingredient_id: int) -> Optional[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()


def create_ingredient(db: Session, ingredient: IngredientCreate) -> Ingredient:
    db_ingredient = Ingredient(**ingredient.model_dump())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


def update_ingredient(db: Session, ingredient_id: int, ingredient_update: IngredientUpdate) -> Optional[Ingredient]:
    db_ingredient = get_ingredient(db, ingredient_id)
    if not db_ingredient:
        return None
    
    update_data = ingredient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ingredient, field, value)
    
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


def delete_ingredient(db: Session, ingredient_id: int) -> bool:
    db_ingredient = get_ingredient(db, ingredient_id)
    if not db_ingredient:
        return False
    
    # Check if used in recipes
    usage_count = db.query(RecipeIngredient).filter(
        RecipeIngredient.ingredient_id == ingredient_id
    ).count()
    
    if usage_count > 0:
        raise ValueError(f"Ingredient is used in {usage_count} recipe(s)")
    
    db.delete(db_ingredient)
    db.commit()
    return True


# Recipe services - FIXED version with proper transaction handling
def get_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
    return db.query(Recipe).options(
        joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
    ).offset(skip).limit(limit).all()


def get_recipe(db: Session, recipe_id: int) -> Optional[Recipe]:
    recipe = db.query(Recipe).options(
        joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
    ).filter(Recipe.id == recipe_id).first()
    return recipe


def create_recipe(db: Session, recipe: RecipeCreate, user_id: Optional[int] = None) -> Recipe:
    """
    Create recipe with ingredients - FIXED to properly save ingredients
    """
    try:
        # Create recipe without ingredients first
        recipe_data = recipe.model_dump(exclude={'ingredients'})
        db_recipe = Recipe(**recipe_data, created_by=user_id)
        
        db.add(db_recipe)
        db.flush()  # Get the recipe ID without committing
        
        # Add ingredients
        if recipe.ingredients:
            for ing in recipe.ingredients:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=db_recipe.id,
                    ingredient_id=ing.ingredient_id,
                    quantity=ing.quantity
                )
                db.add(recipe_ingredient)
        
        # Calculate nutrition
        db_recipe.calculate_nutrition()
        
        db.commit()
        db.refresh(db_recipe)
        
        # Reload with ingredients
        return get_recipe(db, db_recipe.id)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create recipe: {str(e)}")


def update_recipe(db: Session, recipe_id: int, recipe_update: RecipeUpdate) -> Optional[Recipe]:
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None
    
    try:
        update_data = recipe_update.model_dump(exclude_unset=True)
        ingredients_data = update_data.pop('ingredients', None)
        
        # Update basic fields
        for field, value in update_data.items():
            setattr(db_recipe, field, value)
        
        # Update ingredients if provided
        if ingredients_data is not None:
            # Delete old ingredients
            db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe_id
            ).delete()
            
            # Add new ingredients
            for ing in ingredients_data:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=db_recipe.id,
                    ingredient_id=ing['ingredient_id'],
                    quantity=ing['quantity']
                )
                db.add(recipe_ingredient)
        
        # Recalculate nutrition
        db_recipe.calculate_nutrition()
        
        db.commit()
        db.refresh(db_recipe)
        
        return get_recipe(db, db_recipe.id)
    
    except Exception as e:
        db.rollback()
        raise


def delete_recipe(db: Session, recipe_id: int) -> bool:
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        return False
    
    db.delete(db_recipe)
    db.commit()
    return True


# Meal Plan services
def get_meal_plans(db: Session, user_id: int, start_date: date, end_date: date) -> List[MealPlan]:
    return db.query(MealPlan).options(
        joinedload(MealPlan.recipe).joinedload(Recipe.ingredients)
    ).filter(
        MealPlan.user_id == user_id,
        MealPlan.date >= start_date,
        MealPlan.date <= end_date
    ).order_by(MealPlan.date, MealPlan.meal_type).all()


def create_meal_plan(db: Session, meal_plan: MealPlanCreate, user_id: int) -> MealPlan:
    db_meal_plan = MealPlan(**meal_plan.model_dump(), user_id=user_id)
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan


def delete_meal_plan(db: Session, meal_plan_id: int, user_id: int) -> bool:
    db_meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == user_id
    ).first()
    if not db_meal_plan:
        return False
    
    db.delete(db_meal_plan)
    db.commit()
    return True


# Shopping List services
def generate_shopping_list(db: Session, user_id: int, start_date: date, end_date: date) -> List[ShoppingList]:
    # Clear existing shopping list
    db.query(ShoppingList).filter(ShoppingList.user_id == user_id).delete()
    
    # Get meal plans for the period
    meal_plans = db.query(MealPlan).filter(
        MealPlan.user_id == user_id,
        MealPlan.date >= start_date,
        MealPlan.date <= end_date
    ).all()
    
    # Aggregate ingredients
    ingredient_quantities = {}
    
    for meal_plan in meal_plans:
        recipe = db.query(Recipe).options(
            joinedload(Recipe.ingredients)
        ).filter(Recipe.id == meal_plan.recipe_id).first()
        
        if recipe and recipe.ingredients:
            for recipe_ingredient in recipe.ingredients:
                ing_id = recipe_ingredient.ingredient_id
                quantity = recipe_ingredient.quantity
                
                if ing_id in ingredient_quantities:
                    ingredient_quantities[ing_id] += quantity
                else:
                    ingredient_quantities[ing_id] = quantity
    
    # Create shopping list items
    shopping_items = []
    for ing_id, quantity in ingredient_quantities.items():
        shopping_item = ShoppingList(
            user_id=user_id,
            ingredient_id=ing_id,
            quantity=quantity
        )
        db.add(shopping_item)
        shopping_items.append(shopping_item)
    
    db.commit()
    
    # Reload with ingredients
    return db.query(ShoppingList).options(
        joinedload(ShoppingList.ingredient)
    ).filter(ShoppingList.user_id == user_id).all()


def get_shopping_list(db: Session, user_id: int) -> List[ShoppingList]:
    return db.query(ShoppingList).options(
        joinedload(ShoppingList.ingredient)
    ).filter(ShoppingList.user_id == user_id).all()


def toggle_shopping_item(db: Session, item_id: int, user_id: int) -> Optional[ShoppingList]:
    item = db.query(ShoppingList).filter(
        ShoppingList.id == item_id,
        ShoppingList.user_id == user_id
    ).first()
    
    if not item:
        return None
    
    item.purchased = not item.purchased
    db.commit()
    db.refresh(item)
    return item


# User Metrics services
def get_user_metrics(db: Session, user_id: int) -> List[UserMetric]:
    return db.query(UserMetric).filter(
        UserMetric.user_id == user_id
    ).order_by(UserMetric.date.desc()).all()


def create_user_metric(db: Session, user_id: int, metric_data) -> UserMetric:
    db_metric = UserMetric(**metric_data.model_dump(exclude={'date'}), user_id=user_id)
    if metric_data.date:
        db_metric.date = metric_data.date
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


# Workout services
def get_workouts(db: Session, user_id: int) -> List[Workout]:
    return db.query(Workout).options(
        joinedload(Workout.exercises).joinedload(WorkoutExercise.exercise)
    ).filter(Workout.user_id == user_id).order_by(Workout.date.desc()).all()


def get_workout(db: Session, workout_id: int, user_id: int) -> Optional[Workout]:
    return db.query(Workout).options(
        joinedload(Workout.exercises).joinedload(WorkoutExercise.exercise)
    ).filter(
        Workout.id == workout_id,
        Workout.user_id == user_id
    ).first()


def create_workout(db: Session, workout_data, user_id: int) -> Workout:
    workout_info = workout_data.model_dump(exclude={'exercises'})
    db_workout = Workout(**workout_info, user_id=user_id)
    
    db.add(db_workout)
    db.flush()
    
    # Add exercises
    if workout_data.exercises:
        for ex in workout_data.exercises:
            workout_exercise = WorkoutExercise(
                workout_id=db_workout.id,
                exercise_id=ex.exercise_id,
                sets=ex.sets,
                reps=ex.reps,
                weight=ex.weight
            )
            db.add(workout_exercise)
    
    db.commit()
    db.refresh(db_workout)
    
    return get_workout(db, db_workout.id, user_id)


def update_workout(db: Session, workout_id: int, user_id: int, workout_update) -> Optional[Workout]:
    db_workout = get_workout(db, workout_id, user_id)
    if not db_workout:
        return None
    
    update_data = workout_update.model_dump(exclude_unset=True)
    exercises_data = update_data.pop('exercises', None)
    
    for field, value in update_data.items():
        setattr(db_workout, field, value)
    
    if exercises_data is not None:
        db.query(WorkoutExercise).filter(
            WorkoutExercise.workout_id == workout_id
        ).delete()
        
        for ex in exercises_data:
            workout_exercise = WorkoutExercise(
                workout_id=db_workout.id,
                exercise_id=ex['exercise_id'],
                sets=ex['sets'],
                reps=ex['reps'],
                weight=ex['weight']
            )
            db.add(workout_exercise)
    
    db.commit()
    db.refresh(db_workout)
    
    return get_workout(db, workout_id, user_id)


# Exercise services
def get_exercises(db: Session) -> List[Exercise]:
    return db.query(Exercise).all()


def create_exercise(db: Session, exercise_data) -> Exercise:
    db_exercise = Exercise(**exercise_data.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


# Nutrition calculation helpers
def calculate_daily_nutrition(db: Session, user_id: int, target_date: date) -> dict:
    meal_plans = db.query(MealPlan).options(
        joinedload(MealPlan.recipe).joinedload(Recipe.ingredients)
    ).filter(
        MealPlan.user_id == user_id,
        MealPlan.date == target_date
    ).all()
    
    total_kcal = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    
    for meal_plan in meal_plans:
        recipe = meal_plan.recipe
        total_kcal += recipe.total_kcal or 0
        total_protein += recipe.total_protein or 0
        total_fat += recipe.total_fat or 0
        total_carbs += recipe.total_carbs or 0
    
    return {
        'total_kcal': total_kcal,
        'total_protein': total_protein,
        'total_fat': total_fat,
        'total_carbs': total_carbs
    }


def calculate_user_goals(user: User) -> dict:
    """Calculate recommended daily calorie and macro goals based on user profile"""
    if not all([user.weight, user.height, user.age, user.gender]):
        return {
            'calories': 2000,
            'protein': 150,
            'fat': 67,
            'carbs': 250
        }
    
    # BMR calculation (Mifflin-St Jeor)
    if user.gender == 'male':
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
    
    # Activity multiplier
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    tdee = bmr * activity_multipliers.get(user.activity_level, 1.55)
    
    # Goal adjustment
    if user.goal == 'lose':
        tdee -= 500
    elif user.goal == 'gain':
        tdee += 500
    
    calories = round(tdee)
    protein = round(user.weight * 2)  # 2g per kg bodyweight
    fat = round(calories * 0.25 / 9)  # 25% of calories from fat
    carbs = round((calories - protein * 4 - fat * 9) / 4)
    
    return {
        'calories': calories,
        'protein': protein,
        'fat': fat,
        'carbs': carbs
    }
