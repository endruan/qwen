'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import { Book, ChevronRight, Search, Filter } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

interface Section {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  icon: string;
  lessons_count: number;
}

export default function LessonsPage() {
  const router = useRouter();
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchSections();
  }, []);

  const fetchSections = async () => {
    try {
      const response = await axios.get('/api/v1/sections');
      setSections(response.data);
    } catch (error) {
      toast.error('Ошибка загрузки уроков');
    } finally {
      setLoading(false);
    }
  };

  const filteredSections = sections.filter(section =>
    section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    section.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Toaster position="top-center" />
      
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Уроки</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Изучайте Python шаг за шагом
              </p>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Личный кабинет
            </Link>
          </div>

          {/* Search */}
          <div className="mt-6 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Поиск уроков..."
              className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <div className="space-y-8">
            {filteredSections.map((section) => (
              <div
                key={section.id}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden"
              >
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-indigo-100 dark:bg-indigo-900 rounded-xl">
                      <Book className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                        {section.title}
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        {section.lessons_count} уроков
                      </p>
                    </div>
                  </div>
                  {section.description && (
                    <p className="mt-3 text-gray-600 dark:text-gray-400">
                      {section.description}
                    </p>
                  )}
                </div>

                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {section.lessons && section.lessons.length > 0 ? (
                    section.lessons.map((lesson: any, index: number) => (
                      <Link
                        key={lesson.id}
                        href={`/lesson/${lesson.slug}`}
                        className="block p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-full text-sm font-medium text-gray-600 dark:text-gray-400">
                              {index + 1}
                            </span>
                            <div>
                              <h3 className="font-medium text-gray-900 dark:text-white">
                                {lesson.title}
                              </h3>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                ~{lesson.estimated_time} мин • {lesson.difficulty === 'beginner' ? 'Начальный' : lesson.difficulty === 'intermediate' ? 'Средний' : 'Продвинутый'} уровень
                              </p>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-gray-400" />
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                      Уроки загружаются...
                    </div>
                  )}
                </div>
              </div>
            ))}

            {filteredSections.length === 0 && (
              <div className="text-center py-20">
                <Book className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Ничего не найдено
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Попробуйте изменить поисковый запрос
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
