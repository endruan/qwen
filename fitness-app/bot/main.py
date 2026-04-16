import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO)

API_URL = "http://localhost:8000/api"
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_main_keyboard():
    keyboard = [
        [KeyboardButton(text="📅 Меню на сегодня"), KeyboardButton(text="🛒 Список покупок")],
        [KeyboardButton(text="🏋️ Тренировка"), KeyboardButton(text="⚖️ Записать вес")],
        [KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я ваш помощник для управления питанием и тренировками.\n\n"
        "Используйте кнопки ниже или команды:",
        reply_markup=get_main_keyboard()
    )


@dp.message(Command("menu"))
@dp.message(F.text == "📅 Меню на сегодня")
async def show_menu(message: types.Message):
    """Show today's meal plan"""
    telegram_id = str(message.from_user.id)
    
    async with ClientSession() as session:
        try:
            # Get user by telegram_id (you'll need to implement this endpoint)
            async with session.get(f"{API_URL}/users/by-telegram/{telegram_id}") as resp:
                if resp.status != 200:
                    await message.answer("❌ Сначала авторизуйтесь в приложении")
                    return
                
                user_data = await resp.json()
                user_id = user_data["id"]
            
            # Get meal plans for today
            from datetime import date
            today = date.today().isoformat()
            
            async with session.get(f"{API_URL}/nutrition/meal-plans?start_date={today}&end_date={today}") as resp:
                if resp.status == 200:
                    meal_plans = await resp.json()
                    
                    if not meal_plans:
                        await message.answer("📅 На сегодня нет запланированных приемов пищи")
                        return
                    
                    response_text = "📅 **Меню на сегодня:**\n\n"
                    for meal in meal_plans:
                        emoji = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}
                        meal_type = meal.get("meal_type", "meal")
                        recipe_name = meal.get("recipe", {}).get("name", "Unknown")
                        kcal = meal.get("recipe", {}).get("total_kcal", 0)
                        
                        response_text += f"{emoji.get(meal_type, '🍽')} *{meal_type.capitalize()}:*\n"
                        response_text += f"  {recipe_name}\n"
                        response_text += f"  📊 {kcal} ккал\n\n"
                    
                    await message.answer(response_text, parse_mode="Markdown")
                else:
                    await message.answer("❌ Ошибка получения меню")
        
        except Exception as e:
            logging.error(f"Error in show_menu: {e}")
            await message.answer("❌ Ошибка подключения к серверу")


@dp.message(Command("shopping"))
@dp.message(F.text == "🛒 Список покупок")
async def show_shopping_list(message: types.Message):
    """Show shopping list"""
    telegram_id = str(message.from_user.id)
    
    async with ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/users/by-telegram/{telegram_id}") as resp:
                if resp.status != 200:
                    await message.answer("❌ Сначала авторизуйтесь в приложении")
                    return
                
                user_data = await resp.json()
                user_id = user_data["id"]
            
            async with session.get(f"{API_URL}/nutrition/shopping-list") as resp:
                if resp.status == 200:
                    items = await resp.json()
                    
                    if not items:
                        await message.answer("🛒 Список покупок пуст")
                        return
                    
                    response_text = "🛒 **Список покупок:**\n\n"
                    total_cost = 0
                    
                    for item in items:
                        ingredient = item.get("ingredient", {})
                        name = ingredient.get("name", "Unknown")
                        quantity = item.get("quantity", 0)
                        unit = ingredient.get("unit_type", "г")
                        purchased = "✅" if item.get("purchased") else "⬜"
                        
                        price_per_unit = ingredient.get("price_per_unit", 0)
                        cost = price_per_unit * quantity
                        total_cost += cost
                        
                        response_text += f"{purchased} {name}: {quantity:.0f}{unit} - {cost:.2f}₽\n"
                    
                    response_text += f"\n💰 **Итого: {total_cost:.2f}₽**"
                    
                    await message.answer(response_text, parse_mode="Markdown")
                else:
                    await message.answer("❌ Ошибка получения списка покупок")
        
        except Exception as e:
            logging.error(f"Error in show_shopping_list: {e}")
            await message.answer("❌ Ошибка подключения к серверу")


@dp.message(Command("workout"))
@dp.message(F.text == "🏋️ Тренировка")
async def show_workout(message: types.Message):
    """Show today's workout"""
    telegram_id = str(message.from_user.id)
    
    async with ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/users/by-telegram/{telegram_id}") as resp:
                if resp.status != 200:
                    await message.answer("❌ Сначала авторизуйтесь в приложении")
                    return
                
                user_data = await resp.json()
            
            from datetime import date
            today = date.today().isoformat()
            
            async with session.get(f"{API_URL}/workouts") as resp:
                if resp.status == 200:
                    workouts = await resp.json()
                    
                    # Filter today's workout
                    today_workout = None
                    for workout in workouts:
                        if workout.get("date") == today:
                            today_workout = workout
                            break
                    
                    if not today_workout:
                        await message.answer("🏋️ На сегодня нет запланированной тренировки")
                        return
                    
                    response_text = f"🏋️ **Тренировка на {today}:**\n\n"
                    
                    if today_workout.get("notes"):
                        response_text += f"📝 {today_workout['notes']}\n\n"
                    
                    exercises = today_workout.get("exercises", [])
                    for ex in exercises:
                        exercise_name = ex.get("exercise", {}).get("name", "Unknown")
                        sets = ex.get("sets", 0)
                        reps = ex.get("reps", 0)
                        weight = ex.get("weight", 0)
                        completed = "✅" if ex.get("completed") else "⬜"
                        
                        response_text += f"{completed} {exercise_name}: {sets}x{reps}"
                        if weight > 0:
                            response_text += f" @ {weight}кг"
                        response_text += "\n"
                    
                    await message.answer(response_text, parse_mode="Markdown")
                else:
                    await message.answer("❌ Ошибка получения тренировки")
        
        except Exception as e:
            logging.error(f"Error in show_workout: {e}")
            await message.answer("❌ Ошибка подключения к серверу")


@dp.message(Command("weight"))
@dp.message(F.text == "⚖️ Записать вес")
async def log_weight(message: types.Message):
    """Prompt to log weight"""
    await message.answer(
        "⚖️ Введите ваш вес в кг (например, 75.5):\n\n"
        "Или используйте команду: /weight 75.5"
    )


@dp.message(Command("help"))
@dp.message(F.text == "❓ Помощь")
async def show_help(message: types.Message):
    """Show help message"""
    help_text = """
🤖 **Бот для управления питанием и тренировками**

📋 **Команды:**
/start - Запустить бота
/menu - Показать меню на сегодня
/shopping - Показать список покупок
/workout - Показать тренировку на сегодня
/weight - Записать вес
/help - Эта справка

💡 **Советы:**
• Планируйте питание на неделю вперед
• Обновляйте список покупок автоматически
• Отмечайте выполненные тренировки

Для работы бота необходимо быть зарегистрированным в приложении.
    """
    await message.answer(help_text, parse_mode="Markdown")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
