'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Book, Code, Trophy, User, Menu, X, Sun, Moon, LogOut } from 'lucide-react';
import axios from 'axios';

export default function Home() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
    
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setIsDarkMode(true);
    }
  }, []);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2">
              <Code className="w-8 h-8 text-indigo-600" />
              <span className="text-xl font-bold text-gray-900 dark:text-white">Python Learning</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/lessons" className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">
                Уроки
              </Link>
              <Link href="/about" className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">
                О платформе
              </Link>
              
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {isLoggedIn ? (
                <div className="flex items-center space-x-4">
                  <Link href="/dashboard" className="text-gray-700 dark:text-gray-300 hover:text-indigo-600">
                    Личный кабинет
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Выйти</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link href="/auth/login" className="text-gray-700 dark:text-gray-300 hover:text-indigo-600">
                    Войти
                  </Link>
                  <Link
                    href="/auth/register"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                  >
                    Регистрация
                  </Link>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-white dark:bg-gray-900 border-t dark:border-gray-800">
            <div className="px-4 py-4 space-y-4">
              <Link href="/lessons" className="block text-gray-700 dark:text-gray-300">Уроки</Link>
              <Link href="/about" className="block text-gray-700 dark:text-gray-300">О платформе</Link>
              {isLoggedIn ? (
                <>
                  <Link href="/dashboard" className="block text-gray-700 dark:text-gray-300">Личный кабинет</Link>
                  <button onClick={handleLogout} className="block text-red-500">Выйти</button>
                </>
              ) : (
                <>
                  <Link href="/auth/login" className="block text-gray-700 dark:text-gray-300">Войти</Link>
                  <Link href="/auth/register" className="block text-indigo-600">Регистрация</Link>
                </>
              )}
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="flex items-center space-x-2 text-gray-700 dark:text-gray-300"
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                <span>{isDarkMode ? 'Светлая тема' : 'Тёмная тема'}</span>
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Изучай Python{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
              интерактивно
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-10 max-w-3xl mx-auto">
            От основ до продвинутого уровня. Практикуйся прямо в браузере, получай мгновенную обратную связь и отслеживай свой прогресс.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={isLoggedIn ? '/lessons' : '/auth/register'}
              className="px-8 py-4 bg-indigo-600 text-white rounded-xl text-lg font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105 shadow-lg"
            >
              Начать обучение бесплатно
            </Link>
            <Link
              href="/lessons"
              className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-xl text-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-all border border-gray-200 dark:border-gray-700"
            >
              Смотреть уроки
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg">
            <Book className="w-12 h-12 text-indigo-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              150+ уроков
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Полная программа от основ Python до продвинутых тем: ООП, асинхронность, базы данных и многое другое.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg">
            <Code className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Практика в браузере
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Пиши и запускай код прямо в браузере. Мгновенная проверка результатов и подсказки.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg">
            <Trophy className="w-12 h-12 text-yellow-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Геймификация
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Получай достижения, поддерживай серии дней, соревнуйся с другими учениками.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-indigo-600 mb-2">150+</div>
            <div className="text-gray-600 dark:text-gray-400">Уроков</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">15</div>
            <div className="text-gray-600 dark:text-gray-400">Разделов</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-yellow-600 mb-2">8</div>
            <div className="text-gray-600 dark:text-gray-400">Достижений</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">∞</div>
            <div className="text-gray-600 dark:text-gray-400">Практики</div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-900 border-t dark:border-gray-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Code className="w-6 h-6 text-indigo-600" />
              <span className="font-semibold text-gray-900 dark:text-white">Python Learning Platform</span>
            </div>
            <div className="text-gray-600 dark:text-gray-400 text-sm">
              © 2024 Python Learning Platform. Все права защищены.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
