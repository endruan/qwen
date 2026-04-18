// Main Application JavaScript

const app = {
    currentUser: null,
    
    init() {
        this.loadUserData();
        this.setupEventListeners();
    },
    
    navigateTo(section) {
        // Hide all sections
        document.querySelectorAll('section').forEach(s => {
            s.classList.remove('active-section');
            s.classList.add('hidden-section');
        });
        
        // Show target section
        const targetSection = document.getElementById(`${section}-section`);
        if (targetSection) {
            targetSection.classList.remove('hidden-section');
            targetSection.classList.add('active-section');
        }
        
        // Load lessons if navigating to lessons
        if (section === 'lessons' && typeof lessonManager !== 'undefined' && lessonManager) {
            lessonManager.renderModules();
        }
        
        // Hide dashboard if navigating away
        if (section !== 'dashboard') {
            const dashboard = document.getElementById('userDashboard');
            if (dashboard) {
                dashboard.style.display = 'none';
            }
        }
    },
    
    setTheme(theme) {
        const body = document.body;
        body.classList.remove('light-theme', 'dark-theme');
        body.classList.add(`${theme}-theme`);
        localStorage.setItem('theme', theme);
    },
    
    loadUserData() {
        const userData = localStorage.getItem('currentUser');
        if (userData) {
            this.currentUser = JSON.parse(userData);
            this.showDashboard(this.currentUser);
        }
    },
    
    showDashboard(user) {
        const dashboard = document.getElementById('userDashboard');
        if (dashboard) {
            dashboard.style.display = 'flex';
        }
        
        // Hide main content initially
        document.querySelectorAll('section').forEach(s => {
            s.classList.remove('active-section');
            s.classList.add('hidden-section');
        });
        
        // Update user info
        const userNameDisplay = document.getElementById('userName');
        if (userNameDisplay) {
            userNameDisplay.textContent = user.username || 'Student';
        }
        
        this.updateDashboard(user);
    },
    
    updateDashboard(user) {
        // Update progress stats
        const completedLessons = user.completedLessons?.length || 0;
        const totalPoints = user.totalPoints || 0;
        const level = Math.floor(totalPoints / 500) + 1;
        
        // Update dashboard values
        const dashXP = document.getElementById('dash-xp');
        const dashLevel = document.getElementById('dash-level');
        const dashCompleted = document.getElementById('dash-completed');
        
        if (dashXP) dashXP.textContent = totalPoints;
        if (dashLevel) dashLevel.textContent = level;
        if (dashCompleted) {
            const totalLessons = 18;
            const percentage = Math.round((completedLessons / totalLessons) * 100);
            dashCompleted.textContent = `${percentage}%`;
        }
        
        // Update progress bars
        const progressBars = document.querySelectorAll('.progress-fill');
        if (progressBars.length >= 3) {
            progressBars[0].style.width = `${(completedLessons / 18) * 100}%`;
            const progressValue = progressBars[0].previousElementSibling?.querySelector('.progress-value');
            if (progressValue) progressValue.textContent = `${completedLessons}/18`;
            
            progressBars[2].style.width = `${Math.min((totalPoints / 1000) * 100, 100)}%`;
            const pointsValue = progressBars[2].previousElementSibling?.querySelector('.progress-value');
            if (pointsValue) pointsValue.textContent = `${totalPoints} XP`;
        }
    },
    
    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const body = document.body;
                const isDark = body.classList.contains('dark-theme');
                this.setTheme(isDark ? 'light' : 'dark');
            });
        }
        
        // Language toggle
        const langToggle = document.getElementById('langToggle');
        if (langToggle) {
            langToggle.addEventListener('click', () => {
                const newLang = currentLang === 'ru' ? 'en' : 'ru';
                updateLanguage(newLang);
                const langBtn = document.querySelector('.lang-icon');
                if (langBtn) {
                    langBtn.textContent = newLang === 'ru' ? 'EN' : 'RU';
                }
            });
        }
        
        // Login button
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                document.getElementById('authModal').classList.add('active');
            });
        }
        
        // Close modal
        const closeModal = document.getElementById('closeModal');
        if (closeModal) {
            closeModal.addEventListener('click', () => {
                document.getElementById('authModal').classList.remove('active');
            });
        }
        
        // Close modal on outside click
        const authModal = document.getElementById('authModal');
        if (authModal) {
            authModal.addEventListener('click', (e) => {
                if (e.target.id === 'authModal') {
                    authModal.classList.remove('active');
                }
            });
        }
        
        // Auth tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchAuthTab(tab);
            });
        });
        
        // Auth forms
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }
        
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', this.handleRegister.bind(this));
        }
        
        // Code editor
        const runCodeBtn = document.getElementById('runCode');
        if (runCodeBtn) {
            runCodeBtn.addEventListener('click', runCode);
        }
        
        const clearOutputBtn = document.getElementById('clearOutput');
        if (clearOutputBtn) {
            clearOutputBtn.addEventListener('click', clearOutput);
        }
        
        // Example filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', filterExamples);
        });
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Start learning button
        const startLearningBtn = document.getElementById('startLearning');
        if (startLearningBtn) {
            startLearningBtn.addEventListener('click', () => {
                const coursesSection = document.getElementById('courses');
                if (coursesSection) {
                    coursesSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
        
        // View courses button
        const viewCoursesBtn = document.getElementById('viewCourses');
        if (viewCoursesBtn) {
            viewCoursesBtn.addEventListener('click', () => {
                const coursesSection = document.getElementById('courses');
                if (coursesSection) {
                    coursesSection.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    },
    
    switchAuthTab(tab) {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const tabs = document.querySelectorAll('.tab-btn');
        
        tabs.forEach(t => t.classList.remove('active'));
        const activeTab = document.querySelector(`[data-tab="${tab}"]`);
        if (activeTab) activeTab.classList.add('active');
        
        if (loginForm && registerForm) {
            if (tab === 'login') {
                loginForm.classList.remove('hidden');
                registerForm.classList.add('hidden');
            } else {
                loginForm.classList.add('hidden');
                registerForm.classList.remove('hidden');
            }
        }
    },
    
    handleLogin(e) {
        e.preventDefault();
        const email = e.target.querySelector('input[type="email"]').value;
        
        const user = {
            username: email.split('@')[0],
            email: email,
            level: 1,
            completedLessons: [],
            completedProjects: 0,
            totalPoints: 0,
            achievements: []
        };
        
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.currentUser = user;
        document.getElementById('authModal').classList.remove('active');
        this.showDashboard(user);
        
        alert(currentLang === 'ru' ? 'Успешный вход!' : 'Login successful!');
    },
    
    handleRegister(e) {
        e.preventDefault();
        const username = e.target.querySelector('input[type="text"]').value;
        const email = e.target.querySelector('input[type="email"]').value;
        const passwords = e.target.querySelectorAll('input[type="password"]');
        const password = passwords[0]?.value;
        const confirmPassword = passwords[1]?.value;
        
        if (password !== confirmPassword) {
            alert(currentLang === 'ru' ? 'Пароли не совпадают!' : 'Passwords do not match!');
            return;
        }
        
        const user = {
            username: username,
            email: email,
            level: 1,
            completedLessons: [],
            completedProjects: 0,
            totalPoints: 0,
            achievements: []
        };
        
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.currentUser = user;
        document.getElementById('authModal').classList.remove('active');
        this.showDashboard(user);
        
        alert(currentLang === 'ru' ? 'Регистрация успешна!' : 'Registration successful!');
    },
    
    resetProgress() {
        if (confirm(currentLang === 'ru' ? 'Вы уверены, что хотите сбросить весь прогресс?' : 'Are you sure you want to reset all progress?')) {
            localStorage.removeItem('currentUser');
            location.reload();
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app.init();
    initLanguage();
    initTheme();
});

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    const body = document.body;
    const themeIcon = document.querySelector('.theme-icon');
    
    body.classList.remove('light-theme', 'dark-theme');
    body.classList.add(`${theme}-theme`);
    
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    const newTheme = isDark ? 'light' : 'dark';
    applyTheme(newTheme);
}

// Run Code (Mock Python execution)
function runCode() {
    const code = document.getElementById('codeInput').value;
    const output = document.getElementById('codeOutput');
    
    if (!output) return;
    
    output.textContent = currentLang === 'ru' ? 'Запуск кода...\n' : 'Running code...\n';
    
    // Simple mock execution - in real app, this would use Pyodide or call a backend
    setTimeout(() => {
        try {
            // Very basic simulation of Python output
            let result = '';
            const lines = code.split('\n');
            
            lines.forEach(line => {
                if (line.trim().startsWith('print(')) {
                    // Extract string from print statement
                    const match = line.match(/print\(['"](.+)['"]\)/);
                    if (match) {
                        result += match[1] + '\n';
                    }
                    // Check for f-string
                    const fMatch = line.match(/print\(f['"](.+)['"]\)/);
                    if (fMatch) {
                        result += fMatch[1].replace(/{.+?}/g, '1') + '\n';
                    }
                }
            });
            
            if (result) {
                output.textContent = result;
            } else {
                output.textContent = currentLang === 'ru' 
                    ? 'Код выполнен успешно!\n(Для полноценного выполнения Python подключите бэкенд или Pyodide)' 
                    : 'Code executed successfully!\n(For full Python execution, connect backend or Pyodide)';
            }
        } catch (error) {
            output.textContent = `Error: ${error.message}`;
        }
    }, 500);
}

// Clear Output
function clearOutput() {
    const output = document.getElementById('codeOutput');
    if (output) {
        output.textContent = '';
    }
}

// Filter Examples
function filterExamples(e) {
    const filter = e.target.dataset.filter;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // Filter cards
    document.querySelectorAll('.example-card').forEach(card => {
        if (filter === 'all' || card.dataset.category === filter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Logout
function logout() {
    localStorage.removeItem('currentUser');
    location.reload();
}

// Add logout listener to all logout links
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('logout')) {
        e.preventDefault();
        logout();
    }
});

// Save settings
const settingsForm = document.querySelector('.settings-form');
if (settingsForm) {
    settingsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert(currentLang === 'ru' ? 'Настройки сохранены!' : 'Settings saved!');
    });
}

// Course buttons
document.querySelectorAll('.btn-course').forEach(btn => {
    btn.addEventListener('click', function() {
        if (!this.disabled) {
            alert(currentLang === 'ru' 
                ? 'Переход к уроку... (Здесь будет контент урока)' 
                : 'Going to lesson... (Lesson content will be here)');
        }
    });
});

// Project buttons
document.querySelectorAll('.btn-project').forEach(btn => {
    btn.addEventListener('click', function() {
        alert(currentLang === 'ru' 
            ? 'Начало проекта... (Здесь откроется редактор проекта)' 
            : 'Starting project... (Project editor will open here)');
    });
});

// View code buttons
document.querySelectorAll('.btn-view').forEach(btn => {
    btn.addEventListener('click', function() {
        const exampleTitle = this.parentElement.querySelector('h4').textContent;
        alert(currentLang === 'ru' 
            ? `Открытие примера: ${exampleTitle}\n(Здесь покажется код с объяснениями)` 
            : `Opening example: ${exampleTitle}\n(Code with explanations will appear here)`);
    });
});
