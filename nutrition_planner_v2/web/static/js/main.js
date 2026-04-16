// Main JavaScript for Nutrition Planner

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 8px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

// Format currency
function formatCurrency(value) {
    return value.toFixed(2) + ' ₽';
}

// Format number with one decimal
function formatNumber(value) {
    return Math.round(value * 10) / 10;
}

// Date utilities
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function getWeekDates(startDate) {
    const dates = [];
    for (let i = 0; i < 7; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        dates.push(formatDate(date));
    }
    return dates;
}

// API helpers
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Accept': 'application/json'
        }
    };
    
    if (data instanceof FormData) {
        options.body = data;
    } else if (data) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }
    
    return response.json();
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', () => {
    // Add any initialization code here
    console.log('Nutrition Planner initialized');
});

// Export to Telegram
async function exportToTelegram() {
    try {
        const response = await fetch('/api/shopping-list/export');
        const data = await response.json();
        
        // Copy to clipboard
        await navigator.clipboard.writeText(data.text);
        showNotification('📋 Список скопирован в буфер обмена!');
        
        // Open Telegram
        window.open('https://t.me/savedmessages', '_blank');
    } catch (error) {
        showNotification('❌ Ошибка экспорта: ' + error.message, 'error');
    }
}

// Rich text editor helper (for recipe descriptions)
function initRichText(editorId) {
    const editor = document.getElementById(editorId);
    if (!editor) return;
    
    // Enable basic HTML editing
    editor.contentEditable = true;
    
    // Add toolbar if needed
    const toolbar = document.createElement('div');
    toolbar.className = 'rich-text-toolbar';
    toolbar.innerHTML = `
        <button type="button" onclick="document.execCommand('bold')"><b>B</b></button>
        <button type="button" onclick="document.execCommand('italic')"><i>I</i></button>
        <button type="button" onclick="document.execCommand('underline')"><u>U</u></button>
        <button type="button" onclick="insertImagePrompt()">🖼️</button>
    `;
    toolbar.style.cssText = `
        display: flex;
        gap: 5px;
        margin-bottom: 10px;
        padding: 10px;
        background: #f5f5f5;
        border-radius: 6px;
    `;
    
    editor.parentNode.insertBefore(toolbar, editor);
    editor.style.cssText = `
        min-height: 150px;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        background: white;
    `;
}

function insertImagePrompt() {
    const url = prompt('Введите URL изображения:');
    if (url) {
        document.execCommand('insertImage', false, url);
    }
}

// Meal planner helpers
const MEAL_TYPES = {
    'breakfast': '🌅 Завтрак',
    'snack1': '🍎 Второй завтрак',
    'lunch': '🍲 Обед',
    'snack2': '☕ Перекус',
    'dinner': '🌙 Ужин',
    'snack3': '🥛 Второй перекус'
};

function getMealTypeLabel(type) {
    return MEAL_TYPES[type] || type;
}

// Calculate recipe nutrition
function calculateRecipeNutrition(ingredients) {
    let totalCalories = 0;
    let totalProtein = 0;
    let totalFat = 0;
    let totalCarbs = 0;
    let totalCost = 0;
    
    ingredients.forEach(ing => {
        const factor = ing.quantity / 100;
        totalCalories += ing.calories * factor;
        totalProtein += ing.protein * factor;
        totalFat += ing.fat * factor;
        totalCarbs += ing.carbs * factor;
        
        if (ing.price_per_unit && ing.package_size) {
            totalCost += (ing.price_per_unit / ing.package_size) * ing.quantity;
        }
    });
    
    return {
        calories: totalCalories,
        protein: totalProtein,
        fat: totalFat,
        carbs: totalCarbs,
        cost: totalCost
    };
}

// Validate form
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#f44336';
            isValid = false;
        } else {
            field.style.borderColor = '#e0e0e0';
        }
    });
    
    return isValid;
}

// Clear form
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

// Local storage helpers
function saveToStorage(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function loadFromStorage(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Print/Export helpers
function printPage() {
    window.print();
}

function exportToPDF() {
    // Simple print-based export
    window.print();
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('App ready');
    });
} else {
    console.log('App ready');
}
