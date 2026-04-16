"""
Telegram Bot integration for Nutrition Planner.
Provides bot commands for meal planning, recipe management, and shopping lists.
"""

import asyncio
from datetime import date, timedelta
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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


class NutritionBot:
    """Telegram bot for Nutrition Planner."""
    
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.db: Optional[Session] = None
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup bot command handlers."""
        
        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            """Handle /start command."""
            await message.answer(
                "👋 Привет! Я ваш помощник по планированию питания.\n\n"
                "📋 Доступные команды:\n"
                "/menu - Показать меню на сегодня\n"
                "/week - Показать план на неделю\n"
                "/recipes - Список рецептов\n"
                "/add_recipe - Добавить рецепт в меню\n"
                "/shopping - Список покупок\n"
                "/ingredients - Ингредиенты\n"
                "/help - Помощь"
            )
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            """Handle /help command."""
            await message.answer(
                "📖 Помощь по использованию бота:\n\n"
                "1️⃣ **Планирование питания**\n"
                "   Используйте /add_recipe чтобы добавить рецепт в меню\n"
                "   \n"
                "2️⃣ **Просмотр меню**\n"
                "   /menu - меню на сегодня\n"
                "   /week - план на неделю\n"
                "   \n"
                "3️⃣ **Рецепты**\n"
                "   /recipes - просмотр всех рецептов\n"
                "   \n"
                "4️⃣ **Покупки**\n"
                "   /shopping - список покупок на неделю\n"
                "   \n"
                "Типы приемов пищи:\n"
                "🌅 breakfast - Завтрак\n"
                "☕ second_breakfast - Второй завтрак\n"
                "🍲 lunch - Обед\n"
                "🥜 snack - Перекус\n"
                "🌙 dinner - Ужин\n"
                "🍵 second_snack - Второй перекус"
            )
        
        @self.dp.message(Command("menu"))
        async def cmd_menu(message: types.Message):
            """Show today's meal plan."""
            self.db = init_db()
            try:
                service = MealPlanService(self.db)
                today = date.today()
                
                meals = service.get_meals_by_type(today)
                nutrition = service.calculate_daily_nutrition(today)
                
                meal_names_ru = {
                    'breakfast': '🌅 Завтрак',
                    'second_breakfast': '☕ Второй завтрак',
                    'lunch': '🍲 Обед',
                    'snack': '🥜 Перекус',
                    'dinner': '🌙 Ужин',
                    'second_snack': '🍵 Второй перекус'
                }
                
                response = f"📅 Меню на {today.strftime('%d.%m.%Y')}\n\n"
                
                has_meals = False
                for meal_type, recipes in meals.items():
                    if recipes:
                        has_meals = True
                        response += f"{meal_names_ru.get(meal_type, meal_type)}:\n"
                        for recipe in recipes:
                            response += f"  • {recipe['name']}\n"
                            n = recipe['nutrition']
                            response += f"    КБЖУ: {n['calories']:.0f} ккал, "
                            response += f"Б: {n['protein']:.1f}г, "
                            response += f"Ж: {n['fat']:.1f}г, "
                            response += f"У: {n['carbohydrates']:.1f}г\n"
                            response += f"    Цена: {n['price']:.2f}₽\n"
                        response += "\n"
                
                if not has_meals:
                    response += "Меню на сегодня пустое.\n"
                    response += "Используйте /add_recipe чтобы добавить блюда.\n"
                else:
                    daily = nutrition['daily_total']
                    response += f"\n💰 Итого за день:\n"
                    response += f"Калории: {daily['calories']:.0f} ккал\n"
                    response += f"Белки: {daily['protein']:.1f}г\n"
                    response += f"Жиры: {daily['fat']:.1f}г\n"
                    response += f"Углеводы: {daily['carbohydrates']:.1f}г\n"
                    response += f"Стоимость: {daily['price']:.2f}₽\n"
                
                await message.answer(response)
            finally:
                if self.db:
                    self.db.close()
        
        @self.dp.message(Command("week"))
        async def cmd_week(message: types.Message):
            """Show weekly meal plan."""
            self.db = init_db()
            try:
                service = MealPlanService(self.db)
                today = date.today()
                # Get Monday of current week
                start_of_week = today - timedelta(days=today.weekday())
                
                weekly_plans = service.get_weekly_meal_plan(start_of_week)
                
                response = f"📅 План питания на неделю\n"
                response += f"({start_of_week.strftime('%d.%m')} - "
                response += f"{(start_of_week + timedelta(days=6)).strftime('%d.%m.%Y')})\n\n"
                
                if not weekly_plans:
                    response += "План на неделю пустой.\n"
                else:
                    current_date = start_of_week
                    for i in range(7):
                        day_name = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][i]
                        response += f"*{day_name} {current_date.strftime('%d.%m')}*\n"
                        
                        if current_date in weekly_plans:
                            meals = service.get_meals_by_type(current_date)
                            meal_count = sum(len(recipes) for recipes in meals.values())
                            response += f"  Приемов пищи: {meal_count}\n"
                            
                            nutrition = service.calculate_daily_nutrition(current_date)
                            daily = nutrition['daily_total']
                            response += f"  Ккал: {daily['calories']:.0f}, "
                            response += f"Цена: {daily['price']:.2f}₽\n"
                        else:
                            response += "  Нет плана\n"
                        
                        response += "\n"
                        current_date += timedelta(days=1)
                
                await message.answer(response, parse_mode="Markdown")
            finally:
                if self.db:
                    self.db.close()
        
        @self.dp.message(Command("recipes"))
        async def cmd_recipes(message: types.Message):
            """Show all recipes."""
            self.db = init_db()
            try:
                service = RecipeService(self.db)
                recipes = service.get_all_recipes()
                
                if not recipes:
                    await message.answer(
                        "📚 База рецептов пуста.\n"
                        "Добавьте рецепты через веб-интерфейс или API."
                    )
                    return
                
                response = "📚 Рецепты:\n\n"
                for i, recipe in enumerate(recipes[:10], 1):  # Show first 10
                    nutrition = service.calculate_recipe_nutrition(recipe.id)
                    response += f"{i}. *{recipe.name}*\n"
                    response += f"   Ккал: {nutrition.get('calories', 0):.0f}\n"
                    response += f"   Б: {nutrition.get('protein', 0):.1f}г, "
                    response += f"Ж: {nutrition.get('fat', 0):.1f}г, "
                    response += f"У: {nutrition.get('carbohydrates', 0):.1f}г\n"
                    response += f"   Цена: {nutrition.get('price', 0):.2f}₽\n\n"
                
                if len(recipes) > 10:
                    response += f"... и еще {len(recipes) - 10} рецептов\n"
                
                await message.answer(response, parse_mode="Markdown")
            finally:
                if self.db:
                    self.db.close()
        
        @self.dp.message(Command("shopping"))
        async def cmd_shopping(message: types.Message):
            """Generate and show shopping list."""
            self.db = init_db()
            try:
                service = ShoppingListService(self.db)
                today = date.today()
                # Get Monday of current week
                start_of_week = today - timedelta(days=today.weekday())
                
                shopping_list = service.generate_shopping_list_from_week(start_of_week)
                
                if not shopping_list:
                    await message.answer(
                        "🛒 Список покупок пуст.\n"
                        "Сначала составьте план питания на неделю."
                    )
                    return
                
                response = "🛒 Список покупок на неделю:\n\n"
                total_price = 0
                
                for item in shopping_list:
                    response += f"• {item['name']}\n"
                    response += f"  Количество: {item['quantity_needed']:.0f}{item['unit']}\n"
                    response += f"  Цена: {item['estimated_price']:.2f}₽\n\n"
                    total_price += item['estimated_price']
                
                response += f"\n💰 Общая стоимость: {total_price:.2f}₽\n"
                
                await message.answer(response)
            finally:
                if self.db:
                    self.db.close()
        
        @self.dp.message(Command("ingredients"))
        async def cmd_ingredients(message: types.Message):
            """Show all ingredients."""
            self.db = init_db()
            try:
                service = IngredientService(self.db)
                ingredients = service.get_all_ingredients()
                
                if not ingredients:
                    await message.answer(
                        "🥗 База ингредиентов пуста.\n"
                        "Добавьте ингредиенты через веб-интерфейс или API."
                    )
                    return
                
                response = "🥗 Ингредиенты (первые 20):\n\n"
                for i, ing in enumerate(ingredients[:20], 1):
                    response += f"{i}. {ing.name}\n"
                    response += f"   Ккал: {ing.calories:.0f}, "
                    response += f"Б: {ing.protein:.1f}г, "
                    response += f"Ж: {ing.fat:.1f}г, "
                    response += f"У: {ing.carbohydrates:.1f}г\n"
                    response += f"   Цена: {ing.price_per_100g:.2f}₽/100г\n\n"
                
                if len(ingredients) > 20:
                    response += f"... и еще {len(ingredients) - 20} ингредиентов\n"
                
                await message.answer(response)
            finally:
                if self.db:
                    self.db.close()
        
        @self.dp.message(Command("add_recipe"))
        async def cmd_add_recipe(message: types.Message):
            """Guide user to add recipe to meal plan."""
            await message.answer(
                "➕ Чтобы добавить рецепт в меню, используйте API или веб-интерфейс.\n\n"
                "Пример через API:\n"
                "POST /meal-plans/{date}/\n"
                "{\n"
                '  "recipe_id": 1,\n'
                '  "meal_type": "breakfast"\n'
                "}\n\n"
                "Типы приемов пищи:\n"
                "- breakfast\n"
                "- second_breakfast\n"
                "- lunch\n"
                "- snack\n"
                "- dinner\n"
                "- second_snack"
            )
    
    async def start_polling(self):
        """Start bot polling."""
        print("🤖 Telegram bot started...")
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Stop the bot."""
        await self.bot.close()
        if self.db:
            self.db.close()


async def run_bot(token: str):
    """Run the Telegram bot."""
    bot = NutritionBot(token)
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        await bot.stop()


if __name__ == "__main__":
    # Example usage (replace with your actual token)
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    asyncio.run(run_bot(BOT_TOKEN))
