from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    telegram_id = Column(String, unique=True, nullable=True)
    
    # Profile
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)  # cm
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # male/female
    activity_level = Column(String, default="moderate")  # sedentary/light/moderate/active/very_active
    goal = Column(String, default="maintain")  # lose/maintain/gain
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metrics = relationship("UserMetric", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    shopping_list = relationship("ShoppingList", back_populates="user", cascade="all, delete-orphan")


class UserMetric(Base):
    __tablename__ = "user_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=datetime.utcnow().date(), nullable=False)
    
    weight = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    chest = Column(Float, nullable=True)
    biceps = Column(Float, nullable=True)
    hips = Column(Float, nullable=True)
    body_fat = Column(Float, nullable=True)
    
    user = relationship("User", back_populates="metrics")


class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    
    # Nutrition per 100g/ml/unit
    kcal_per_100 = Column(Float, default=0)
    protein_per_100 = Column(Float, default=0)
    fat_per_100 = Column(Float, default=0)
    carbs_per_100 = Column(Float, default=0)
    
    # Price info
    price_per_package = Column(Float, default=0)
    package_quantity = Column(Float, default=100)
    unit_type = Column(String, default="g")  # g/kg/ml/l/pcs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")
    shopping_items = relationship("ShoppingList", back_populates="ingredient", cascade="all, delete-orphan")
    
    @property
    def price_per_unit(self):
        """Calculate price per gram/ml/unit"""
        if self.package_quantity and self.package_quantity > 0:
            return self.price_per_package / self.package_quantity
        return 0


class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)
    servings = Column(Integer, default=1)
    
    # Calculated totals
    total_kcal = Column(Float, default=0)
    total_protein = Column(Float, default=0)
    total_fat = Column(Float, default=0)
    total_carbs = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="recipe", cascade="all, delete-orphan")
    
    def calculate_nutrition(self):
        """Recalculate total nutrition from ingredients"""
        total_kcal = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_cost = 0
        
        for ri in self.ingredients:
            ingredient = ri.ingredient
            multiplier = ri.quantity / 100  # Convert to per-100g basis
            
            total_kcal += ingredient.kcal_per_100 * multiplier
            total_protein += ingredient.protein_per_100 * multiplier
            total_fat += ingredient.fat_per_100 * multiplier
            total_carbs += ingredient.carbs_per_100 * multiplier
            total_cost += ingredient.price_per_unit * ri.quantity
        
        self.total_kcal = round(total_kcal, 2)
        self.total_protein = round(total_protein, 2)
        self.total_fat = round(total_fat, 2)
        self.total_carbs = round(total_carbs, 2)
        self.total_cost = round(total_cost, 2)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # in grams/ml/units
    
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")


class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    
    date = Column(Date, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast/lunch/dinner/snack
    
    user = relationship("User", back_populates="meal_plans")
    recipe = relationship("Recipe", back_populates="meal_plans")


class ShoppingList(Base):
    __tablename__ = "shopping_list"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    
    quantity = Column(Float, nullable=False)
    purchased = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="shopping_list")
    ingredient = relationship("Ingredient", back_populates="shopping_items")


class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)
    muscle_group = Column(String, nullable=True)  # chest/back/legs/shoulders/arms/core
    
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan")


class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    date = Column(Date, nullable=False)
    duration = Column(Integer, nullable=True)  # minutes
    notes = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=10)
    weight = Column(Float, default=0)
    completed = Column(Boolean, default=False)
    
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
