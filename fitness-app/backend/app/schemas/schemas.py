from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = "moderate"
    goal: Optional[str] = "maintain"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = "moderate"
    goal: Optional[str] = "maintain"


class UserResponse(UserBase):
    id: int
    telegram_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserMetricCreate(BaseModel):
    weight: Optional[float] = None
    waist: Optional[float] = None
    chest: Optional[float] = None
    biceps: Optional[float] = None
    hips: Optional[float] = None
    body_fat: Optional[float] = None
    date: Optional[date] = None


class UserMetricResponse(UserMetricCreate):
    id: int
    user_id: int
    date: date
    
    class Config:
        from_attributes = True


# Ingredient schemas
class IngredientBase(BaseModel):
    name: str
    kcal_per_100: float = 0
    protein_per_100: float = 0
    fat_per_100: float = 0
    carbs_per_100: float = 0
    price_per_package: float = 0
    package_quantity: float = 100
    unit_type: str = "g"


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    kcal_per_100: Optional[float] = None
    protein_per_100: Optional[float] = None
    fat_per_100: Optional[float] = None
    carbs_per_100: Optional[float] = None
    price_per_package: Optional[float] = None
    package_quantity: Optional[float] = None
    unit_type: Optional[str] = None


class IngredientResponse(IngredientBase):
    id: int
    price_per_unit: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Recipe schemas
class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredientResponse(RecipeIngredientBase):
    id: int
    recipe_id: int
    ingredient: IngredientResponse
    
    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    servings: int = 1


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate]


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    servings: Optional[int] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None


class RecipeResponse(RecipeBase):
    id: int
    total_kcal: float
    total_protein: float
    total_fat: float
    total_carbs: float
    total_cost: float
    ingredients: List[RecipeIngredientResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


# Meal Plan schemas
class MealPlanBase(BaseModel):
    recipe_id: int
    date: date
    meal_type: str  # breakfast/lunch/dinner/snack


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanResponse(MealPlanBase):
    id: int
    user_id: int
    recipe: RecipeResponse
    
    class Config:
        from_attributes = True


# Shopping List schemas
class ShoppingListItemBase(BaseModel):
    ingredient_id: int
    quantity: float


class ShoppingListItemCreate(ShoppingListItemBase):
    pass


class ShoppingListItemResponse(ShoppingListItemBase):
    id: int
    user_id: int
    purchased: bool
    ingredient: IngredientResponse
    
    class Config:
        from_attributes = True


# Exercise schemas
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    muscle_group: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: int
    
    class Config:
        from_attributes = True


class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    sets: int = 3
    reps: int = 10
    weight: float = 0


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutExerciseResponse(WorkoutExerciseBase):
    id: int
    workout_id: int
    completed: bool
    exercise: ExerciseResponse
    
    class Config:
        from_attributes = True


# Workout schemas
class WorkoutBase(BaseModel):
    date: date
    duration: Optional[int] = None
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate]


class WorkoutUpdate(BaseModel):
    duration: Optional[int] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None
    exercises: Optional[List[WorkoutExerciseCreate]] = None


class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    completed: bool
    created_at: datetime
    exercises: List[WorkoutExerciseResponse] = []
    
    class Config:
        from_attributes = True


# Dashboard schemas
class NutritionSummary(BaseModel):
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float
    calorie_goal: float
    protein_goal: float
    fat_goal: float
    carbs_goal: float


class WeightProgress(BaseModel):
    date: date
    weight: float


class DashboardData(BaseModel):
    nutrition: NutritionSummary
    weight_history: List[WeightProgress]
    recent_workouts: List[WorkoutResponse]
    upcoming_meals: List[MealPlanResponse]
