// API Module - Handles all communication with the Flask backend
class TradingAPI {
    constructor(baseURL = '') {
        // Default to the provided domain, fallback to localhost
        this.defaultBaseURL = 'https://28791--main--hypertrade--admin.coder.000164.xyz';
        this.baseURL = baseURL || this.getStoredBaseURL() || this.defaultBaseURL;
        this.endpoints = {
            tradingStats: '/api/trading-stats',
            tradeHistory: '/api/trade-history',
            chartData: '/api/chart-data',
            accountSummary: '/api/account-summary'
        };
    }

    /**
     * Get stored base URL from localStorage
     */
    getStoredBaseURL() {
        try {
            return localStorage.getItem('autoTrade_apiEndpoint');
        } catch (error) {
            console.warn('Cannot access localStorage:', error);
            return null;
        }
    }

    /**
     * Store base URL in localStorage
     */
    setStoredBaseURL(url) {
        try {
            localStorage.setItem('autoTrade_apiEndpoint', url);
            this.baseURL = url;
            console.log(`API endpoint updated to: ${url}`);
        } catch (error) {
            console.warn('Cannot store in localStorage:', error);
        }
    }

    /**
     * Update the base URL for API calls
     */
    updateBaseURL(newBaseURL) {
        this.baseURL = newBaseURL;
        this.setStoredBaseURL(newBaseURL);
    }

    /**
     * Get current base URL
     */
    getCurrentBaseURL() {
        return this.baseURL;
    }

    /**
     * Reset to default URL
     */
    resetToDefault() {
        this.updateBaseURL(this.defaultBaseURL);
    }

    /**
     * Generic API request handler with error handling
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            console.log(`Making API request to: ${url}`);
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'error') {
                throw new Error(data.message || 'API returned error status');
            }
            
            console.log(`API response from ${endpoint}:`, data);
            return data;
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw new Error(`Failed to fetch data: ${error.message}`);
        }
    }

    /**
     * Get comprehensive trading statistics
     */
    async getTradingStats() {
        try {
            const response = await this.makeRequest(this.endpoints.tradingStats);
            return response.data || {};
        } catch (error) {
            console.error('Error fetching trading stats:', error);
            throw error;
        }
    }

