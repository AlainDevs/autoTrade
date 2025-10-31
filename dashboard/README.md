# AutoTrade Dashboard

A comprehensive web-based dashboard for monitoring your AutoTrade trading activity, displaying real-time statistics, trade history, and performance analytics.

## 🚀 Features

- **Real-time Statistics**: Total P&L, success rate, trade count, and volume
- **Trade History Table**: Sortable, filterable table of all trades
- **Interactive Charts**: Volume and P&L visualization over time
- **Symbol Breakdown**: Trading activity by cryptocurrency symbol
- **Auto-refresh**: Real-time data updates every 30 seconds
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark Theme**: Professional trading interface optimized for extended use

## 📋 Prerequisites

- AutoTrade server running with Appwrite integration configured
- Modern web browser with JavaScript enabled
- Internet connection for Chart.js CDN

## 🛠️ Setup

### 1. Verify AutoTrade Server

Ensure your AutoTrade server is running:

```bash
# Start the server
poetry run python run.py

# Or for production
poetry run gunicorn --bind 0.0.0.0:28791 "run:app"
```

### 2. Access the Dashboard

Open your web browser and navigate to:

```
https://28791--main--hypertrade--admin.coder.000164.xyz/dashboard
```

Or for local development:
```
http://localhost:28791/dashboard
```

### 3. Configure API Endpoint (if needed)

The dashboard now supports configurable API endpoints:

1. Click the **Settings** button (⚙️) in the top-right corner
2. Enter your AutoTrade server URL in the "API Endpoint URL" field
3. Click "Test Connection" to verify connectivity
4. Click "Save Settings" to apply changes

**Default endpoint**: `https://28791--main--hypertrade--admin.coder.000164.xyz`

Settings are automatically saved in your browser's local storage.

## 📊 Dashboard Sections

### Statistics Cards
- **Total P&L**: Estimated profit/loss based on trading activity
- **Success Rate**: Percentage of completed trades
- **Total Trades**: Count of buy/sell transactions
- **Total Volume**: Sum of all trading volume

### Performance Charts
- **Trading Volume**: Bar chart showing daily trading volume
- **Cumulative P&L**: Line chart tracking profit/loss over time
- **Period Filters**: View data for 7, 30, or 90 days

### Trade History Table
- **Sortable Columns**: Click headers to sort by any field
- **Symbol Filter**: Filter trades by cryptocurrency
- **Real-time Updates**: Automatically refreshes with new trades
- **Trade Details**: Time, symbol, type, amount, price, value, status

### Symbol Breakdown
- **Per-Symbol Analytics**: Volume and trade count by cryptocurrency
- **Buy/Sell Ratios**: Trading direction preferences per symbol

## 🔧 Configuration

### Auto-refresh Settings

The dashboard automatically refreshes every 30 seconds. To modify this:

1. Edit `dashboard/js/dashboard.js`
2. Change the `refreshIntervalMs` value (in milliseconds)
3. Refresh the browser

### Chart Time Periods

Default chart periods can be modified in the JavaScript files:
- Volume chart: `dashboard/js/dashboard.js` → `updateVolumeChart()`
- P&L chart: `dashboard/js/dashboard.js` → `updatePnLChart()`

## 🎨 Customization

### Theme Colors

Edit `dashboard/css/dashboard.css` to customize colors:

```css
:root {
    --primary-bg: #0d1421;     /* Main background */
    --secondary-bg: #1a202c;   /* Card backgrounds */
    --success-color: #48bb78;  /* Profit/success color */
    --error-color: #f56565;    /* Loss/error color */
    /* ... other variables */
}
```

### Adding New Metrics

To add new statistics:

1. Update the API endpoint in `src/routes/dashboard_routes.py`
2. Add corresponding HTML elements in `dashboard/index.html`
3. Update the JavaScript in `dashboard/js/dashboard.js`

## 🐛 Troubleshooting

### Dashboard Not Loading
- Verify AutoTrade server is running
- Check browser console for JavaScript errors
- Ensure all dashboard files are in the correct directory

### No Data Displayed
- Confirm Appwrite integration is working
- Check that trades exist in your database
- Verify API endpoints are responding (use test script)

### Charts Not Rendering
- Ensure Chart.js CDN is accessible
- Check browser console for errors
- Verify chart data format is correct

### Connection Issues
- Check server logs for API errors
- Verify Flask routes are registered correctly
- Test individual API endpoints with curl or browser

## 📱 Mobile Support

The dashboard is fully responsive and optimized for mobile devices:
- Touch-friendly interface
- Responsive tables with horizontal scrolling
- Optimized chart sizing for small screens
- Collapsible navigation elements

## 🔒 Security Notes

- Dashboard uses read-only API endpoints
- No sensitive data is exposed in client-side code
- All trading operations still require webhook authentication
- Dashboard access follows same server security as main application

## 📈 Performance

- Lightweight JavaScript (~15KB total)
- Efficient data fetching with minimal API calls
- Chart.js provides hardware-accelerated rendering
- Automatic cleanup of resources on page unload

## 🔄 Updates

To update the dashboard:
1. Replace dashboard files with new versions
2. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
3. Restart AutoTrade server if API changes were made

## 📞 Support

For issues with the dashboard:
1. Run the test script: `python test_dashboard.py`
2. Check browser developer console for errors
3. Review AutoTrade server logs
4. Ensure Appwrite configuration is correct

## 🎯 API Endpoints

The dashboard uses these API endpoints:

- `GET /api/trading-stats` - Trading statistics
- `GET /api/trade-history` - Trade history with filtering
- `GET /api/chart-data` - Chart visualization data
- `GET /api/account-summary` - Account balance information
- `GET /dashboard` - Dashboard HTML page
- `GET /dashboard/<asset>` - Static assets (CSS, JS)

## 📝 License

This dashboard is part of the AutoTrade project and follows the same license terms.