# Fitness & Nutrition Management System

## 🏗️ Architecture

```
fitness-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, security
│   │   ├── db/             # Database connection
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── bot/                    # Telegram bot
│   ├── main.py
│   └── requirements.txt
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/fitness_db"
export SECRET_KEY="your-secret-key"
export TELEGRAM_BOT_TOKEN="your-bot-token"

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Telegram Bot Setup

```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 📊 Database Schema

### Users
- id, email, password_hash, telegram_id
- weight, height, age, gender
- activity_level, goal

### UserMetrics
- id, user_id, date
- weight, waist, chest, biceps, hips

### Ingredients
- id, name, kcal_per_100, protein_per_100, fat_per_100, carbs_per_100
- price_per_package, package_quantity, unit_type

### Recipes
- id, name, description, photo_url, servings
- total_kcal, total_protein, total_fat, total_carbs, total_cost

### RecipeIngredients
- id, recipe_id, ingredient_id, quantity

### MealPlans
- id, user_id, date, meal_type
- recipe_id

### ShoppingList
- id, user_id, ingredient_id, quantity, purchased

### Workouts
- id, user_id, date, duration, notes

### Exercises
- id, name, description, photo_url, muscle_group

### WorkoutExercises
- id, workout_id, exercise_id, sets, reps, weight, completed

## 🔧 Key Features Fixed

1. **Ingredient Saving**: Fixed transaction handling in recipe creation
2. **Recipe Creation**: Added proper error handling and validation
3. **Recipe Loading**: Optimized queries with proper joins

## 📱 API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Users
- GET /api/users/profile
- PUT /api/users/profile
- GET /api/users/metrics
- POST /api/users/metrics

### Ingredients
- GET /api/ingredients
- POST /api/ingredients
- PUT /api/ingredients/{id}
- DELETE /api/ingredients/{id}

### Recipes
- GET /api/recipes
- POST /api/recipes
- GET /api/recipes/{id}
- PUT /api/recipes/{id}
- DELETE /api/recipes/{id}

### Meal Plans
- GET /api/meal-plans?start_date=&end_date=
- POST /api/meal-plans
- DELETE /api/meal-plans/{id}

### Shopping List
- GET /api/shopping-list
- POST /api/shopping-list/generate
- PUT /api/shopping-list/{id}/toggle

### Workouts
- GET /api/workouts
- POST /api/workouts
- PUT /api/workouts/{id}

## 🤖 Telegram Bot Commands

- /start - Start bot
- /menu - View today's meal plan
- /shopping - Get shopping list
- /workout - View today's workout
- /weight - Log weight
- /help - Show help
