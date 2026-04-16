from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.database import User, UserMeasurement, Ingredient, Recipe, RecipeIngredient, MealPlan, MealPlanRecipe, Supplement, ShoppingListItem
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, telegram_id: str = None) -> User:
        """Получить или создать пользователя"""
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update_user(self, user_id: int, **kwargs) -> User:
        """Обновить данные пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def calculate_bmi(self, weight: float, height: float) -> float:
        """Рассчитать ИМТ"""
        if height > 0:
            return weight / ((height / 100) ** 2)
        return 0
    
    def get_bmi_category(self, bmi: float) -> str:
        """Категория ИМТ"""
        if bmi < 18.5:
            return "Недостаточный вес"
        elif bmi < 25:
            return "Нормальный вес"
        elif bmi < 30:
            return "Избыточный вес"
        else:
            return "Ожирение"
    
    def calculate_daily_calories(self, weight: float, height: float, age: int, 
                                  gender: str, activity_level: str) -> int:
        """Расчет суточной нормы калорий (формула Миффлина-Сан Жеора)"""
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        activity_multipliers = {
            'low': 1.2,
            'moderate': 1.55,
            'high': 1.725
        }
        return int(bmr * activity_multipliers.get(activity_level, 1.55))
    
    def add_measurement(self, user_id: int, **kwargs) -> UserMeasurement:
        """Добавить замер пользователя"""
        measurement = UserMeasurement(user_id=user_id, **kwargs)
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        
        # Обновить текущий вес пользователя
        if measurement.weight:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.weight = measurement.weight
                self.db.commit()
        
        return measurement
    
    def get_measurements_history(self, user_id: int, days: int = 30) -> List[UserMeasurement]:
        """Получить историю замеров"""
        start_date = date.today() - timedelta(days=days)
        return self.db.query(UserMeasurement).filter(
            UserMeasurement.user_id == user_id,
            UserMeasurement.date >= start_date
        ).order_by(UserMeasurement.date.desc()).all()
    
    def get_supplements(self, user_id: int) -> List[Supplement]:
        """Получить добавки пользователя"""
        return self.db.query(Supplement).filter(
            Supplement.user_id == user_id,
            Supplement.is_active == True
        ).all()
    
    def add_supplement(self, user_id: int, **kwargs) -> Supplement:
        """Добавить добавку"""
        supplement = Supplement(user_id=user_id, **kwargs)
        self.db.add(supplement)
        self.db.commit()
        self.db.refresh(supplement)
        return supplement
    
    def update_supplement(self, supplement_id: int, **kwargs) -> Supplement:
        """Обновить добавку"""
        supplement = self.db.query(Supplement).filter(Supplement.id == supplement_id).first()
        if supplement:
            for key, value in kwargs.items():
                if hasattr(supplement, key):
                    setattr(supplement, key, value)
            self.db.commit()
            self.db.refresh(supplement)
        return supplement


class IngredientService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Ingredient]:
        return self.db.query(Ingredient).order_by(Ingredient.name).all()
    
    def get_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        return self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    
    def create(self, **kwargs) -> Ingredient:
        ingredient = Ingredient(**kwargs)
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient
    
    def update(self, ingredient_id: int, **kwargs) -> Optional[Ingredient]:
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if ingredient:
            for key, value in kwargs.items():
                if hasattr(ingredient, key):
                    setattr(ingredient, key, value)
            self.db.commit()
            self.db.refresh(ingredient)
        return ingredient
    
    def delete(self, ingredient_id: int) -> bool:
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if ingredient:
            self.db.delete(ingredient)
            self.db.commit()
            return True
        return False
    
    def search(self, query: str) -> List[Ingredient]:
        return self.db.query(Ingredient).filter(
            Ingredient.name.ilike(f"%{query}%")
        ).limit(20).all()


class RecipeService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Recipe]:
        return self.db.query(Recipe).order_by(Recipe.name).all()
    
    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    def create(self, ingredients_data: List[Dict] = None, **kwargs) -> Recipe:
        recipe = Recipe(**kwargs)
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        
        if ingredients_data:
            for ing_data in ingredients_data:
                recipe_ing = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ing_data['ingredient_id'],
                    quantity=ing_data['quantity']
                )
                self.db.add(recipe_ing)
            self.db.commit()
        
        return recipe
    
    def update(self, recipe_id: int, ingredients_data: List[Dict] = None, **kwargs) -> Optional[Recipe]:
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            for key, value in kwargs.items():
                if hasattr(recipe, key):
                    setattr(recipe, key, value)
            
            # Обновить ингредиенты
            if ingredients_data is not None:
                # Удалить старые ингредиенты
                self.db.query(RecipeIngredient).filter(
                    RecipeIngredient.recipe_id == recipe_id
                ).delete()
                
                # Добавить новые
                for ing_data in ingredients_data:
                    recipe_ing = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ing_data['ingredient_id'],
                        quantity=ing_data['quantity']
                    )
                    self.db.add(recipe_ing)
            
            self.db.commit()
            self.db.refresh(recipe)
        return recipe
    
    def delete(self, recipe_id: int) -> bool:
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            self.db.delete(recipe)
            self.db.commit()
            return True
        return False


class MealPlanService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_day_plan(self, target_date: date) -> Dict[str, Any]:
        """Получить план питания на день"""
        meal_types = ['breakfast', 'second_breakfast', 'lunch', 'snack', 'dinner', 'second_snack']
        day_plan = {}
        
        for meal_type in meal_types:
            meal_plan = self.db.query(MealPlan).filter(
                MealPlan.date == target_date,
                MealPlan.meal_type == meal_type
            ).first()
            
            if meal_plan:
                recipes = []
                for mp_recipe in meal_plan.recipes:
                    recipes.append({
                        'id': mp_recipe.recipe.id,
                        'name': mp_recipe.recipe.name,
                        'servings': mp_recipe.servings,
                        'calories': mp_recipe.total_calories,
                        'protein': mp_recipe.total_protein,
                        'fat': mp_recipe.total_fat,
                        'carbs': mp_recipe.total_carbs,
                        'cost': mp_recipe.total_cost,
                        'photo_path': mp_recipe.recipe.photo_path
                    })
                
                day_plan[meal_type] = {
                    'id': meal_plan.id,
                    'recipes': recipes,
                    'notes': meal_plan.notes
                }
            else:
                day_plan[meal_type] = {'id': None, 'recipes': [], 'notes': None}
        
        # Подсчет итогов за день
        total_calories = sum(
            r['calories'] for meal in day_plan.values() for r in meal['recipes']
        )
        total_protein = sum(
            r['protein'] for meal in day_plan.values() for r in meal['recipes']
        )
        total_fat = sum(
            r['fat'] for meal in day_plan.values() for r in meal['recipes']
        )
        total_carbs = sum(
            r['carbs'] for meal in day_plan.values() for r in meal['recipes']
        )
        total_cost = sum(
            r['cost'] for meal in day_plan.values() for r in meal['recipes']
        )
        
        day_plan['_totals'] = {
            'calories': total_calories,
            'protein': total_protein,
            'fat': total_fat,
            'carbs': total_carbs,
            'cost': total_cost
        }
        
        return day_plan
    
    def get_week_plan(self, start_date: date = None) -> Dict[date, Dict]:
        """Получить план питания на неделю"""
        if start_date is None:
            # Начало недели (понедельник)
            start_date = date.today() - timedelta(days=date.today().weekday())
        
        week_plan = {}
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            week_plan[current_date] = self.get_day_plan(current_date)
        
        return week_plan
    
    def get_month_plan(self, year: int = None, month: int = None) -> Dict[date, Dict]:
        """Получить план питания на месяц"""
        if year is None or month is None:
            today = date.today()
            year = today.year
            month = today.month
        
        # Первый день месяца
        start_date = date(year, month, 1)
        # Последний день месяца
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        month_plan = {}
        current_date = start_date
        while current_date <= end_date:
            month_plan[current_date] = self.get_day_plan(current_date)
            current_date += timedelta(days=1)
        
        return month_plan
    
    def add_recipe_to_meal(self, meal_plan_id: int, recipe_id: int, servings: float = 1) -> MealPlanRecipe:
        """Добавить рецепт в прием пищи"""
        mp_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan_id,
            recipe_id=recipe_id,
            servings=servings
        )
        self.db.add(mp_recipe)
        self.db.commit()
        self.db.refresh(mp_recipe)
        return mp_recipe
    
    def remove_recipe_from_meal(self, meal_plan_recipe_id: int) -> bool:
        """Удалить рецепт из приема пищи"""
        mp_recipe = self.db.query(MealPlanRecipe).filter(
            MealPlanRecipe.id == meal_plan_recipe_id
        ).first()
        if mp_recipe:
            self.db.delete(mp_recipe)
            self.db.commit()
            return True
        return False
    
    def create_or_get_meal_plan(self, target_date: date, meal_type: str) -> MealPlan:
        """Создать или получить план приема пищи"""
        meal_plan = self.db.query(MealPlan).filter(
            MealPlan.date == target_date,
            MealPlan.meal_type == meal_type
        ).first()
        
        if not meal_plan:
            meal_plan = MealPlan(date=target_date, meal_type=meal_type)
            self.db.add(meal_plan)
            self.db.commit()
            self.db.refresh(meal_plan)
        
        return meal_plan
    
    def update_meal_notes(self, meal_plan_id: int, notes: str) -> Optional[MealPlan]:
        """Обновить заметки к приему пищи"""
        meal_plan = self.db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if meal_plan:
            meal_plan.notes = notes
            self.db.commit()
            self.db.refresh(meal_plan)
        return meal_plan


class ShoppingListService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_from_week_plan(self, start_date: date = None) -> List[Dict]:
        """Сгенерировать список покупок из плана на неделю"""
        meal_plan_service = MealPlanService(self.db)
        week_plan = meal_plan_service.get_week_plan(start_date)
        
        # Словарь для агрегации ингредиентов
        ingredient_totals = {}
        
        for day_date, day_plan in week_plan.items():
            for meal_type, meal_data in day_plan.items():
                if meal_type == '_totals':
                    continue
                
                for recipe in meal_data.get('recipes', []):
                    # Получаем рецепт с ингредиентами
                    recipe_obj = self.db.query(Recipe).filter(Recipe.id == recipe['id']).first()
                    if recipe_obj:
                        for recipe_ing in recipe_obj.ingredients:
                            ing_id = recipe_ing.ingredient_id
                            if ing_id not in ingredient_totals:
                                ingredient = recipe_ing.ingredient
                                ingredient_totals[ing_id] = {
                                    'id': ing_id,
                                    'name': ingredient.name,
                                    'quantity': 0,
                                    'unit': ingredient.unit,
                                    'cost': 0
                                }
                            
                            # Добавляем количество с учетом порций
                            quantity_needed = recipe_ing.quantity * (recipe['servings'] / recipe_obj.servings)
                            ingredient_totals[ing_id]['quantity'] += quantity_needed
                            ingredient_totals[ing_id]['cost'] += recipe_ing.ingredient.price_per_unit * quantity_needed
        
        # Преобразуем в список
        shopping_list = list(ingredient_totals.values())
        shopping_list.sort(key=lambda x: x['name'])
        
        return shopping_list
    
    def export_to_telegram(self, shopping_list: List[Dict]) -> str:
        """Экспортировать список покупок в формат для Telegram"""
        message = "🛒 *Список покупок*\n\n"
        total_cost = 0
        
        for item in shopping_list:
            quantity = f"{item['quantity']:.0f}" if item['quantity'] == int(item['quantity']) else f"{item['quantity']:.1f}"
            cost = item['cost']
            total_cost += cost
            message += f"• {item['name']}: {quantity}{item['unit']} - {cost:.2f}₽\n"
        
        message += f"\n💰 *Итого: {total_cost:.2f}₽*"
        
        return message
    
    def clear_list(self) -> bool:
        """Очистить список покупок"""
        self.db.query(ShoppingListItem).delete()
        self.db.commit()
        return True
    
    def add_item(self, ingredient_id: int, quantity: float, note: str = None) -> ShoppingListItem:
        """Добавить item в список покупок"""
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if ingredient:
            item = ShoppingListItem(
                ingredient_id=ingredient_id,
                quantity=quantity,
                unit=ingredient.unit,
                estimated_cost=ingredient.price_per_unit * quantity,
                note=note
            )
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        return None
