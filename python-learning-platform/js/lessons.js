// Lesson Viewer and Course Management

class LessonManager {
    constructor() {
        this.currentLesson = null;
        this.courseData = null;
        this.userProgress = {};
    }

    // Load course data from JSON
    async loadCourseData() {
        try {
            const response = await fetch('lessons/full-course.json');
            this.courseData = await response.json();
            return this.courseData;
        } catch (error) {
            console.error('Error loading course data:', error);
            return null;
        }
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
        const lessons = [];
        if (!this.courseData) return lessons;
        
        for (const level of this.courseData.courseStructure.levels) {
            for (const module of level.modules) {
                lessons.push(...module.lessons.map(lesson => ({
                    ...lesson,
                    levelName: level.name,
                    moduleName: module.name
                })));
            }
        }
        return lessons;
    }

    // Render lesson viewer
    renderLessonViewer(lessonId) {
        const lesson = this.getLesson(lessonId);
        if (!lesson) return;

        this.currentLesson = lesson;
        const lang = currentLang;
        const content = lesson.content[lang];

        const viewerHTML = `
            <div class="lesson-viewer" id="lessonViewer">
                <div class="lesson-header">
                    <button class="btn-back" onclick="lessonManager.closeLesson()">
                        ← <span data-i18n="back">Назад</span>
                    </button>
                    <div class="lesson-meta">
                        <span class="lesson-duration">⏱ ${lesson.duration} мин</span>
                        <span class="lesson-xp">⭐ ${lesson.xp} XP</span>
                    </div>
                </div>

                <div class="lesson-content">
                    <h1 class="lesson-title">${lesson.title[lang]}</h1>
                    
                    <div class="lesson-intro">
                        <p>${content.introduction}</p>
                    </div>

                    ${content.sections.map(section => `
                        <div class="lesson-section">
                            <h2>${section.title}</h2>
                            <div class="section-text">${this.formatText(section.text)}</div>
                        </div>
                    `).join('')}

                    <div class="code-example-section">
                        <h2 data-i18n="code_example">Пример кода</h2>
                        <div class="code-block">
                            <pre><code class="language-python">${this.escapeHtml(content.codeExample)}</code></pre>
                            <button class="btn-copy" onclick="lessonManager.copyCode()" data-i18n="copy_code">Копировать</button>
                        </div>
                    </div>

                    <div class="quiz-section" id="quizSection">
                        <h2 data-i18n="quiz">Проверка знаний</h2>
                        <div class="quiz-container">
                            ${content.quiz.map((q, index) => `
                                <div class="quiz-question" data-question="${index}">
                                    <p class="question-text">${q.question}</p>
                                    <div class="options">
                                        ${q.options.map((opt, optIndex) => `
                                            <button class="option-btn" onclick="lessonManager.selectAnswer(${index}, ${optIndex})">
                                                ${opt}
                                            </button>
                                        `).join('')}
                                    </div>
                                    <div class="feedback"></div>
                                </div>
                            `).join('')}
                        </div>
                        <button class="btn-check-quiz" onclick="lessonManager.checkQuiz()" data-i18n="check_answers">Проверить ответы</button>
                    </div>

                    <div class="task-section">
                        <h2 data-i18n="practice_task">Практическое задание</h2>
                        <div class="task-description">${content.task[lang]}</div>
                        <div class="task-actions">
                            <button class="btn-open-editor" onclick="lessonManager.openInEditor()" data-i18n="open_editor">Открыть в редакторе</button>
                            <button class="btn-submit-task" onclick="lessonManager.submitTask()" data-i18n="submit_task">Выполнено</button>
                        </div>
                    </div>
                </div>

                <div class="lesson-navigation">
                    <button class="btn-nav" id="prevLesson" onclick="lessonManager.navigateLesson(-1)" data-i18n="previous">← Предыдущий</button>
                    <button class="btn-nav btn-complete" onclick="lessonManager.completeLesson()" data-i18n="complete_lesson">✓ Завершить урок</button>
                    <button class="btn-nav" id="nextLesson" onclick="lessonManager.navigateLesson(1)">Следующий →</button>
                </div>
            </div>
        `;

        // Insert viewer into page
        const mainContent = document.querySelector('.main-content') || document.querySelector('body');
        mainContent.innerHTML = viewerHTML;
        
        // Update translations
        updateLanguage(currentLang);
        
        // Highlight code
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    }

