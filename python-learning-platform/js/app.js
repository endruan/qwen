// Main Application JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // Initialize language
    initLanguage();
    
    // Initialize theme
    initTheme();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load user data if logged in
    loadUserData();
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
    
    if (theme === 'dark') {
        themeIcon.textContent = '☀️';
    } else {
        themeIcon.textContent = '🌙';
    }
    
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    const newTheme = isDark ? 'light' : 'dark';
    applyTheme(newTheme);
}

// Language Toggle
function toggleLanguage() {
    const newLang = currentLang === 'ru' ? 'en' : 'ru';
    updateLanguage(newLang);
    
    // Update language button text
    const langBtn = document.querySelector('.lang-icon');
    langBtn.textContent = newLang === 'ru' ? 'EN' : 'RU';
}

// Event Listeners Setup
function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Language toggle
    document.getElementById('langToggle').addEventListener('click', toggleLanguage);
    
    // Login button
    document.getElementById('loginBtn').addEventListener('click', () => {
        document.getElementById('authModal').classList.add('active');
    });
    
    // Close modal
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('authModal').classList.remove('active');
    });
    
    // Close modal on outside click
    document.getElementById('authModal').addEventListener('click', (e) => {
        if (e.target.id === 'authModal') {
            document.getElementById('authModal').classList.remove('active');
        }
    });
    
    // Auth tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchAuthTab(tab);
        });
    });
    
    // Auth forms
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // Code editor
    document.getElementById('runCode').addEventListener('click', runCode);
    document.getElementById('clearOutput').addEventListener('click', clearOutput);
    
    // Example filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', filterExamples);
    });
    
    // Dashboard navigation
    document.querySelectorAll('.dashboard-nav a').forEach(link => {
        link.addEventListener('click', handleDashboardNav);
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
    document.getElementById('startLearning').addEventListener('click', () => {
        document.querySelector('#courses').scrollIntoView({ behavior: 'smooth' });
    });
    
    // View courses button
    document.getElementById('viewCourses').addEventListener('click', () => {
        document.querySelector('#courses').scrollIntoView({ behavior: 'smooth' });
    });
}

// Auth Tab Switching
function switchAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    }
}

// Handle Login (Mock)
function handleLogin(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    const password = e.target.querySelector('input[type="password"]').value;
    
    // Mock authentication - in real app, this would call an API
    const user = {
        username: email.split('@')[0],
        email: email,
        level: 1,
        completedLessons: 0,
        completedProjects: 0,
        totalPoints: 0,
        achievements: []
    };
    
    localStorage.setItem('currentUser', JSON.stringify(user));
    document.getElementById('authModal').classList.remove('active');
    showDashboard(user);
    
    // Show success message
    alert(currentLang === 'ru' ? 'Успешный вход!' : 'Login successful!');
}

// Handle Register (Mock)
function handleRegister(e) {
    e.preventDefault();
    const username = e.target.querySelector('input[type="text"]').value;
    const email = e.target.querySelector('input[type="email"]').value;
    const password = e.target.querySelector('input[type="password"]').value;
    const confirmPassword = e.target.querySelectorAll('input[type="password"]')[1].value;
    
    if (password !== confirmPassword) {
        alert(currentLang === 'ru' ? 'Пароли не совпадают!' : 'Passwords do not match!');
        return;
    }
    
    // Mock registration
    const user = {
        username: username,
        email: email,
        level: 1,
        completedLessons: 0,
        completedProjects: 0,
        totalPoints: 0,
        achievements: []
    };
    
    localStorage.setItem('currentUser', JSON.stringify(user));
    document.getElementById('authModal').classList.remove('active');
    showDashboard(user);
    
    // Show success message
    alert(currentLang === 'ru' ? 'Регистрация успешна!' : 'Registration successful!');
}

// Show Dashboard
function showDashboard(user) {
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userDashboard').classList.add('active');
    document.querySelector('.navbar').style.display = 'none';
    
    // Hide main content sections
    document.querySelectorAll('section').forEach(section => {
        section.style.display = 'none';
    });
    document.querySelector('.footer').style.display = 'none';
}

// Load User Data
function loadUserData() {
    const userData = localStorage.getItem('currentUser');
    if (userData) {
        const user = JSON.parse(userData);
        showDashboard(user);
        updateDashboard(user);
    }
}

// Update Dashboard with User Data
function updateDashboard(user) {
    // Update progress
    const lessonProgress = (user.completedLessons / 50) * 100;
    const projectProgress = (user.completedProjects / 20) * 100;
    const pointsProgress = Math.min((user.totalPoints / 1000) * 100, 100);
    
    const progressCards = document.querySelectorAll('.progress-card');
    progressCards[0].querySelector('.progress-fill').style.width = `${lessonProgress}%`;
    progressCards[0].querySelector('.progress-value').textContent = `${user.completedLessons}/50`;
    
    progressCards[1].querySelector('.progress-fill').style.width = `${projectProgress}%`;
    progressCards[1].querySelector('.progress-value').textContent = `${user.completedProjects}/20`;
    
    progressCards[2].querySelector('.progress-fill').style.width = `${pointsProgress}%`;
    progressCards[2].querySelector('.progress-value').textContent = `${user.totalPoints} XP`;
    
    // Update achievements
    user.achievements.forEach(achId => {
        const achCard = document.querySelector(`[data-achievement="${achId}"]`);
        if (achCard) {
            achCard.classList.remove('locked');
            achCard.classList.add('unlocked');
        }
    });
}

// Dashboard Navigation
function handleDashboardNav(e) {
    e.preventDefault();
    
    // Update active state
    document.querySelectorAll('.dashboard-nav a').forEach(link => {
        link.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // Show/hide sections
    const target = e.target.getAttribute('href');
    document.querySelectorAll('.dashboard-content > div').forEach(section => {
        section.classList.add('hidden');
    });
    
    if (target.includes('progress')) {
        document.getElementById('dashboard-progress').classList.remove('hidden');
    } else if (target.includes('achievements')) {
        document.getElementById('dashboard-achievements').classList.remove('hidden');
    } else if (target.includes('settings')) {
        document.getElementById('dashboard-settings').classList.remove('hidden');
    }
}

// Run Code (Mock Python execution)
function runCode() {
    const code = document.getElementById('codeInput').value;
    const output = document.getElementById('codeOutput');
    
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
    document.getElementById('codeOutput').textContent = '';
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
document.querySelector('.settings-form').addEventListener('submit', (e) => {
    e.preventDefault();
    alert(currentLang === 'ru' ? 'Настройки сохранены!' : 'Settings saved!');
});

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
