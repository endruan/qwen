// Основной JavaScript для Nutrition Planner

document.addEventListener('DOMContentLoaded', function() {
    console.log('Nutrition Planner loaded');
    
    // Инициализация всех компонентов
    initIngredientSelector();
    initRecipeForm();
    initMealPlanner();
});

// Селектор ингредиентов для рецептов
function initIngredientSelector() {
    const addIngredientBtn = document.getElementById('add-ingredient-btn');
    if (!addIngredientBtn) return;
    
    addIngredientBtn.addEventListener('click', function() {
        const ingredientSelect = document.getElementById('ingredient-select');
        const quantityInput = document.getElementById('ingredient-quantity');
        
        if (!ingredientSelect || !quantityInput) return;
        
        const ingredientId = ingredientSelect.value;
        const ingredientName = ingredientSelect.options[ingredientSelect.selectedIndex]?.text;
        const quantity = parseFloat(quantityInput.value);
        
        if (!ingredientId || !quantity || quantity <= 0) {
            alert('Выберите ингредиент и укажите количество');
            return;
        }
        
        // Добавляем в список выбранных ингредиентов
        addIngredientToList(ingredientId, ingredientName, quantity);
        
        // Очищаем поля
        ingredientSelect.value = '';
        quantityInput.value = '';
    });
}

function addIngredientToList(id, name, quantity) {
    const ingredientsList = document.getElementById('selected-ingredients-list');
    if (!ingredientsList) return;
    
    // Проверяем, есть ли уже такой ингредиент
    const existingItem = ingredientsList.querySelector(`[data-ingredient-id="${id}"]`);
    if (existingItem) {
        const qtySpan = existingItem.querySelector('.ingredient-quantity');
        const currentQty = parseFloat(qtySpan.textContent);
        qtySpan.textContent = (currentQty + quantity).toFixed(1);
        return;
    }
    
    const item = document.createElement('div');
    item.className = 'selected-ingredient-item';
    item.dataset.ingredientId = id;
    item.innerHTML = `
        <span class="ingredient-name">${name}</span>
        <span class="ingredient-quantity">${quantity.toFixed(1)}</span>
        <button type="button" class="btn-remove-ingredient" onclick="removeIngredient(${id})">×</button>
    `;
    
    ingredientsList.appendChild(item);
    
    // Обновляем скрытое поле с JSON
    updateIngredientsJson();
}

function removeIngredient(id) {
    const item = document.querySelector(`[data-ingredient-id="${id}"]`);
    if (item) {
        item.remove();
        updateIngredientsJson();
    }
}

function updateIngredientsJson() {
    const ingredientsList = document.getElementById('selected-ingredients-list');
    const jsonInput = document.getElementById('ingredients-json');
    
    if (!ingredientsList || !jsonInput) return;
    
    const items = ingredientsList.querySelectorAll('.selected-ingredient-item');
    const ingredients = [];
    
    items.forEach(item => {
        const id = parseInt(item.dataset.ingredientId);
        const quantity = parseFloat(item.querySelector('.ingredient-quantity').textContent);
        ingredients.push({ ingredient_id: id, quantity: quantity });
    });
    
    jsonInput.value = JSON.stringify(ingredients);
}

// Форма рецепта
function initRecipeForm() {
    const recipeForm = document.getElementById('recipe-form');
    if (!recipeForm) return;
    
    recipeForm.addEventListener('submit', function(e) {
        updateIngredientsJson();
        
        const jsonInput = document.getElementById('ingredients-json');
        if (jsonInput && jsonInput.value === '[]') {
            if (!confirm('Вы не добавили ни одного ингредиента. Продолжить?')) {
                e.preventDefault();
            }
        }
    });
}

// Планировщик питания
function initMealPlanner() {
    // Обработка модальных окон для добавления рецептов
    const mealPlanForms = document.querySelectorAll('.meal-plan-form');
    
    mealPlanForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const recipeSelect = form.querySelector('select[name="recipe_id"]');
            if (recipeSelect && !recipeSelect.value) {
                e.preventDefault();
                alert('Выберите рецепт');
            }
        });
    });
}

// Утилиты
function formatNumber(num, decimals = 1) {
    return parseFloat(num).toFixed(decimals);
}

function calculateBMI(weight, height) {
    if (!weight || !height) return 0;
    return (weight / Math.pow(height / 100, 2)).toFixed(1);
}

// Экспорт списка покупок в Telegram
async function exportToTelegram() {
    try {
        const response = await fetch('/shopping-list/export');
        const data = await response.json();
        
        if (data.message) {
            // Копируем в буфер обмена
            navigator.clipboard.writeText(data.message).then(() => {
                alert('Список покупок скопирован в буфер обмена!\n\nТеперь вы можете вставить его в Telegram.');
            });
        }
    } catch (error) {
        console.error('Ошибка экспорта:', error);
        alert('Произошла ошибка при экспорте списка покупок');
    }
}

// Графики (Chart.js)
function initWeightChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Вес (кг)',
                data: data.values,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function initMacroChart(canvasId, calories, protein, fat, carbs) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Белки', 'Жиры', 'Углеводы'],
            datasets: [{
                data: [protein * 4, fat * 9, carbs * 4],
                backgroundColor: ['#2196F3', '#ff9800', '#4CAF50']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
