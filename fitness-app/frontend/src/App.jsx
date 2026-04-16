import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Recipes from './pages/Recipes';
import Ingredients from './pages/Ingredients';
import MealPlan from './pages/MealPlan';
import ShoppingList from './pages/ShoppingList';
import Workouts from './pages/Workouts';
import Profile from './pages/Profile';
import Navbar from './components/Navbar';
import { authAPI } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await authAPI.getMe();
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {isAuthenticated && <Navbar user={user} onLogout={handleLogout} />}
      
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? 
              <Navigate to="/dashboard" /> : 
              <Login onLogin={() => { setIsAuthenticated(true); checkAuth(); }} />
          } 
        />
        <Route 
          path="/register" 
          element={
            isAuthenticated ? 
              <Navigate to="/dashboard" /> : 
              <Register />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            isAuthenticated ? 
              <Dashboard user={user} /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/recipes" 
          element={
            isAuthenticated ? 
              <Recipes /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/ingredients" 
          element={
            isAuthenticated ? 
              <Ingredients /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/meal-plan" 
          element={
            isAuthenticated ? 
              <MealPlan /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/shopping" 
          element={
            isAuthenticated ? 
              <ShoppingList /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/workouts" 
          element={
            isAuthenticated ? 
              <Workouts /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/profile" 
          element={
            isAuthenticated ? 
              <Profile user={user} /> : 
              <Navigate to="/login" />
          } 
        />
        <Route 
          path="/" 
          element={
            <Navigate to={isAuthenticated ? "/dashboard" : "/login"} />
          } 
        />
      </Routes>
    </div>
  );
}

export default App;
