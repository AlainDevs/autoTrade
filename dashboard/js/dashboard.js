// Main Dashboard Module - Orchestrates all dashboard functionality
class TradingDashboard {
    constructor() {
        this.refreshInterval = null;
        this.refreshIntervalMs = 30000; // 30 seconds
        this.currentTradeSort = { field: 'trade_timestamp', direction: 'desc' };
        this.currentFilters = { symbol: '', limit: 50 };
        this.allTrades = [];
        this.isLoading = false;
        
        // Load stored settings
        this.loadStoredSettings();
        
        this.initialize();
    }

    /**
     * Initialize the dashboard
     */
    async initialize() {
        console.log('Initializing Trading Dashboard...');
        
        // Check if required dependencies are loaded
        if (!window.tradingAPI || !window.tradingCharts) {
            console.error('Required dependencies not loaded');
            this.showError('Dashboard dependencies not loaded. Please refresh the page.');
            return;
        }

        // Initialize event listeners
        this.setupEventListeners();
        
        // Initialize charts
        if (!tradingCharts.initializeCharts()) {
            console.error('Failed to initialize charts');
        }
        
        // Load initial data
        await this.loadAllData();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        console.log('Trading Dashboard initialized successfully');
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Settings button
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.openSettings());
        }

        // Settings modal controls
        const closeSettingsBtn = document.getElementById('closeSettingsBtn');
        if (closeSettingsBtn) {
            closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        }

        const saveSettingsBtn = document.getElementById('saveSettingsBtn');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        }

        const resetSettingsBtn = document.getElementById('resetSettingsBtn');
        if (resetSettingsBtn) {
            resetSettingsBtn.addEventListener('click', () => this.resetSettings());
        }

        const testConnectionBtn = document.getElementById('testConnectionBtn');
        if (testConnectionBtn) {
            testConnectionBtn.addEventListener('click', () => this.testConnection());
        }

        // Close modal when clicking outside
        const settingsModal = document.getElementById('settingsModal');
        if (settingsModal) {
            settingsModal.addEventListener('click', (e) => {
                if (e.target === settingsModal) {
                    this.closeSettings();
                }
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.handleRefresh());
        }

        // Retry button
        const retryBtn = document.getElementById('retryBtn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.loadAllData());
        }

        // Trade table sorting
        const sortableHeaders = document.querySelectorAll('.trades-table th.sortable');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const field = header.dataset.sort;
                this.handleSort(field);
            });
        });

        // Filter controls
        const symbolFilter = document.getElementById('symbolFilter');
        if (symbolFilter) {
            symbolFilter.addEventListener('change', (e) => {
                this.currentFilters.symbol = e.target.value;
                this.filterAndDisplayTrades();
            });
        }

        const tradesLimit = document.getElementById('tradesLimit');
        if (tradesLimit) {
            tradesLimit.addEventListener('change', (e) => {
                this.currentFilters.limit = parseInt(e.target.value);
                this.loadTradeHistory();
            });
        }

        // Chart period selectors
        const volumePeriod = document.getElementById('volumePeriod');
        if (volumePeriod) {
            volumePeriod.addEventListener('change', (e) => {
                this.updateVolumeChart(parseInt(e.target.value));
            });
        }

        const pnlPeriod = document.getElementById('pnlPeriod');
        if (pnlPeriod) {
            pnlPeriod.addEventListener('change', (e) => {
                this.updatePnLChart(parseInt(e.target.value));
            });
        }

        // Window resize handler for charts
        window.addEventListener('resize', () => {
            tradingCharts.resizeCharts();
        });

        // Visibility change handler to pause/resume refresh
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoRefresh();
            } else {
                this.startAutoRefresh();
            }
        });
    }

    /**
     * Load all dashboard data
     */
    async loadAllData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(true);
        this.hideError();

        try {
            // Load data in parallel
            const [statsData, tradesData, chartData, accountData] = await Promise.all([
                tradingAPI.getTradingStats(),
                tradingAPI.getTradeHistory(this.currentFilters),
                tradingAPI.getChartData(),
                tradingAPI.getAccountSummary()
            ]);

            // Update all components
            this.updateStatistics(statsData, accountData);
            this.updateTradeHistory(tradesData.trades);
            this.updateCharts(chartData);
            this.updateSymbolFilter(tradesData.trades);
            this.updateSymbolBreakdown(tradesData.trades);
            this.updateConnectionStatus(true);
            this.updateLastRefreshed();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError(`Failed to load data: ${error.message}`);
            this.updateConnectionStatus(false, error.message);
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    /**
     * Update statistics cards
     */
    updateStatistics(stats, account) {
        // Total P&L (simplified calculation)
        const totalPnl = this.calculateTotalPnL(stats);
        const pnlElement = document.getElementById('totalPnl');
        if (pnlElement) {
            pnlElement.textContent = DataFormatter.formatCurrency(totalPnl);
            pnlElement.className = `stat-value ${DataFormatter.getChangeColorClass(totalPnl)}`;
        }

        // Success Rate
        const successRate = stats.success_rate || 0;
        const successRateElement = document.getElementById('successRate');
        if (successRateElement) {
            successRateElement.textContent = DataFormatter.formatPercentage(successRate);
        }

        const completedTradesElement = document.getElementById('completedTrades');
        if (completedTradesElement) {
            completedTradesElement.textContent = `${stats.completed_trades || 0} completed trades`;
        }

        // Total Trades
        const totalTradesElement = document.getElementById('totalTrades');
        if (totalTradesElement) {
            totalTradesElement.textContent = DataFormatter.formatNumber(stats.total_trades || 0, 0);
        }

        const buyTradesElement = document.getElementById('buyTrades');
        if (buyTradesElement) {
            buyTradesElement.textContent = DataFormatter.formatNumber(stats.buy_trades || 0, 0);
        }

        const sellTradesElement = document.getElementById('sellTrades');
        if (sellTradesElement) {
            sellTradesElement.textContent = DataFormatter.formatNumber(stats.sell_trades || 0, 0);
        }

        // Total Volume
        const totalVolumeElement = document.getElementById('totalVolume');
        if (totalVolumeElement) {
            totalVolumeElement.textContent = DataFormatter.formatCurrency(stats.total_volume || 0);
        }

        // Account Balance
        const accountBalanceElement = document.getElementById('accountBalance');
        if (accountBalanceElement) {
            const balance = account?.perp_account_value || 0;
            accountBalanceElement.textContent = `Account: ${DataFormatter.formatCurrency(balance)}`;
        }
    }

    /**
     * Calculate total P&L (simplified)
     */
    calculateTotalPnL(stats) {
        // This is a simplified calculation
        // In a real scenario, you'd calculate based on actual entry/exit prices
        const volume = stats.total_volume || 0;
        const successRate = stats.success_rate || 0;
        
        // Assume average 1% profit per successful trade
        const estimatedPnL = (volume * (successRate / 100) * 0.01) - (volume * (1 - successRate / 100) * 0.005);
        return estimatedPnL;
    }

    /**
     * Update trade history table
     */
    updateTradeHistory(trades) {
        this.allTrades = trades || [];
        this.filterAndDisplayTrades();
        
        // Update trades count
        const tradesCountElement = document.getElementById('tradesCount');
        if (tradesCountElement) {
            tradesCountElement.textContent = this.allTrades.length;
        }
    }

    /**
     * Filter and display trades based on current filters and sorting
     */
    filterAndDisplayTrades() {
        let filteredTrades = [...this.allTrades];

        // Apply symbol filter
        if (this.currentFilters.symbol) {
            filteredTrades = filteredTrades.filter(trade => 
                trade.symbol === this.currentFilters.symbol
            );
        }

        // Apply sorting
        filteredTrades.sort((a, b) => {
            const field = this.currentSort.field;
            const direction = this.currentSort.direction;
            
            let aVal = a[field];
            let bVal = b[field];
            
            // Handle different data types
            if (field === 'trade_timestamp') {
                aVal = new Date(aVal);
                bVal = new Date(bVal);
            } else if (['amount', 'price', 'total_value'].includes(field)) {
                aVal = parseFloat(aVal) || 0;
                bVal = parseFloat(bVal) || 0;
            } else {
                aVal = String(aVal).toLowerCase();
                bVal = String(bVal).toLowerCase();
            }
            
            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        });

        this.displayTradesTable(filteredTrades);
    }

    /**
     * Display trades in the table
     */
    displayTradesTable(trades) {
        const tbody = document.getElementById('tradesTableBody');
        if (!tbody) return;

        if (!trades || trades.length === 0) {
            tbody.innerHTML = '<tr class="no-data"><td colspan="7">No trades found</td></tr>';
            return;
        }

        const rows = trades.map(trade => {
            const timestamp = DataFormatter.formatRelativeTime(trade.trade_timestamp);
            const symbol = trade.symbol || '--';
            const type = trade.trade_type || '--';
            const amount = DataFormatter.formatNumber(trade.amount || 0, 4);
            const price = DataFormatter.formatCurrency(trade.price || 0);
            const totalValue = DataFormatter.formatCurrency(trade.total_value || 0);
            const status = trade.status || 'unknown';

            return `
                <tr>
                    <td title="${DataFormatter.formatDate(trade.trade_timestamp)}">${timestamp}</td>
                    <td><strong>${symbol}</strong></td>
                    <td><span class="${DataFormatter.getTradeTypeClass(type)}">${type.toUpperCase()}</span></td>
                    <td>${amount}</td>
                    <td>${price}</td>
                    <td>${totalValue}</td>
                    <td><span class="${DataFormatter.getStatusClass(status)}">${status}</span></td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = rows;
    }

    /**
     * Handle table sorting
     */
    handleSort(field) {
        if (this.currentSort.field === field) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.field = field;
            this.currentSort.direction = 'desc';
        }

        // Update sort indicators
        document.querySelectorAll('.trades-table th.sortable').forEach(th => {
            const indicator = th.querySelector('.sort-indicator');
            if (indicator) {
                if (th.dataset.sort === field) {
                    indicator.textContent = this.currentSort.direction === 'asc' ? '↑' : '↓';
                } else {
                    indicator.textContent = '↕️';
                }
            }
        });

        this.filterAndDisplayTrades();
    }

    /**
     * Update symbol filter dropdown
     */
    updateSymbolFilter(trades) {
        const symbolFilter = document.getElementById('symbolFilter');
        if (!symbolFilter) return;

        const symbols = DataFormatter.extractSymbols(trades);
        const currentValue = symbolFilter.value;

        symbolFilter.innerHTML = '<option value="">All Symbols</option>';
        symbols.forEach(symbol => {
            const option = document.createElement('option');
            option.value = symbol;
            option.textContent = symbol;
            if (symbol === currentValue) {
                option.selected = true;
            }
            symbolFilter.appendChild(option);
        });
    }

    /**
     * Update symbol breakdown section
     */
    updateSymbolBreakdown(trades) {
        const symbolsGrid = document.getElementById('symbolsGrid');
        if (!symbolsGrid) return;

        const grouped = DataFormatter.groupTradesBySymbol(trades);
        const symbols = Object.values(grouped);

        if (symbols.length === 0) {
            symbolsGrid.innerHTML = '<div class="symbol-card placeholder"><h4>No trading data available</h4></div>';
            return;
        }

        const cards = symbols.map(symbolData => {
            const volume = DataFormatter.formatCurrency(symbolData.totalVolume);
            const trades = symbolData.totalTrades;
            const buyRatio = symbolData.totalTrades > 0 ? 
                Math.round((symbolData.buyTrades / symbolData.totalTrades) * 100) : 0;

            return `
                <div class="symbol-card">
                    <h4>${symbolData.symbol}</h4>
                    <p>Volume: ${volume}</p>
                    <p>Trades: ${trades}</p>
                    <p>Buy Ratio: ${buyRatio}%</p>
                </div>
            `;
        }).join('');

        symbolsGrid.innerHTML = cards;
    }

    /**
     * Update charts with new data
     */
    updateCharts(chartData) {
        if (!chartData) return;

        // Update volume chart
        this.updateVolumeChart(30, chartData.volume_data);
        
        // Update P&L chart
        this.updatePnLChart(30, chartData.pnl_data);
    }

    /**
     * Update volume chart with period filter
     */
    updateVolumeChart(days, data = null) {
        if (!data) {
            // If no data provided, we need to fetch it
            this.loadChartData().then(chartData => {
                if (chartData?.volume_data) {
                    const filteredData = tradingCharts.filterDataByDays(chartData.volume_data, days);
                    tradingCharts.updateChart('volumeChart', filteredData, 'volume');
                }
            });
        } else {
            const filteredData = tradingCharts.filterDataByDays(data, days);
            tradingCharts.updateChart('volumeChart', filteredData, 'volume');
        }
    }

    /**
     * Update P&L chart with period filter
     */
    updatePnLChart(days, data = null) {
        if (!data) {
            // If no data provided, we need to fetch it
            this.loadChartData().then(chartData => {
                if (chartData?.pnl_data) {
                    const filteredData = tradingCharts.filterDataByDays(chartData.pnl_data, days);
                    tradingCharts.updateChart('pnlChart', filteredData, 'pnl');
                }
            });
        } else {
            const filteredData = tradingCharts.filterDataByDays(data, days);
            tradingCharts.updateChart('pnlChart', filteredData, 'pnl');
        }
    }

    /**
     * Load only chart data
     */
    async loadChartData() {
        try {
            return await tradingAPI.getChartData();
        } catch (error) {
            console.error('Error loading chart data:', error);
            return null;
        }
    }

    /**
     * Load only trade history
     */
    async loadTradeHistory() {
        try {
            const tradesData = await tradingAPI.getTradeHistory(this.currentFilters);
            this.updateTradeHistory(tradesData.trades);
            this.updateSymbolFilter(tradesData.trades);
            this.updateSymbolBreakdown(tradesData.trades);
        } catch (error) {
            console.error('Error loading trade history:', error);
        }
    }

    /**
     * Handle refresh button click
     */
    async handleRefresh() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn && !this.isLoading) {
            refreshBtn.classList.add('loading');
            await this.loadAllData();
            refreshBtn.classList.remove('loading');
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing interval
        
        this.refreshInterval = setInterval(() => {
            if (!document.hidden && !this.isLoading) {
                this.loadAllData();
            }
        }, this.refreshIntervalMs);
        
        console.log(`Auto-refresh started (${this.refreshIntervalMs / 1000}s interval)`);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    /**
     * Show/hide loading overlay
     */
    showLoading(show) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            if (show) {
                loadingOverlay.classList.remove('hidden');
            } else {
                loadingOverlay.classList.add('hidden');
            }
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorMessage && errorText) {
            errorText.textContent = message;
            errorMessage.classList.remove('hidden');
        }
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorMessage = document.getElementById('errorMessage');
        if (errorMessage) {
            errorMessage.classList.add('hidden');
        }
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(connected, error = null) {
        const statusIndicator = document.getElementById('connectionStatus');
        const connectionText = document.getElementById('connectionText');
        
        if (statusIndicator && connectionText) {
            if (connected) {
                statusIndicator.textContent = '🟢';
                connectionText.textContent = 'Connected';
            } else {
                statusIndicator.textContent = '🔴';
                connectionText.textContent = error ? `Disconnected: ${error}` : 'Disconnected';
            }
        }
    }

    /**
     * Update last refreshed timestamp
     */
    updateLastRefreshed() {
        const lastUpdated = document.getElementById('lastUpdated');
        if (lastUpdated) {
            lastUpdated.textContent = new Date().toLocaleTimeString();
        }
    }

    /**
     * Open settings modal
     */
    openSettings() {
        const settingsModal = document.getElementById('settingsModal');
        const apiEndpointInput = document.getElementById('apiEndpoint');
        const currentEndpointDiv = document.getElementById('currentEndpoint');
        const refreshIntervalSelect = document.getElementById('refreshInterval');

        if (settingsModal) {
            // Populate current values
            if (apiEndpointInput) {
                apiEndpointInput.value = tradingAPI.getCurrentBaseURL();
            }
            if (currentEndpointDiv) {
                currentEndpointDiv.textContent = tradingAPI.getCurrentBaseURL();
            }
            if (refreshIntervalSelect) {
                refreshIntervalSelect.value = (this.refreshIntervalMs / 1000).toString();
            }

            settingsModal.classList.remove('hidden');
        }
    }

    /**
     * Close settings modal
     */
    closeSettings() {
        const settingsModal = document.getElementById('settingsModal');
        if (settingsModal) {
            settingsModal.classList.add('hidden');
        }
    }

    /**
     * Save settings
     */
    async saveSettings() {
        const apiEndpointInput = document.getElementById('apiEndpoint');
        const refreshIntervalSelect = document.getElementById('refreshInterval');

        if (apiEndpointInput && refreshIntervalSelect) {
            const newEndpoint = apiEndpointInput.value.trim();
            const newInterval = parseInt(refreshIntervalSelect.value) * 1000;

            // Validate URL
            if (newEndpoint && !this.isValidUrl(newEndpoint)) {
                alert('Please enter a valid URL');
                return;
            }

            // Update API endpoint
            if (newEndpoint && newEndpoint !== tradingAPI.getCurrentBaseURL()) {
                tradingAPI.updateBaseURL(newEndpoint);
                
                // Test the new connection
                const testResult = await this.testConnection(false);
                if (!testResult) {
                    const confirm = window.confirm(
                        'Cannot connect to the new endpoint. Do you want to save it anyway?'
                    );
                    if (!confirm) {
                        return;
                    }
                }
            }

            // Update refresh interval
            if (newInterval !== this.refreshIntervalMs) {
                this.refreshIntervalMs = newInterval;
                this.startAutoRefresh(); // Restart with new interval
                
                // Store in localStorage
                try {
                    localStorage.setItem('autoTrade_refreshInterval', newInterval.toString());
                } catch (error) {
                    console.warn('Cannot store refresh interval:', error);
                }
            }

            this.closeSettings();
            this.showNotification('Settings saved successfully!', 'success');
            
            // Reload data with new settings
            this.loadAllData();
        }
    }

    /**
     * Reset settings to default
     */
    resetSettings() {
        const confirm = window.confirm('Reset all settings to default values?');
        if (confirm) {
            tradingAPI.resetToDefault();
            this.refreshIntervalMs = 30000;
            
            // Clear localStorage
            try {
                localStorage.removeItem('autoTrade_refreshInterval');
            } catch (error) {
                console.warn('Cannot clear localStorage:', error);
            }

            this.closeSettings();
            this.startAutoRefresh();
            this.showNotification('Settings reset to default', 'info');
            this.loadAllData();
        }
    }

    /**
     * Test API connection
     */
    async testConnection(showResult = true) {
        const testBtn = document.getElementById('testConnectionBtn');
        
        if (testBtn) {
            testBtn.classList.add('testing');
            testBtn.textContent = 'Testing...';
        }

        try {
            const result = await tradingAPI.testConnection();
            
            if (showResult) {
                if (result.connected) {
                    this.showNotification('Connection successful!', 'success');
                } else {
                    this.showNotification(`Connection failed: ${result.error}`, 'error');
                }
            }

            return result.connected;
        } catch (error) {
            if (showResult) {
                this.showNotification(`Connection test failed: ${error.message}`, 'error');
            }
            return false;
        } finally {
            if (testBtn) {
                testBtn.classList.remove('testing');
                testBtn.textContent = 'Test Connection';
            }
        }
    }

    /**
     * Validate URL
     */
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1001;
                display: none;
                max-width: 300px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            `;
            document.body.appendChild(notification);
        }

        // Set colors based on type
        let backgroundColor;
        switch (type) {
            case 'success':
                backgroundColor = '#48bb78';
                break;
            case 'error':
                backgroundColor = '#f56565';
                break;
            case 'info':
            default:
                backgroundColor = '#4299e1';
                break;
        }

        notification.textContent = message;
        notification.style.backgroundColor = backgroundColor;
        notification.style.display = 'block';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    /**
     * Load stored settings
     */
    loadStoredSettings() {
        try {
            const storedInterval = localStorage.getItem('autoTrade_refreshInterval');
            if (storedInterval) {
                this.refreshIntervalMs = parseInt(storedInterval);
            }
        } catch (error) {
            console.warn('Cannot load stored settings:', error);
        }
    }

    /**
     * Cleanup when dashboard is destroyed
     */
    destroy() {
        this.stopAutoRefresh();
        tradingCharts.destroyAllCharts();
        console.log('Trading Dashboard destroyed');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create global dashboard instance
    window.dashboard = new TradingDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});

console.log('Dashboard module loaded successfully');