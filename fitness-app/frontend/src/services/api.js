import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  getGoals: () => api.get('/auth/goals'),
  addMetric: (data) => api.post('/auth/metrics', data),
  getMetrics: () => api.get('/auth/metrics'),
};

export const nutritionAPI = {
  // Ingredients
  getIngredients: () => api.get('/nutrition/ingredients'),
  createIngredient: (data) => api.post('/nutrition/ingredients', data),
  updateIngredient: (id, data) => api.put(`/nutrition/ingredients/${id}`, data),
  deleteIngredient: (id) => api.delete(`/nutrition/ingredients/${id}`),
  
  // Recipes
  getRecipes: () => api.get('/nutrition/recipes'),
  getRecipe: (id) => api.get(`/nutrition/recipes/${id}`),
  createRecipe: (data) => api.post('/nutrition/recipes', data),
  updateRecipe: (id, data) => api.put(`/nutrition/recipes/${id}`, data),
  deleteRecipe: (id) => api.delete(`/nutrition/recipes/${id}`),
  
  // Meal Plans
  getMealPlans: (startDate, endDate) => 
    api.get(`/nutrition/meal-plans?start_date=${startDate}&end_date=${endDate}`),
  createMealPlan: (data) => api.post('/nutrition/meal-plans', data),
  deleteMealPlan: (id) => api.delete(`/nutrition/meal-plans/${id}`),
  
  // Shopping List
  getShoppingList: () => api.get('/nutrition/shopping-list'),
  generateShoppingList: (startDate, endDate) => 
    api.post(`/nutrition/shopping-list/generate?start_date=${startDate}&end_date=${endDate}`),
  toggleShoppingItem: (id) => api.put(`/nutrition/shopping-list/${id}/toggle`),
  
  // Dashboard
  getDailyNutrition: (date) => api.get(`/nutrition/dashboard/nutrition?target_date=${date}`),
};

export const workoutsAPI = {
  getExercises: () => api.get('/workouts/exercises'),
  createExercise: (data) => api.post('/workouts/exercises', data),
  getWorkouts: () => api.get('/workouts'),
  getWorkout: (id) => api.get(`/workouts/${id}`),
  createWorkout: (data) => api.post('/workouts', data),
  updateWorkout: (id, data) => api.put(`/workouts/${id}`, data),
  deleteWorkout: (id) => api.delete(`/workouts/${id}`),
};

export default api;
