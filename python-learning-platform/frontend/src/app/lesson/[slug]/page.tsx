'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import { Play, CheckCircle, XCircle, ChevronLeft, BookOpen, Code } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import { marked } from 'marked';

export default function LessonPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [lesson, setLesson] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('# Напишите ваш код здесь\nprint("Hello, Python!")');
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [executing, setExecuting] = useState(false);
  const [activeTab, setActiveTab] = useState<'theory' | 'practice'>('theory');

  useEffect(() => {
    fetchLesson();
  }, [slug]);

  const fetchLesson = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.get(`/api/v1/lessons/slug/${slug}`, { headers });
      setLesson(response.data);
      
      if (response.data.tasks && response.data.tasks.length > 0) {
        setCode(response.data.tasks[0].starter_code || '# Ваш код здесь\n');
      }
    } catch (err) {
      toast.error('Ошибка загрузки урока');
    } finally {
      setLoading(false);
    }
  };

  const runCode = async () => {
    setExecuting(true);
    setOutput('');
    setError('');

    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const response = await axios.post(
        '/api/v1/code/execute',
        { code, timeout: 10 },
        { headers }
      );

      setOutput(response.data.output || '');
      if (response.data.error) {
        setError(response.data.error);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка выполнения кода');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Урок не найден</h1>
          <Link href="/lessons" className="text-indigo-600 hover:text-indigo-500">
            ← Вернуться к урокам
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Toaster position="top-center" />

      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/lessons"
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <ChevronLeft className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {lesson.title}
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  ~{lesson.estimated_time} мин • {lesson.difficulty === 'beginner' ? 'Начальный' : lesson.difficulty === 'intermediate' ? 'Средний' : 'Продвинутый'} уровень
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveTab('theory')}
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                  activeTab === 'theory'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>Теория</span>
              </button>
              <button
                onClick={() => setActiveTab('practice')}
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                  activeTab === 'practice'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <Code className="w-4 h-4" />
                <span>Практика</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'theory' ? (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
            <div
              className="prose dark:prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: marked(lesson.content) }}
            />
            
            {lesson.is_completed && (
              <div className="mt-6 p-4 bg-green-100 dark:bg-green-900 rounded-lg flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <span className="text-green-800 dark:text-green-200 font-medium">
                  Урок завершён! +{lesson.xp_reward} XP
                </span>
              </div>
            )}
          </div>
        ) : (
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Editor */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900 dark:text-white">Редактор кода</h3>
                <button
                  onClick={runCode}
                  disabled={executing}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  <span>{executing ? 'Выполнение...' : 'Запустить'}</span>
                </button>
              </div>
              <Editor
                height="400px"
                language="python"
                theme="vs-dark"
                value={code}
                onChange={(value) => setCode(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
              {lesson.tasks && lesson.tasks.length > 0 && (
                <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                    Задание: {lesson.tasks[0].title}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {lesson.tasks[0].description}
                  </p>
                </div>
              )}
            </div>

            {/* Output */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-white">Результат</h3>
              </div>
              <div className="p-4 h-[400px] overflow-auto">
                {output && (
                  <div className="mb-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-medium text-gray-900 dark:text-white">Вывод:</span>
                    </div>
                    <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                      {output}
                    </pre>
                  </div>
                )}
                {error && (
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <XCircle className="w-5 h-5 text-red-600" />
                      <span className="font-medium text-gray-900 dark:text-white">Ошибка:</span>
                    </div>
                    <pre className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg text-sm text-red-800 dark:text-red-300 whitespace-pre-wrap">
                      {error}
                    </pre>
                  </div>
                )}
                {!output && !error && (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-20">
                    Нажмите «Запустить» чтобы выполнить код
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
