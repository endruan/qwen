# models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean, DateTime, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
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
    
    # Новая логика цены
    price_per_unit = Column(Float, default=0)  # Цена за упаковку
    package_size = Column(Float, default=100)    # Размер упаковки (г, мл, шт)
    unit_type = Column(String, default="г")      # г, кг, мл, л, шт
    
    recipes = relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, default="")  # Поддерживает HTML
    instructions = Column(Text, default="")
    image_url = Column(String, nullable=True)  # Ссылка на фото
    servings = Column(Integer, default=1)       # Кол-во порций
    total_calories = Column(Float, default=0)
    total_protein = Column(Float, default=0)
    total_fat = Column(Float, default=0)
    total_carbs = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlanItem", back_populates="recipe")

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity = Column(Float, default=0)  # Количество в рецепте
    
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")

class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)
    current_weight = Column(Float, default=0)
    target_weight = Column(Float, default=0)
    height = Column(Integer, default=0)  # см
    age = Column(Integer, default=30)
    gender = Column(String, default="male")   # male/female
    activity_level = Column(String, default="moderate") # low, moderate, high
    target_calories = Column(Integer, default=2000)
    target_protein = Column(Float, default=150)
    target_fat = Column(Float, default=70)
    target_carbs = Column(Float, default=200)
    
    measurements = relationship("BodyMeasurement", back_populates="user", cascade="all, delete-orphan")
    weight_history = relationship("WeightLog", back_populates="user", cascade="all, delete-orphan")

class BodyMeasurement(Base):
    __tablename__ = "body_measurements"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now)
    chest = Column(Float, default=0) # Грудь
    waist = Column(Float, default=0) # Талия
    hips = Column(Float, default=0)  # Бедра
    bicep = Column(Float, default=0) # Бицепс
    thigh = Column(Float, default=0) # Бедро
    
    user = relationship("UserProfile", back_populates="measurements")

class WeightLog(Base):
    __tablename__ = "weight_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now)
    weight = Column(Float, default=0)
    
    user = relationship("UserProfile", back_populates="weight_history")

class Supplement(Base):
    __tablename__ = "supplements"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    dosage = Column(String, default="") # Например: 2000 ME, 5g
    timing = Column(String, default="") # Утро, Обед, Вечер
    is_active = Column(Boolean, default=True)

class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, unique=True)
    items = relationship("MealPlanItem", back_populates="plan", cascade="all, delete-orphan")

class MealPlanItem(Base):
    __tablename__ = "meal_plan_items"
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("meal_plans.id", ondelete="CASCADE"))
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    meal_type = Column(String) # breakfast, snack1, lunch, snack2, dinner, snack3
    servings_count = Column(Float, default=1.0) # Сколько порций едим
    
    plan = relationship("MealPlan", back_populates="items")
    recipe = relationship("Recipe", back_populates="meal_plans")

# Database setup
DATABASE_URL = "sqlite:///./nutrition.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
