'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'

export default function Home() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const isDarkMode = localStorage.getItem('darkMode') === 'true'
    setIsDark(isDarkMode)
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleTheme = () => {
    const newMode = !isDark
    setIsDark(newMode)
    localStorage.setItem('darkMode', String(newMode))
    document.documentElement.classList.toggle('dark')
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-dark-bg dark:to-dark-card">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            🐍 PyLearn
          </div>
          <div className="flex gap-4 items-center">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-border"
            >
              {isDark ? '☀️' : '🌙'}
            </button>
            <Link
              href="/login"
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-primary-600"
            >
              Войти
            </Link>
            <Link
              href="/register"
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              Регистрация
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 text-gray-900 dark:text-white">
          Изучай Python{' '}
          <span className="text-primary-600 dark:text-primary-400">интерактивно</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          Современная образовательная платформа с 200+ уроками, практикой в браузере 
          и системой достижений
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/register"
            className="px-8 py-4 bg-primary-600 text-white text-lg rounded-xl hover:bg-primary-700 transition shadow-lg"
          >
            Начать бесплатно
          </Link>
          <Link
            href="/lessons"
            className="px-8 py-4 border-2 border-primary-600 text-primary-600 dark:text-primary-400 text-lg rounded-xl hover:bg-primary-50 dark:hover:bg-dark-card transition"
          >
            Смотреть уроки
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
          Почему PyLearn?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-6 bg-white dark:bg-dark-card rounded-xl shadow-lg">
            <div className="text-4xl mb-4">💻</div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">Онлайн-редактор</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Пишите и запускайте код прямо в браузере без установки Python
            </p>
          </div>
          <div className="p-6 bg-white dark:bg-dark-card rounded-xl shadow-lg">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">200+ уроков</h3>
            <p className="text-gray-600 dark:text-gray-400">
              От основ до продвинутых тем: ООП, асинхронность, API, базы данных
            </p>
          </div>
          <div className="p-6 bg-white dark:bg-dark-card rounded-xl shadow-lg">
            <div className="text-4xl mb-4">🏆</div>
            <h3 className="text-xl font-semibold mb-2 dark:text-white">Геймификация</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Получайте достижения, отслеживайте серии дней и прогресс
            </p>
          </div>
        </div>
      </section>

      {/* Course Modules Preview */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
          Программа курса
        </h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { icon: '🐍', title: 'Основы Python' },
            { icon: '📊', title: 'Типы данных' },
            { icon: '🔁', title: 'Циклы и условия' },
            { icon: '⚙️', title: 'Функции' },
            { icon: '📁', title: 'Работа с файлами' },
            { icon: '🏗️', title: 'ООП' },
            { icon: '⚠️', title: 'Исключения' },
            { icon: '📦', title: 'Модули' },
            { icon: '🌐', title: 'API' },
            { icon: '🗄️', title: 'Базы данных' },
            { icon: '⚡', title: 'Асинхронность' },
            { icon: '🚀', title: 'Проекты' },
          ].map((module, index) => (
            <div
              key={index}
              className="p-4 bg-white dark:bg-dark-card rounded-lg shadow hover:shadow-md transition text-center"
            >
              <div className="text-3xl mb-2">{module.icon}</div>
              <div className="font-medium dark:text-white">{module.title}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 border-t dark:border-dark-border">
        <div className="text-center text-gray-600 dark:text-gray-400">
          © 2024 PyLearn Platform. Все права защищены.
        </div>
      </footer>
    </main>
  )
}
