/**
 * Eco-RVM - JavaScript Principal v2.0
 */

// Formatear números con separadores de miles
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Mostrar notificación toast
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Crear gráfica de líneas para reciclajes por día
function createRecyclingChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.map(d => {
                const date = new Date(d);
                return date.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric' });
            }),
            datasets: [{
                label: 'Reciclajes',
                data: values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#333',
                    titleFont: { size: 14 },
                    bodyFont: { size: 13 },
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Crear gráfica de dona para distribución
function createDonutChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Animar números
function animateNumber(element, targetValue, duration = 1000) {
    const startValue = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const easeOutQuad = progress * (2 - progress);
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuad);

        element.textContent = formatNumber(currentValue);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Canjear recompensa
async function redeemReward(userId, rewardId) {
    try {
        const response = await fetch('/api/rewards/redeem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                usuario_id: userId,
                recompensa_id: rewardId
            })
        });

        const data = await response.json();

        if (data.exito) {
            showToast(`¡Canje exitoso! Código: ${data.codigo_canje}`, 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showToast(data.error || 'Error al canjear', 'danger');
        }
    } catch (error) {
        showToast('Error de conexión', 'danger');
        console.error('Error:', error);
    }
}

// Cargar estadísticas del dashboard
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/stats/dashboard');
        const data = await response.json();

        // Actualizar estadísticas
        if (data.estadisticas) {
            updateStatElement('total-usuarios', data.estadisticas.total_usuarios);
            updateStatElement('total-transacciones', data.estadisticas.total_transacciones);
            updateStatElement('total-puntos', data.estadisticas.total_puntos_sistema);
        }

        // Actualizar impacto ambiental
        if (data.impacto_ambiental) {
            updateStatElement('co2-evitado', data.impacto_ambiental.co2_evitado_kg.toFixed(2));
            updateStatElement('peso-reciclado', data.impacto_ambiental.peso_reciclado_kg.toFixed(2));
        }

        // Crear gráfica de reciclajes
        if (data.reciclajes_semana) {
            createRecyclingChart('chart-reciclajes', data.reciclajes_semana);
        }

    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        if (typeof value === 'number') {
            animateNumber(element, value);
        } else {
            element.textContent = value;
        }
    }
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    // Animar elementos con clase .animate-number
    document.querySelectorAll('.animate-number').forEach(el => {
        const value = parseInt(el.dataset.value || el.textContent, 10);
        if (!isNaN(value)) {
            animateNumber(el, value);
        }
    });

    // Añadir fade-in a cards
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});

// Exportar funciones para uso global
window.EcoRVM = {
    showToast,
    formatNumber,
    createRecyclingChart,
    createDonutChart,
    animateNumber,
    redeemReward,
    loadDashboardStats
};

// Aplicar estilos dinámicos desde atributos data-* (Fix para linters)
document.addEventListener('DOMContentLoaded', function () {
    // Anchos dinámicos (Progress Bars)
    document.querySelectorAll('.dynamic-width').forEach(el => {
        if (el.dataset.width) {
            el.style.width = el.dataset.width;
        }
    });

    // Colores dinámicos (Badges)
    document.querySelectorAll('.dynamic-badge').forEach(el => {
        if (el.dataset.color) {
            const color = el.dataset.color;
            el.style.backgroundColor = color + '20'; // Opacidad 20%
            el.style.border = `2px solid ${color}`;
        }
    });
});
