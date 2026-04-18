import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
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

// Response interceptor for handling errors
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

// Auth APIs
export const authAPI = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Modules APIs
export const modulesAPI = {
  getAll: () => api.get('/modules/'),
  getById: (id: number) => api.get(`/modules/${id}`),
};

// Lessons APIs
export const lessonsAPI = {
  getAll: () => api.get('/lessons/'),
  getById: (id: number) => api.get(`/lessons/${id}`),
  getByModule: (moduleId: number) => api.get(`/lessons/module/${moduleId}`),
};

// Tasks APIs
export const tasksAPI = {
  getByLesson: (lessonId: number) => api.get(`/tasks/lesson/${lessonId}`),
  getById: (id: number) => api.get(`/tasks/${id}`),
  execute: (taskId: number, code: string) =>
    api.post(`/tasks/${taskId}/execute`, { code }),
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getProgress: () => api.get('/dashboard/progress'),
  getAchievements: () => api.get('/dashboard/achievements'),
  getAllAchievements: () => api.get('/dashboard/all-achievements'),
};
