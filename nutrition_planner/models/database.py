"""
Database models for the Nutrition Planner application.
Uses SQLAlchemy for ORM with SQLite backend (can be changed to PostgreSQL later).
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date

Base = declarative_base()

# Association table for many-to-many relationship between recipes and ingredients
recipe_ingredients_assoc = Table(
    'recipe_ingredients',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True),
    Column('quantity', Float, nullable=False)  # quantity in grams
)

# Association table for meal plans and recipes
meal_plan_recipes = Table(
    'meal_plan_recipes',
    Base.metadata,
    Column('meal_plan_id', Integer, ForeignKey('meal_plans.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('meal_type', String(50), nullable=False)  # breakfast, second_breakfast, lunch, snack, dinner, second_snack
)


class Ingredient(Base):
    """Ingredient model with KBZHU and price information."""
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    calories = Column(Float, nullable=False)  # per 100g
    protein = Column(Float, nullable=False)  # per 100g
    fat = Column(Float, nullable=False)  # per 100g
    carbohydrates = Column(Float, nullable=False)  # per 100g
    price_per_100g = Column(Float, nullable=False, default=0.0)
    unit = Column(String(20), default='г')  # unit of measurement
    
    recipes = relationship("Recipe", secondary=recipe_ingredients_assoc, back_populates="ingredients")
    
    def __repr__(self):
        return f"<Ingredient(name='{self.name}', calories={self.calories})>"
    
    def get_nutrition_for_quantity(self, quantity_grams):
        """Calculate KBZHU and price for a specific quantity."""
        multiplier = quantity_grams / 100.0
        return {
            'calories': self.calories * multiplier,
            'protein': self.protein * multiplier,
            'fat': self.fat * multiplier,
            'carbohydrates': self.carbohydrates * multiplier,
            'price': self.price_per_100g * multiplier
        }


class Recipe(Base):
    """Recipe model containing ingredients and preparation instructions."""
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    instructions = Column(String(5000))
    prep_time_minutes = Column(Integer, default=0)
    servings = Column(Integer, default=1)
    
    ingredients = relationship("Ingredient", secondary=recipe_ingredients_assoc, 
                              back_populates="recipes",
                              lazy='joined')
    
    def __repr__(self):
        return f"<Recipe(name='{self.name}')>"
    
    def get_total_nutrition(self):
        """Calculate total KBZHU and price for the recipe."""
        total = {'calories': 0, 'protein': 0, 'fat': 0, 'carbohydrates': 0, 'price': 0}
        
        for ingredient in self.ingredients:
            # Get the quantity from the association table
            assoc = next((r for r in self.ingredients if r.id == ingredient.id), None)
            if assoc:
                # We need to access the quantity from the association
                pass
        
        # For simplicity, we'll calculate this in the service layer
        return total


class MealPlan(Base):
    """Meal plan for a specific date with multiple meal types."""
    __tablename__ = 'meal_plans'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    notes = Column(String(500))
    
    # Relationships to recipes through association table
    recipes = relationship("Recipe", secondary=meal_plan_recipes, 
                          backref="meal_plans",
                          lazy='joined')
    
    def __repr__(self):
        return f"<MealPlan(date='{self.date}')>"
    
    def get_meals_by_type(self):
        """Group recipes by meal type."""
        meals = {
            'breakfast': [],
            'second_breakfast': [],
            'lunch': [],
            'snack': [],
            'dinner': [],
            'second_snack': []
        }
        # Implementation will be in service layer
        return meals


class ShoppingListItem(Base):
    """Shopping list item generated from meal plans."""
    __tablename__ = 'shopping_list_items'
    
    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    quantity_needed = Column(Float, nullable=False)
    estimated_price = Column(Float, nullable=False)
    is_purchased = Column(Integer, default=0)  # boolean as integer
    created_date = Column(Date, default=date.today)
    
    ingredient = relationship("Ingredient", backref="shopping_list_items")
    
    def __repr__(self):
        return f"<ShoppingListItem(ingredient='{self.ingredient.name}', quantity={self.quantity_needed})>"


def init_db(database_url='sqlite:///nutrition_planner.db'):
    """Initialize the database and create tables."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
