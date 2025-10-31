// Charts Module - Handles Chart.js visualizations for trading data
class TradingCharts {
    constructor() {
        this.charts = {};
        this.chartOptions = this.getDefaultChartOptions();
    }

    /**
     * Get default Chart.js configuration options
     */
    getDefaultChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#a0aec0',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#2d3748',
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0',
                    borderColor: '#4a5568',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#4a5568',
                        borderColor: '#4a5568'
                    },
                    ticks: {
                        color: '#a0aec0',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: '#4a5568',
                        borderColor: '#4a5568'
                    },
                    ticks: {
                        color: '#a0aec0',
                        font: {
                            size: 11
                        }
                    }
                }
            }
        };
    }

    /**
     * Create or update the volume chart
     */
    createVolumeChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return null;
        }

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Prepare data for Chart.js
        const chartData = this.prepareVolumeData(data);

        const config = {
            type: 'bar',
            data: chartData,
            options: {
                ...this.chartOptions,
                plugins: {
                    ...this.chartOptions.plugins,
                    title: {
                        display: true,
                        text: 'Daily Trading Volume',
                        color: '#ffffff',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        ...this.chartOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                return `Volume: ${DataFormatter.formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    ...this.chartOptions.scales,
                    y: {
                        ...this.chartOptions.scales.y,
                        beginAtZero: true,
                        ticks: {
                            ...this.chartOptions.scales.y.ticks,
                            callback: function(value) {
                                return DataFormatter.formatCurrency(value, 0);
                            }
                        }
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    /**
     * Create or update the P&L chart
     */
    createPnLChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return null;
        }

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Prepare data for Chart.js
        const chartData = this.preparePnLData(data);

        const config = {
            type: 'line',
            data: chartData,
            options: {
                ...this.chartOptions,
                plugins: {
                    ...this.chartOptions.plugins,
                    title: {
                        display: true,
                        text: 'Cumulative P&L Over Time',
                        color: '#ffffff',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        ...this.chartOptions.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                const color = value >= 0 ? '#48bb78' : '#f56565';
                                return `P&L: ${DataFormatter.formatCurrency(value)}`;
                            }
                        }
                    }
                },
                scales: {
                    ...this.chartOptions.scales,
                    y: {
                        ...this.chartOptions.scales.y,
                        ticks: {
                            ...this.chartOptions.scales.y.ticks,
                            callback: function(value) {
                                return DataFormatter.formatCurrency(value);
                            }
                        }
                    }
                },
                elements: {
                    line: {
                        tension: 0.4,
                        borderWidth: 3
                    },
                    point: {
                        radius: 4,
                        hoverRadius: 6
                    }
                }
            }
        };

        this.charts[canvasId] = new Chart(ctx, config);
        return this.charts[canvasId];
    }

    /**
     * Prepare volume data for Chart.js
     */
    prepareVolumeData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return {
                labels: ['No Data'],
                datasets: [{
                    label: 'Volume',
                    data: [0],
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }]
            };
        }

        // Sort data by date
        const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

        const labels = sortedData.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        const volumes = sortedData.map(item => parseFloat(item.volume || 0));

        return {
            labels,
            datasets: [{
                label: 'Trading Volume',
                data: volumes,
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        };
    }

    /**
     * Prepare P&L data for Chart.js
     */
    preparePnLData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return {
                labels: ['No Data'],
                datasets: [{
                    label: 'P&L',
                    data: [0],
                    borderColor: '#4299e1',
                    backgroundColor: 'rgba(66, 153, 225, 0.1)',
                    fill: true
                }]
            };
        }

        // Sort data by date
        const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

        const labels = sortedData.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        const pnlValues = sortedData.map(item => parseFloat(item.pnl || 0));

        // Create gradient for positive/negative values
        const positiveColor = '#48bb78';
        const negativeColor = '#f56565';
        const neutralColor = '#4299e1';

        // Determine primary color based on final P&L
        const finalPnL = pnlValues[pnlValues.length - 1] || 0;
        let borderColor, backgroundColor;

        if (finalPnL > 0) {
            borderColor = positiveColor;
            backgroundColor = 'rgba(72, 187, 120, 0.1)';
        } else if (finalPnL < 0) {
            borderColor = negativeColor;
            backgroundColor = 'rgba(245, 101, 101, 0.1)';
        } else {
            borderColor = neutralColor;
            backgroundColor = 'rgba(66, 153, 225, 0.1)';
        }

        return {
            labels,
            datasets: [{
                label: 'Cumulative P&L',
                data: pnlValues,
                borderColor: borderColor,
                backgroundColor: backgroundColor,
                fill: true,
                pointBackgroundColor: pnlValues.map(val => val >= 0 ? positiveColor : negativeColor),
                pointBorderColor: pnlValues.map(val => val >= 0 ? positiveColor : negativeColor),
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderColor: borderColor,
                segment: {
                    borderColor: function(ctx) {
                        const value = ctx.p1.parsed.y;
                        return value >= 0 ? positiveColor : negativeColor;
                    }
                }
            }]
        };
    }

    /**
     * Update existing chart with new data
     */
    updateChart(canvasId, data, chartType = 'volume') {
        const chart = this.charts[canvasId];
        if (!chart) {
            console.warn(`Chart with id '${canvasId}' not found. Creating new chart.`);
            if (chartType === 'volume') {
                return this.createVolumeChart(canvasId, data);
            } else if (chartType === 'pnl') {
                return this.createPnLChart(canvasId, data);
            }
            return null;
        }

        // Prepare new data
        let newData;
        if (chartType === 'volume') {
            newData = this.prepareVolumeData(data);
        } else if (chartType === 'pnl') {
            newData = this.preparePnLData(data);
        }

        if (newData) {
            chart.data = newData;
            chart.update('active');
        }

        return chart;
    }

    /**
     * Filter chart data by date range
     */
    filterDataByDays(data, days) {
        if (!Array.isArray(data) || days <= 0) return data;

        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);

        return data.filter(item => {
            const itemDate = new Date(item.date);
            return itemDate >= cutoffDate;
        });
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            if (this.charts[canvasId]) {
                this.charts[canvasId].destroy();
                delete this.charts[canvasId];
            }
        });
    }

    /**
     * Destroy specific chart
     */
    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    /**
     * Resize charts (useful for responsive design)
     */
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }

    /**
     * Get chart instance by canvas ID
     */
    getChart(canvasId) {
        return this.charts[canvasId] || null;
    }

    /**
     * Check if Chart.js is available
     */
    static isChartJSAvailable() {
        return typeof Chart !== 'undefined';
    }

    /**
     * Initialize charts with empty data
     */
    initializeCharts() {
        if (!TradingCharts.isChartJSAvailable()) {
            console.error('Chart.js is not loaded. Please include Chart.js library.');
            return false;
        }

        // Initialize with empty data
        this.createVolumeChart('volumeChart', []);
        this.createPnLChart('pnlChart', []);

        return true;
    }
}

// Chart color themes
const ChartThemes = {
    dark: {
        background: '#0d1421',
        cardBackground: '#2d3748',
        borderColor: '#4a5568',
        textColor: '#a0aec0',
        primaryColor: '#667eea',
        successColor: '#48bb78',
        errorColor: '#f56565',
        warningColor: '#ed8936'
    },
    light: {
        background: '#ffffff',
        cardBackground: '#f7fafc',
        borderColor: '#e2e8f0',
        textColor: '#2d3748',
        primaryColor: '#4299e1',
        successColor: '#38a169',
        errorColor: '#e53e3e',
        warningColor: '#d69e2e'
    }
};

// Export for use in other modules
window.TradingCharts = TradingCharts;
window.ChartThemes = ChartThemes;

// Create global charts instance
window.tradingCharts = new TradingCharts();

console.log('Trading Charts module loaded successfully');