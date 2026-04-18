import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
}

interface DashboardStats {
  total_lessons: number;
  completed_lessons: number;
  completion_percentage: number;
  total_tasks: number;
  completed_tasks: number;
  current_streak: number;
  longest_streak: number;
  total_achievements: number;
  total_submissions: number;
}

interface AppState {
  user: User | null;
  stats: DashboardStats | null;
  isDark: boolean;
  language: 'ru' | 'en';
  setUser: (user: User | null) => void;
  setStats: (stats: DashboardStats | null) => void;
  toggleTheme: () => void;
  setLanguage: (lang: 'ru' | 'en') => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  stats: null,
  isDark: false,
  language: 'ru',
  
  setUser: (user) => set({ user }),
  setStats: (stats) => set({ stats }),
  toggleTheme: () => set((state) => {
    const newIsDark = !state.isDark;
    localStorage.setItem('darkMode', String(newIsDark));
    document.documentElement.classList.toggle('dark');
    return { isDark: newIsDark };
  }),
  setLanguage: (language) => set({ language }),
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, stats: null });
  },
}));
