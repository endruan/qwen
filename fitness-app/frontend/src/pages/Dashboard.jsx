import React, { useState, useEffect } from 'react';
import { authAPI, nutritionAPI } from '../services/api';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Dashboard = ({ user }) => {
  const [goals, setGoals] = useState(null);
  const [nutrition, setNutrition] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [goalsRes, nutritionRes, metricsRes] = await Promise.all([
        authAPI.getGoals(),
        nutritionAPI.getDailyNutrition(new Date().toISOString().split('T')[0]),
        authAPI.getMetrics()
      ]);
      
      setGoals(goalsRes.data);
      setNutrition(nutritionRes.data);
      setMetrics(metricsRes.data.slice(0, 7));
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const macrosData = nutrition ? [
    { name: 'Белки', value: nutrition.total_protein, goal: goals?.protein || 0, color: '#3B82F6' },
    { name: 'Жиры', value: nutrition.total_fat, goal: goals?.fat || 0, color: '#F59E0B' },
    { name: 'Углеводы', value: nutrition.total_carbs, goal: goals?.carbs || 0, color: '#10B981' },
  ] : [];

  const weightData = metrics.map(m => ({
    date: new Date(m.date).toLocaleDateString('ru-RU'),
    weight: m.weight
  })).reverse();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Дашборд</h1>
      
      {/* Goals Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500">Калории</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {nutrition?.total_kcal?.toFixed(0) || 0} / {goals?.calories || 0}
          </p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${Math.min((nutrition?.total_kcal / goals?.calories) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500">Белки</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {nutrition?.total_protein?.toFixed(0) || 0} / {goals?.protein || 0}г
          </p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: `${Math.min((nutrition?.total_protein / goals?.protein) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500">Жиры</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {nutrition?.total_fat?.toFixed(0) || 0} / {goals?.fat || 0}г
          </p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-yellow-500 h-2 rounded-full"
              style={{ width: `${Math.min((nutrition?.total_fat / goals?.fat) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500">Углеводы</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {nutrition?.total_carbs?.toFixed(0) || 0} / {goals?.carbs || 0}г
          </p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${Math.min((nutrition?.total_carbs / goals?.carbs) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weight Progress */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Динамика веса</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weightData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="weight" stroke="#3B82F6" strokeWidth={2} name="Вес (кг)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Macros Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Распределение макронутриентов</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={macrosData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" name="Потреблено" />
              <Bar dataKey="goal" fill="#82ca9d" name="Цель" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* User Info */}
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Профиль</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500">Рост</p>
            <p className="text-lg font-medium">{user?.height || '-'} см</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Вес</p>
            <p className="text-lg font-medium">{user?.weight || '-'} кг</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Возраст</p>
            <p className="text-lg font-medium">{user?.age || '-'} лет</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Цель</p>
            <p className="text-lg font-medium capitalize">{user?.goal || '-'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
