/*
 * AGTR Merkezi v5.0 - Charts Module
 * Chart.js ile profesyonel grafikler
 */

const AGTRCharts = {
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#a0a0b0',
                    font: { family: "'Inter', sans-serif" }
                }
            },
            tooltip: {
                backgroundColor: '#1a1a2e',
                titleColor: '#fff',
                bodyColor: '#a0a0b0',
                borderColor: '#ff6b00',
                borderWidth: 1,
                padding: 12,
                displayColors: false
            }
        },
        scales: {
            x: {
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: { color: '#a0a0b0' }
            },
            y: {
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: { color: '#a0a0b0' }
            }
        }
    },
    
    colors: {
        primary: '#ff6b00',
        secondary: '#00ff88',
        tertiary: '#00bfff',
        danger: '#ff3366',
        warning: '#ffcc00',
        gradient1: ['rgba(255, 107, 0, 0.5)', 'rgba(255, 107, 0, 0.0)'],
        gradient2: ['rgba(0, 255, 136, 0.5)', 'rgba(0, 255, 136, 0.0)']
    },
    
    createGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },
    
    // Revenue Chart - Cizgi grafik
    revenue(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const gradient = this.createGradient(
            ctx.getContext('2d'), 
            this.colors.gradient1[0], 
            this.colors.gradient1[1]
        );
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Gelir (TL)',
                    data: data.values,
                    borderColor: this.colors.primary,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Aylık Gelir',
                        color: '#fff',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    },
    
    // Users Chart - Bar grafik
    users(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Yeni Kullanıcı',
                    data: data.values,
                    backgroundColor: this.colors.secondary,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Kullanıcı Kayıtları',
                        color: '#fff',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    },
    
    // Servers Chart - Doughnut
    servers(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        this.colors.secondary,  // Online
                        this.colors.danger,     // Offline
                        this.colors.warning,    // Pending
                        this.colors.tertiary    // Expired
                    ],
                    borderWidth: 0,
                    spacing: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#a0a0b0', padding: 20 }
                    },
                    title: {
                        display: true,
                        text: 'Sunucu Durumları',
                        color: '#fff',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    },
    
    // Players Chart - Real-time line
    players(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Online Oyuncu',
                    data: data.values,
                    borderColor: this.colors.tertiary,
                    backgroundColor: 'transparent',
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: {
                ...this.defaultOptions,
                animation: { duration: 0 },
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Anlık Oyuncu Sayısı',
                        color: '#fff',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    },
    
    // Traffic Chart - Area
    traffic(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const gradient1 = this.createGradient(
            ctx.getContext('2d'),
            'rgba(0, 191, 255, 0.4)',
            'rgba(0, 191, 255, 0.0)'
        );
        
        const gradient2 = this.createGradient(
            ctx.getContext('2d'),
            'rgba(255, 107, 0, 0.4)',
            'rgba(255, 107, 0, 0.0)'
        );
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Sayfa Görüntüleme',
                        data: data.pageViews,
                        borderColor: this.colors.tertiary,
                        backgroundColor: gradient1,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Ziyaretçi',
                        data: data.visitors,
                        borderColor: this.colors.primary,
                        backgroundColor: gradient2,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Site Trafiği',
                        color: '#fff',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    },
    
    // Game Type Distribution - Polar Area
    gameTypes(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        'rgba(255, 107, 0, 0.7)',
                        'rgba(0, 255, 136, 0.7)',
                        'rgba(0, 191, 255, 0.7)',
                        'rgba(255, 51, 102, 0.7)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#a0a0b0' }
                    },
                    title: {
                        display: true,
                        text: 'Oyun Dağılımı',
                        color: '#fff',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    r: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { display: false }
                    }
                }
            }
        });
    },
    
    // Update chart data (for real-time)
    updateChart(chart, newData, newLabels = null) {
        if (!chart) return;
        
        chart.data.datasets[0].data = newData;
        if (newLabels) {
            chart.data.labels = newLabels;
        }
        chart.update('none');
    },
    
    // Add data point (for streaming)
    addDataPoint(chart, label, value, maxPoints = 20) {
        if (!chart) return;
        
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);
        
        if (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        
        chart.update('none');
    },
    
    // Destroy chart
    destroy(chart) {
        if (chart) {
            chart.destroy();
        }
    }
};

// Sparkline mini charts
const Sparkline = {
    create(element, data, color = '#ff6b00') {
        const canvas = document.createElement('canvas');
        canvas.width = element.offsetWidth || 100;
        canvas.height = element.offsetHeight || 30;
        element.appendChild(canvas);
        
        return new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.map((_, i) => i),
                datasets: [{
                    data: data,
                    borderColor: color,
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.4
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }
};

// Export
window.AGTRCharts = AGTRCharts;
window.Sparkline = Sparkline;
