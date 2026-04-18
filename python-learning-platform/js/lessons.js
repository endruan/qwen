// Lesson Viewer and Course Management

class LessonManager {
    constructor() {
        this.currentLesson = null;
        this.courseData = null;
        this.userProgress = {};
        this.allLessonsFlat = [];
    }

    // Load course data from JSON
    async loadCourseData() {
        try {
            const response = await fetch('lessons/full-course.json');
            this.courseData = await response.json();
            this.flattenLessons();
            return this.courseData;
        } catch (error) {
            console.error('Error loading course data:', error);
            return null;
        }
    }

    // Flatten all lessons into a single array for navigation
    flattenLessons() {
        this.allLessonsFlat = [];
        if (!this.courseData) return;
        
        for (const level of this.courseData.courseStructure.levels) {
            for (const module of level.modules) {
                for (const lesson of module.lessons) {
                    this.allLessonsFlat.push({
                        ...lesson,
                        levelId: level.id,
                        levelName: level.name,
                        moduleId: module.id,
                        moduleName: module.name
                    });
                }
            }
        }
    }

    // Render modules grid
    renderModules() {
        if (!this.courseData) {
            this.loadCourseData().then(() => this.renderModules());
            return;
        }

        const container = document.getElementById('modules-container');
        if (!container) return;

        const lang = currentLang;
        let html = '';

        for (const level of this.courseData.courseStructure.levels) {
            html += `
                <div class="level-section">
                    <h2 class="level-title">${level.name[lang]}</h2>
                    <div class="modules-row">
            `;

            for (const module of level.modules) {
                const completedCount = module.lessons.filter(l => 
                    this.isLessonCompleted(l.id)
                ).length;
                const totalCount = module.lessons.length;
                const progress = Math.round((completedCount / totalCount) * 100);

                html += `
                    <div class="module-card" data-module="${module.id}">
                        <div class="module-header">
                            <h3>${module.name[lang]}</h3>
                            <span class="module-progress">${progress}%</span>
                        </div>
                        <div class="module-lessons">
                `;

                for (const lesson of module.lessons) {
                    const isCompleted = this.isLessonCompleted(lesson.id);
                    html += `
                        <button class="lesson-btn ${isCompleted ? 'completed' : ''}" 
                                onclick="lessonManager.openLesson('${lesson.id}')">
                            <span class="lesson-icon">${isCompleted ? '✓' : '📝'}</span>
                            <span class="lesson-title">${lesson.title[lang]}</span>
                            <span class="lesson-meta">${lesson.duration} мин • ${lesson.xp} XP</span>
                        </button>
                    `;
                }

                html += `
                        </div>
                    </div>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
    }

    // Check if lesson is completed
    isLessonCompleted(lessonId) {
        const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
        return userData.completedLessons?.includes(lessonId) || false;
    }

    // Open lesson viewer
    openLesson(lessonId) {
        const lesson = this.getLesson(lessonId);
        if (!lesson) return;

        this.currentLesson = lesson;
        const lang = currentLang;
        const content = lesson.content[lang];

        // Hide modules, show lesson viewer
        document.getElementById('modules-container').style.display = 'none';
        const viewerSection = document.getElementById('lesson-viewer-section');
        viewerSection.classList.remove('hidden-section');
        viewerSection.classList.add('active-section');

        const viewerHTML = `
            <div class="lesson-viewer-full">
                <div class="lesson-header-bar">
                    <button class="btn-back-modules" onclick="lessonManager.backToModules()">
                        ← <span data-i18n="back_to_modules">Назад к модулям</span>
                    </button>
                    <div class="lesson-meta-inline">
                        <span class="lesson-duration">⏱ ${lesson.duration} мин</span>
                        <span class="lesson-xp">⭐ ${lesson.xp} XP</span>
                    </div>
                </div>

                <div class="lesson-body">
                    <h1 class="lesson-main-title">${lesson.title[lang]}</h1>
                    
                    <div class="lesson-intro-box">
                        <p class="intro-text">${content.introduction}</p>
                    </div>

                    ${content.sections.map((section, idx) => `
                        <div class="lesson-section-block">
                            <h2><span class="section-num">${idx + 1}</span> ${section.title}</h2>
                            <div class="section-content">${this.formatText(section.text)}</div>
                        </div>
                    `).join('')}

                    <div class="code-example-block">
                        <div class="code-header">
                            <h2 data-i18n="code_example">Пример кода</h2>
                            <button class="btn-copy-code" onclick="lessonManager.copyCode()">
                                📋 <span data-i18n="copy_code">Копировать</span>
                            </button>
                        </div>
                        <pre class="code-pre"><code class="language-python">${this.escapeHtml(content.codeExample)}</code></pre>
                    </div>

                    <div class="quiz-block" id="quizBlock">
                        <h2 data-i18n="knowledge_check">Проверка знаний</h2>
                        <p class="quiz-instruction" data-i18n="quiz_instruction">Выберите правильный ответ на каждый вопрос:</p>
                        
                        <div class="quiz-questions">
                            ${content.quiz.map((q, qIdx) => `
                                <div class="question-card" data-qidx="${qIdx}">
                                    <p class="question-text">${qIdx + 1}. ${q.question}</p>
                                    <div class="answers-grid">
                                        ${q.options.map((opt, optIdx) => `
                                            <button class="answer-option" onclick="lessonManager.selectAnswer(${qIdx}, ${optIdx})">
                                                <span class="option-letter">${String.fromCharCode(65 + optIdx)}</span>
                                                <span class="option-text">${opt}</span>
                                            </button>
                                        `).join('')}
                                    </div>
                                    <div class="question-feedback"></div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <button class="btn-check-quiz" onclick="lessonManager.checkQuiz()" data-i18n="check_answers">Проверить ответы</button>
                    </div>

                    <div class="practice-block">
                        <h2 data-i18n="practice_task">Практическое задание</h2>
                        <div class="task-card">
                            <p class="task-desc">${content.practice.task[lang] || content.practice.task}</p>
                            ${content.practice.starterCode ? `
                                <pre class="starter-code"><code>${this.escapeHtml(content.practice.starterCode)}</code></pre>
                            ` : ''}
                        </div>
                        <div class="task-buttons">
                            <button class="btn-open-editor" onclick="lessonManager.openEditorForTask()">
                                💻 <span data-i18n="open_in_editor">Открыть в редакторе</span>
                            </button>
                            <button class="btn-done-task" onclick="lessonManager.markTaskDone()">
                                ✓ <span data-i18n="mark_done">Я выполнил</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="lesson-footer-nav">
                    <button class="btn-prev-lesson" onclick="lessonManager.navigateLesson(-1)" ${this.getCurrentIndex() === 0 ? 'disabled' : ''}>
                        ← <span data-i18n="previous_lesson">Пред. урок</span>
                    </button>
                    <button class="btn-complete-lesson" onclick="lessonManager.completeLesson()">
                        🎉 <span data-i18n="complete_lesson">Завершить урок</span>
                    </button>
                    <button class="btn-next-lesson" onclick="lessonManager.navigateLesson(1)" ${this.getCurrentIndex() >= this.allLessonsFlat.length - 1 ? 'disabled' : ''}>
                        <span data-i18n="next_lesson">След. урок</span> →
                    </button>
                </div>
            </div>
        `;

        document.getElementById('lesson-content').innerHTML = viewerHTML;
        
        // Update translations
        if (typeof updateLanguage === 'function') {
            updateLanguage(lang);
        }
        
        // Highlight code
        if (typeof Prism !== 'undefined') {
            setTimeout(() => Prism.highlightAll(), 100);
        }
    }

    // Get current lesson index
    getCurrentIndex() {
        if (!this.currentLesson) return -1;
        return this.allLessonsFlat.findIndex(l => l.id === this.currentLesson.id);
    }

    // Back to modules
    backToModules() {
        document.getElementById('lesson-viewer-section').classList.remove('active-section');
        document.getElementById('lesson-viewer-section').classList.add('hidden-section');
        document.getElementById('modules-container').style.display = 'grid';
        this.renderModules();
    }

    // Get lesson by ID
    getLesson(lessonId) {
        if (!this.courseData) return null;
        
        for (const level of this.courseData.courseStructure.levels) {
            for (const module of level.modules) {
                for (const lesson of module.lessons) {
                    if (lesson.id === lessonId) {
                        return lesson;
                    }
                }
            }
        }
        return null;
    }

    // Get all lessons
    getAllLessons() {
        return this.allLessonsFlat;
    }

    // Navigate between lessons
    navigateLesson(direction) {
        const currentIndex = this.getCurrentIndex();
        const newIndex = currentIndex + direction;
        
        if (newIndex >= 0 && newIndex < this.allLessonsFlat.length) {
            this.openLesson(this.allLessonsFlat[newIndex].id);
        }
    }

    // Format text with line breaks and lists
    formatText(text) {
        return text
            .split('\n')
            .map(line => {
                if (line.trim().startsWith('•')) {
                    return `<li>${line.trim().substring(1)}</li>`;
                }
                return line.trim() ? `<p>${line}</p>` : '';
            })
            .filter(l => l)
            .join('')
            .replace(/(<p>.*?<\/p>)(<p>.*?<\/p>)/gs, '$1$2');
    }

    // Escape HTML for code display
    escapeHtml(code) {
        const div = document.createElement('div');
        div.textContent = code;
        return div.innerHTML;
    }

    // Copy code to clipboard
    copyCode() {
        const code = this.currentLesson.content[currentLang].codeExample;
        navigator.clipboard.writeText(code).then(() => {
            const btn = document.querySelector('.btn-copy-code');
            const originalText = btn.innerHTML;
            btn.innerHTML = '✓ ' + (currentLang === 'ru' ? 'Скопировано!' : 'Copied!');
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 2000);
        });
    }

    // Select answer for quiz
    selectAnswer(questionIndex, optionIndex) {
        const question = document.querySelector(`[data-qidx="${questionIndex}"]`);
        const options = question.querySelectorAll('.answer-option');
        
        options.forEach((opt, idx) => {
            opt.classList.remove('selected');
            if (idx === optionIndex) {
                opt.classList.add('selected');
            }
        });
        
        question.dataset.selected = optionIndex;
    }

    // Check quiz answers
    checkQuiz() {
        const quiz = this.currentLesson.content[currentLang].quiz;
        let score = 0;
        
        quiz.forEach((q, index) => {
            const questionEl = document.querySelector(`[data-qidx="${index}"]`);
            const selected = parseInt(questionEl.dataset.selected);
            const feedback = questionEl.querySelector('.question-feedback');
            
            if (selected === undefined) {
                feedback.innerHTML = `<span class="feedback-warn">${currentLang === 'ru' ? 'Выберите ответ' : 'Select an answer'}</span>`;
                return;
            }
            
            if (selected === q.correct) {
                score++;
                feedback.innerHTML = `<span class="feedback-correct">✓ ${currentLang === 'ru' ? 'Верно!' : 'Correct!'}</span>`;
            } else {
                feedback.innerHTML = `<span class="feedback-incorrect">✗ ${currentLang === 'ru' ? 'Неверно' : 'Incorrect'}. ${currentLang === 'ru' ? 'Правильный:' : 'Correct:'} ${q.options[q.correct]}</span>`;
            }
        });
        
        const percentage = Math.round((score / quiz.length) * 100);
        const message = currentLang === 'ru' 
            ? `Ваш результат: ${percentage}%` 
            : `Your score: ${percentage}%`;
        
        alert(message);
        
        if (percentage === 100) {
            this.awardBonusXP(25);
            this.showNotification(
                currentLang === 'ru' ? '🎯 Отлично!' : '🎯 Excellent!',
                '+25 XP за perfect quiz!',
                'success'
            );
        }
    }

    // Open editor for task
    openEditorForTask() {
        const task = this.currentLesson.content[currentLang].practice.task;
        const starterCode = this.currentLesson.content[currentLang].practice.starterCode || '';
        
        // Navigate to editor section
        app.navigateTo('editor');
        
        const codeInput = document.getElementById('codeInput');
        if (codeInput) {
            codeInput.value = `# ${currentLang === 'ru' ? 'Задание:' : 'Task:'} ${task}\n${starterCode}`;
        }
    }

    // Mark task as done
    markTaskDone() {
        const confirmed = confirm(currentLang === 'ru' 
            ? 'Вы уверены, что выполнили задание?' 
            : 'Are you sure you completed the task?');
        
        if (confirmed) {
            this.completeLesson();
        }
    }

    // Complete lesson
    completeLesson() {
        if (!this.currentLesson) return;
        
        const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
        if (!userData.completedLessons) userData.completedLessons = [];
        if (!userData.totalPoints) userData.totalPoints = 0;
        
        if (!userData.completedLessons.includes(this.currentLesson.id)) {
            userData.completedLessons.push(this.currentLesson.id);
            userData.totalPoints += this.currentLesson.xp;
            
            localStorage.setItem('currentUser', JSON.stringify(userData));
            app.currentUser = userData;
            app.updateDashboard(userData);
            
            this.showNotification(
                currentLang === 'ru' ? '🎉 Урок завершён!' : '🎉 Lesson Completed!',
                `+${this.currentLesson.xp} XP`,
                'success'
            );
            
            this.checkAchievements(userData);
        }
        
        // Navigate to next lesson
        setTimeout(() => {
            this.navigateLesson(1);
        }, 1500);
    }

    // Award bonus XP
    awardBonusXP(amount) {
        const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
        userData.totalPoints = (userData.totalPoints || 0) + amount;
        localStorage.setItem('currentUser', JSON.stringify(userData));
        app.currentUser = userData;
        app.updateDashboard(userData);
    }

    // Check achievements
    checkAchievements(userData) {
        const achievements = userData.achievements || [];
        const newAchievements = [];
        const completedCount = userData.completedLessons?.length || 0;
        
        if (completedCount === 1 && !achievements.includes('first_steps')) {
            newAchievements.push({
                id: 'first_steps',
                name: currentLang === 'ru' ? 'Первые шаги' : 'First Steps',
                desc: currentLang === 'ru' ? 'Пройди первый урок' : 'Complete first lesson'
            });
        }
        
        if (completedCount === 5 && !achievements.includes('learner')) {
            newAchievements.push({
                id: 'learner',
                name: currentLang === 'ru' ? 'Ученик' : 'Learner',
                desc: currentLang === 'ru' ? 'Пройди 5 уроков' : 'Complete 5 lessons'
            });
        }
        
        if (completedCount === 10 && !achievements.includes('dedicated')) {
            newAchievements.push({
                id: 'dedicated',
                name: currentLang === 'ru' ? 'Преданный' : 'Dedicated',
                desc: currentLang === 'ru' ? 'Пройди 10 уроков' : 'Complete 10 lessons'
            });
        }
        
        if (completedCount === 18 && !achievements.includes('graduate')) {
            newAchievements.push({
                id: 'graduate',
                name: currentLang === 'ru' ? 'Выпускник' : 'Graduate',
                desc: currentLang === 'ru' ? 'Пройди весь курс' : 'Complete entire course'
            });
        }
        
        if (newAchievements.length > 0) {
            userData.achievements = [...achievements, ...newAchievements.map(a => a.id)];
            localStorage.setItem('currentUser', JSON.stringify(userData));
            app.currentUser = userData;
            
            newAchievements.forEach(ach => {
                this.showNotification(
                    currentLang === 'ru' ? '🏆 Достижение!' : '🏆 Achievement!',
                    ach.name,
                    'achievement'
                );
            });
        }
    }

    // Show notification
    showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notif-content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize lesson manager
const lessonManager = new LessonManager();

// Load course data on init
document.addEventListener('DOMContentLoaded', () => {
    lessonManager.loadCourseData();
});
