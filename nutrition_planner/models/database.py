from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=True)
    name = Column(String, default="Пользователь")
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)  # см
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # 'male' или 'female'
    activity_level = Column(String, default="moderate")  # low, moderate, high
    target_calories = Column(Integer, default=2000)
    target_protein = Column(Float, default=150)
    target_fat = Column(Float, default=70)
    target_carbs = Column(Float, default=200)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    measurements = relationship("UserMeasurement", back_populates="user", cascade="all, delete-orphan")
    supplements = relationship("Supplement", back_populates="user", cascade="all, delete-orphan")

class UserMeasurement(Base):
    __tablename__ = 'user_measurements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, default=datetime.utcnow().date())
    weight = Column(Float, nullable=True)
    chest = Column(Float, nullable=True)  # Грудь
    waist = Column(Float, nullable=True)  # Талия
    hips = Column(Float, nullable=True)   # Бедра
    bicep = Column(Float, nullable=True)  # Бицепс
    thigh = Column(Float, nullable=True)  # Бедро
    neck = Column(Float, nullable=True)   # Шея
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="measurements")

class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    calories_per_100g = Column(Float, default=0)
    protein_per_100g = Column(Float, default=0)
    fat_per_100g = Column(Float, default=0)
    carbs_per_100g = Column(Float, default=0)
    price_per_package = Column(Float, default=0)
    package_weight = Column(Float, default=1000)  # вес упаковки в граммах/мл
    unit = Column(String, default="г")  # г, кг, шт, л, мл
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient", cascade="all, delete-orphan")
    
    @property
    def price_per_unit(self):
        """Цена за 1 единицу (грамм/шт/мл)"""
        if self.package_weight > 0:
            return self.price_per_package / self.package_weight
        return 0
    
    @property
    def price_per_kg(self):
        """Цена за кг/литр"""
        if self.unit in ['г', 'кг']:
            return self.price_per_unit * 1000
        elif self.unit in ['мл', 'л']:
            return self.price_per_unit * 1000
        return self.price_per_unit

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # HTML форматирование
    photo_path = Column(String, nullable=True)
    servings = Column(Integer, default=1)
    prep_time = Column(Integer, nullable=True)  # минут
    cook_time = Column(Integer, nullable=True)  # минут
    category = Column(String, nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlanRecipe", back_populates="recipe")
    
    @property
    def total_calories(self):
        return sum(ri.total_calories for ri in self.ingredients)
    
    @property
    def total_protein(self):
        return sum(ri.total_protein for ri in self.ingredients)
    
    @property
    def total_fat(self):
        return sum(ri.total_fat for ri in self.ingredients)
    
    @property
    def total_carbs(self):
        return sum(ri.total_carbs for ri in self.ingredients)
    
    @property
    def total_cost(self):
        return sum(ri.total_cost for ri in self.ingredients)
    
    @property
    def calories_per_serving(self):
        return self.total_calories / self.servings if self.servings > 0 else 0
    
    @property
    def protein_per_serving(self):
        return self.total_protein / self.servings if self.servings > 0 else 0
    
    @property
    def fat_per_serving(self):
        return self.total_fat / self.servings if self.servings > 0 else 0
    
    @property
    def carbs_per_serving(self):
        return self.total_carbs / self.servings if self.servings > 0 else 0
    
    @property
    def cost_per_serving(self):
        return self.total_cost / self.servings if self.servings > 0 else 0

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    quantity = Column(Float, default=100)  # количество в граммах/мл/шт
    
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")
    
    @property
    def total_calories(self):
        return (self.ingredient.calories_per_100g * self.quantity) / 100
    
    @property
    def total_protein(self):
        return (self.ingredient.protein_per_100g * self.quantity) / 100
    
    @property
    def total_fat(self):
        return (self.ingredient.fat_per_100g * self.quantity) / 100
    
    @property
    def total_carbs(self):
        return (self.ingredient.carbs_per_100g * self.quantity) / 100
    
    @property
    def total_cost(self):
        return self.ingredient.price_per_unit * self.quantity

class MealPlan(Base):
    __tablename__ = 'meal_plans'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    meal_type = Column(String, nullable=False)  # breakfast, second_breakfast, lunch, snack, dinner, second_snack
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recipes = relationship("MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Уникальность комбинации даты и типа приема пищи для одного пользователя
        # (если будет поддержка нескольких пользователей)
    )

class MealPlanRecipe(Base):
    __tablename__ = 'meal_plan_recipes'
    
    id = Column(Integer, primary_key=True)
    meal_plan_id = Column(Integer, ForeignKey('meal_plans.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    servings = Column(Float, default=1)  # можно указать дробное количество порций
    
    meal_plan = relationship("MealPlan", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="meal_plans")
    
    @property
    def total_calories(self):
        return self.recipe.calories_per_serving * self.servings
    
    @property
    def total_protein(self):
        return self.recipe.protein_per_serving * self.servings
    
    @property
    def total_fat(self):
        return self.recipe.fat_per_serving * self.servings
    
    @property
    def total_carbs(self):
        return self.recipe.carbs_per_serving * self.servings
    
    @property
    def total_cost(self):
        return self.recipe.cost_per_serving * self.servings

class Supplement(Base):
    __tablename__ = 'supplements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)  # D3, Омега-3, Креатин и т.д.
    dosage = Column(String, nullable=True)  # дозировка (например, "1000 ME", "5г")
    frequency = Column(String, nullable=True)  # как часто принимать
    time_of_day = Column(String, nullable=True)  # утро, обед, вечер
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="supplements")

class ShoppingListItem(Base):
    __tablename__ = 'shopping_list_items'
    
    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    quantity = Column(Float, default=0)
    unit = Column(String, default="г")
    estimated_cost = Column(Float, default=0)
    is_purchased = Column(Boolean, default=False)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ingredient = relationship("Ingredient")

# Database setup
DATABASE_URL = "sqlite:///./nutrition.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
