from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    calories = Column(Float)  # на 100г/ед
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    
    # Логика цены и упаковки
    price = Column(Float)  # Цена за упаковку
    package_weight = Column(Float)  # Вес упаковки (г/мл/шт)
    unit = Column(String, default="г")  # г, кг, шт, мл, л
    
    recipes = relationship("RecipeIngredient", back_populates="ingredient")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)  # HTML контент
    image_path = Column(String, nullable=True)
    servings = Column(Integer, default=1)
    
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="recipe")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    weight = Column(Float)  # Вес в граммах/шт в рецепте
    
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")

class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)
    current_weight = Column(Float, default=0.0)
    target_calories = Column(Integer, default=2000)
    target_protein = Column(Float, default=150.0)
    target_fat = Column(Float, default=70.0)
    target_carbs = Column(Float, default=200.0)
    
    # Замеры
    waist = Column(Float, nullable=True)
    chest = Column(Float, nullable=True)
    bicep = Column(Float, nullable=True)
    hips = Column(Float, nullable=True)

class WeightLog(Base):
    __tablename__ = "weight_logs"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    weight = Column(Float)
    waist = Column(Float, nullable=True)
    chest = Column(Float, nullable=True)
    bicep = Column(Float, nullable=True)

class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    meal_type = Column(String)  # breakfast, lunch, etc.
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    servings_count = Column(Float, default=1.0)  # Сколько порций съедает пользователь
    
    recipe = relationship("Recipe", back_populates="meal_plans")

class Supplement(Base):
    __tablename__ = "supplements"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    dosage = Column(String)  # e.g., "5000 ME", "1 capsule"
    timing = Column(String)  # e.g., "Morning", "With food"