    /**
     * Get trade history with optional filtering
     */
    async getTradeHistory(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            if (params.limit) queryParams.append('limit', params.limit);
            if (params.symbol) queryParams.append('symbol', params.symbol);
            
            const endpoint = `${this.endpoints.tradeHistory}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
            const response = await this.makeRequest(endpoint);
            
            return {
                trades: response.data || [],
                count: response.count || 0
            };
        } catch (error) {
            console.error('Error fetching trade history:', error);
            throw error;
        }
    }

    /**
     * Get formatted chart data for visualizations
     */
    async getChartData() {
        try {
            const response = await this.makeRequest(this.endpoints.chartData);
            return response.data || { volume_data: [], pnl_data: [] };
        } catch (error) {
            console.error('Error fetching chart data:', error);
            throw error;
        }
    }

    /**
     * Get current account summary and balance
     */
    async getAccountSummary() {
        try {
            const response = await this.makeRequest(this.endpoints.accountSummary);
            return response.data || {};
        } catch (error) {
            console.error('Error fetching account summary:', error);
            throw error;
        }
    }

    /**
     * Test API connectivity
     */
    async testConnection() {
        try {
            await this.makeRequest('/balance');
            return { connected: true, timestamp: new Date().toISOString() };
        } catch (error) {
            console.error('Connection test failed:', error);
            return { connected: false, error: error.message, timestamp: new Date().toISOString() };
        }
    }
}

// Utility functions for data formatting
class DataFormatter {
    /**
     * Format currency values
     */
    static formatCurrency(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '$--';
        }
        
        const num = parseFloat(value);
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    }

    /**
     * Format percentage values
     */
    static formatPercentage(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '--%';
        }
        
        const num = parseFloat(value);
        return `${num.toFixed(decimals)}%`;
    }

    /**
     * Format numbers with appropriate suffixes (K, M, B)
     */
    static formatNumber(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '--';
        }
        
        const num = parseFloat(value);
        
        if (Math.abs(num) >= 1000000000) {
            return (num / 1000000000).toFixed(decimals) + 'B';
        } else if (Math.abs(num) >= 1000000) {
            return (num / 1000000).toFixed(decimals) + 'M';
        } else if (Math.abs(num) >= 1000) {
            return (num / 1000).toFixed(decimals) + 'K';
        }
        
        return num.toFixed(decimals);
    }

    /**
     * Format timestamp to readable date
     */
    static formatDate(timestamp, options = {}) {
        if (!timestamp) return '--';
        
        try {
            const date = new Date(timestamp);
            const defaultOptions = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            
            return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
        } catch (error) {
            console.error('Error formatting date:', error);
            return '--';
        }
    }

    /**
     * Format relative time (e.g., "2 hours ago")
     */
    static formatRelativeTime(timestamp) {
        if (!timestamp) return '--';
        
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            
            return this.formatDate(timestamp, { month: 'short', day: 'numeric' });
        } catch (error) {
            console.error('Error formatting relative time:', error);
            return '--';
        }
    }

    /**
     * Get trade type styling class
     */
    static getTradeTypeClass(tradeType) {
        switch (tradeType?.toLowerCase()) {
            case 'buy':
                return 'trade-type-buy';
            case 'sell':
                return 'trade-type-sell';
            default:
                return '';
        }
    }

    /**
     * Get status styling class
     */
    static getStatusClass(status) {
        switch (status?.toLowerCase()) {
            case 'completed':
                return 'trade-status completed';
            case 'pending':
                return 'trade-status pending';
            case 'failed':
                return 'trade-status failed';
            default:
                return 'trade-status';
        }
    }

    /**
     * Calculate percentage change between two values
     */
    static calculatePercentageChange(oldValue, newValue) {
        if (!oldValue || oldValue === 0) return 0;
        return ((newValue - oldValue) / oldValue) * 100;
    }

    /**
     * Get color class based on positive/negative value
     */
    static getChangeColorClass(value) {
        if (value > 0) return 'text-success';
        if (value < 0) return 'text-error';
        return '';
    }

    /**
     * Extract unique symbols from trades data
     */
    static extractSymbols(trades) {
        if (!Array.isArray(trades)) return [];
        
        const symbols = new Set();
        trades.forEach(trade => {
            if (trade.symbol) {
                symbols.add(trade.symbol);
            }
        });
        
        return Array.from(symbols).sort();
    }

    /**
     * Group trades by symbol for analysis
     */
    static groupTradesBySymbol(trades) {
        if (!Array.isArray(trades)) return {};
        
        const grouped = {};
        
        trades.forEach(trade => {
            const symbol = trade.symbol || 'Unknown';
            if (!grouped[symbol]) {
                grouped[symbol] = {
                    symbol,
                    trades: [],
                    totalVolume: 0,
                    totalTrades: 0,
                    buyTrades: 0,
                    sellTrades: 0
                };
            }
            
            grouped[symbol].trades.push(trade);
            grouped[symbol].totalTrades++;
            grouped[symbol].totalVolume += parseFloat(trade.total_value || 0);
            
            if (trade.trade_type?.toLowerCase() === 'buy') {
                grouped[symbol].buyTrades++;
            } else if (trade.trade_type?.toLowerCase() === 'sell') {
                grouped[symbol].sellTrades++;
            }
        });
        
        return grouped;
    }
}

// Export for use in other modules
window.TradingAPI = TradingAPI;
window.DataFormatter = DataFormatter;

// Create global API instance
window.tradingAPI = new TradingAPI();

console.log('Trading API module loaded successfully');