    // Format text with line breaks and lists
    formatText(text) {
        return text
            .split('\n')
            .map(line => {
                if (line.startsWith('•')) {
                    return `<li>${line.substring(1).trim()}</li>`;
                }
                return `<p>${line}</p>`;
            })
            .join('')
            .replace(/<p><\/p>/g, '');
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
            const btn = document.querySelector('.btn-copy');
            btn.textContent = currentLang === 'ru' ? 'Скопировано!' : 'Copied!';
            setTimeout(() => {
                btn.textContent = currentLang === 'ru' ? 'Копировать' : 'Copy';
            }, 2000);
        });
    }

    // Select answer for quiz
    selectAnswer(questionIndex, optionIndex) {
        const question = document.querySelector(`[data-question="${questionIndex}"]`);
        const options = question.querySelectorAll('.option-btn');
        
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
            const questionEl = document.querySelector(`[data-question="${index}"]`);
            const selected = parseInt(questionEl.dataset.selected);
            const feedback = questionEl.querySelector('.feedback');
            
            if (selected === undefined) {
                feedback.innerHTML = `<span class="incorrect">${currentLang === 'ru' ? 'Выберите ответ' : 'Select an answer'}</span>`;
                return;
            }
            
            if (selected === q.correct) {
                score++;
                feedback.innerHTML = `<span class="correct">✓ ${currentLang === 'ru' ? 'Верно!' : 'Correct!'}</span>`;
            } else {
                feedback.innerHTML = `<span class="incorrect">✗ ${currentLang === 'ru' ? 'Неверно' : 'Incorrect'}. ${currentLang === 'ru' ? 'Правильный ответ:' : 'Correct answer:'} ${q.options[q.correct]}</span>`;
            }
        });
        
        const percentage = Math.round((score / quiz.length) * 100);
        alert(`${currentLang === 'ru' ? 'Ваш результат:' : 'Your score:'} ${percentage}%`);
        
        if (percentage === 100) {
            // Award bonus XP
            this.awardXP(25);
        }
    }

    // Open task in code editor
    openInEditor() {
        const task = this.currentLesson.content[currentLang].task[currentLang];
        const editorSection = document.querySelector('#editor');
        
        if (editorSection) {
            editorSection.scrollIntoView({ behavior: 'smooth' });
            const codeInput = document.getElementById('codeInput');
            codeInput.value = `# Задание: ${task}\n# Напишите ваш код здесь:\n\n`;
            codeInput.focus();
        }
    }

    // Submit task completion
    submitTask() {
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
        
        // Update user progress
        const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
        if (!userData.completedLessons) userData.completedLessons = [];
        if (!userData.totalPoints) userData.totalPoints = 0;
        
        if (!userData.completedLessons.includes(this.currentLesson.id)) {
            userData.completedLessons.push(this.currentLesson.id);
            userData.totalPoints += this.currentLesson.xp;
            
            localStorage.setItem('currentUser', JSON.stringify(userData));
            
            // Show achievement notification
            this.showNotification(
                currentLang === 'ru' ? 'Урок завершён!' : 'Lesson Completed!',
                `+${this.currentLesson.xp} XP`,
                'success'
            );
            
            // Check for achievements
            this.checkAchievements(userData);
        }
        
        // Navigate to next lesson or back to courses
        setTimeout(() => {
            this.navigateLesson(1);
        }, 1500);
    }

    // Navigate between lessons
    navigateLesson(direction) {
        const allLessons = this.getAllLessons();
        const currentIndex = allLessons.findIndex(l => l.id === this.currentLesson?.id);
        const newIndex = currentIndex + direction;
        
        if (newIndex >= 0 && newIndex < allLessons.length) {
            this.renderLessonViewer(allLessons[newIndex].id);
        } else if (newIndex < 0) {
            // Go back to courses
            document.querySelector('#courses').scrollIntoView({ behavior: 'smooth' });
        } else {
            this.showNotification(
                currentLang === 'ru' ? 'Курс завершён!' : 'Course Completed!',
                currentLang === 'ru' ? 'Поздравляем с окончанием!' : 'Congratulations on finishing!',
                'success'
            );
        }
    }

    // Close lesson viewer
    closeLesson() {
        const viewer = document.getElementById('lessonViewer');
        if (viewer) {
            viewer.remove();
        }
        document.querySelector('#courses').style.display = 'block';
    }

    // Award XP
    awardXP(amount) {
        const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
        userData.totalPoints = (userData.totalPoints || 0) + amount;
        localStorage.setItem('currentUser', JSON.stringify(userData));
    }

    // Check achievements
    checkAchievements(userData) {
        const achievements = userData.achievements || [];
        const newAchievements = [];
        
        // First lesson completed
        if (userData.completedLessons?.length === 1 && !achievements.includes('first_steps')) {
            newAchievements.push({
                id: 'first_steps',
                name: currentLang === 'ru' ? 'Первые шаги' : 'First Steps',
                desc: currentLang === 'ru' ? 'Пройди первый урок' : 'Complete first lesson'
            });
        }
        
        // 5 lessons completed
        if (userData.completedLessons?.length === 5 && !achievements.includes('learner')) {
            newAchievements.push({
                id: 'learner',
                name: currentLang === 'ru' ? 'Ученик' : 'Learner',
                desc: currentLang === 'ru' ? 'Пройди 5 уроков' : 'Complete 5 lessons'
            });
        }
        
        if (newAchievements.length > 0) {
            userData.achievements = [...achievements, ...newAchievements.map(a => a.id)];
            localStorage.setItem('currentUser', JSON.stringify(userData));
            
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
            <div class="notification-content">
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

// Add event listeners for course buttons
document.addEventListener('DOMContentLoaded', () => {
    // Load course data
    lessonManager.loadCourseData();
    
    // Add click handlers to course cards
    document.querySelectorAll('.btn-course').forEach(btn => {
        btn.addEventListener('click', function() {
            if (!this.disabled) {
                const level = this.closest('.course-card').classList.contains('beginner') ? 'beginner' : 
                             this.closest('.course-card').classList.contains('intermediate') ? 'intermediate' : 'advanced';
                
                // Start first lesson of the level
                const lessons = lessonManager.getAllLessons();
                if (lessons.length > 0) {
                    lessonManager.renderLessonViewer(lessons[0].id);
                }
            }
        });
    });
});
