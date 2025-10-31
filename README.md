# 🚀 AutoTrade - Automated Trading System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Hyperliquid](https://img.shields.io/badge/Exchange-Hyperliquid-purple.svg)](https://hyperliquid.xyz/)
[![Appwrite](https://img.shields.io/badge/Database-Appwrite-red.svg)](https://appwrite.io/)

A professional-grade automated trading system that integrates TradingView signals with Hyperliquid perpetual futures trading, featuring comprehensive trade logging and portfolio management.

## ✨ Features

### 🎯 **Core Trading**
- **Webhook Integration**: Receive and execute TradingView alerts instantly
- **Position Management**: Smart position sizing with configurable leverage (1x-100x)
- **Risk Management**: Built-in stop-loss and take-profit automation
- **Trade Cooldowns**: Prevents over-trading with configurable intervals
- **One-Way Trading**: Enforces single-direction positions per asset

### 📊 **Advanced Analytics**
- **Real-Time Trade Logging**: Every trade automatically stored in Appwrite database
- **Performance Analytics**: Track success rates, volume, and P&L
- **Historical Data**: Query trade history by symbol, date, or status
- **Portfolio Tracking**: Monitor balances across perpetual and spot accounts

### 🛡️ **Security & Reliability**
- **Secure Webhooks**: Secret-based authentication for all signals
- **Error Handling**: Graceful degradation with comprehensive logging
- **Position Validation**: Prevents conflicting trades and validates market conditions
- **Configuration Management**: Environment-based settings for different trading modes

## 🏗️ Architecture

```
autoTrade/
├── src/
│   ├── routes/
│   │   ├── balance_routes.py    # Balance checking endpoints
│   │   └── webhook_routes.py    # TradingView webhook handler
│   └── services/
│       └── trading_service.py   # Core trading logic & Appwrite integration
├── setup_py/                   # Database setup utilities
├── config.json                 # Configuration file
└── run.py                      # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry (package manager)
- Hyperliquid account with API access
- Appwrite account for trade logging
- TradingView account (for signal generation)

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd autoTrade

# Install dependencies
poetry install
```

### 2. Configuration

Create and configure your `config.json`:

```json
{
    "comment": "Fill in your details below. is_mainnet should be true for live trading.",
    "is_mainnet": false,
    "secret_key": "0x[YOUR_ETHEREUM_PRIVATE_KEY]",
    "account_address": "0x[YOUR_ACCOUNT_ADDRESS]",
    "webhook_secret": "your_secure_webhook_secret",
    "trade_cooldown_seconds": 60,
    "appwrite_api_secret": "[YOUR_APPWRITE_API_KEY]",
    "appwrite_endpoint": "https://[REGION].cloud.appwrite.io/v1",
    "appwrite_project_id": "[YOUR_PROJECT_ID]",
    "appwrite_database_id": "[YOUR_DATABASE_ID]",
    "appwrite_table_id": "trade_history"
}
```

### 3. Database Setup

Set up your Appwrite trade history database:

```bash
# Add demo data and test connection
poetry run python setup_py/add_demo_trades.py

# Test the integration
poetry run python setup_py/test_appwrite_integration.py
```

### 4. Start the Server

```bash
# Development mode
poetry run python run.py

# Production mode (recommended)
poetry run gunicorn --bind 0.0.0.0:28791 "run:app"
```

Your server will be running at `http://localhost:28791`

## 📡 API Endpoints

### **Balance Check**
```http
GET /balance
```
Returns current account balances and verifies API connectivity.

**Response:**
```json
{
    "status": "success",
    "address": "0x...",
    "perp_account_value": "1000.0",
    "spot_balances": [...]
}
```

### **Trading Webhook**
```http
POST /webhook
```
Receives TradingView alerts and executes trades.

**Request Body:**
```json
{
    "secret": "your_webhook_secret",
    "action": "open",
    "coin": "BTC",
    "is_buy": true,
    "size_usd": 100,
    "leverage": 10,
    "tp_price": "5%",
    "sl_price": "2%",
    "slippage": 0.05
}
```

## 🎛️ Trading Configuration

### **Supported Actions**
- `open`: Open new position
- `close`: Close existing position

### **Position Parameters**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `coin` | string | Trading symbol | `"BTC"`, `"ETH"` |
| `is_buy` | boolean | Position direction | `true` (long), `false` (short) |
| `size_usd` | number | Position size in USD | `100.0` |
| `leverage` | integer | Leverage multiplier | `10` (1x-100x) |
| `tp_price` | string/number | Take profit target | `"5%"` or `65000` |
| `sl_price` | string/number | Stop loss level | `"2%"` or `60000` |
| `slippage` | number | Max slippage tolerance | `0.05` (5%) |

### **Price Formats**
- **Percentage**: `"5%"` or `0.05` (relative to entry price)
- **Absolute**: `65000` (exact price level)

## 📊 Trade History & Analytics

### **Automatic Logging**
Every trade is automatically logged to Appwrite with:
- Unique trade ID and timestamp
- Symbol, type (buy/sell), amount, price
- Total value, fees, status, exchange
- Complete audit trail for compliance

### **Query Trade History**
```python
from src.services.trading_service import TradingService

service = TradingService()

# Get recent trades
trades = service.get_trade_history(limit=50)

# Filter by symbol
btc_trades = service.get_trade_history(symbol="BTC/USD")

# Get trading statistics
stats = service.get_trading_stats()
print(f"Success rate: {stats['success_rate']}%")
print(f"Total volume: ${stats['total_volume']}")
```

## 🔧 TradingView Integration

### **Pine Script Example**
```pinescript
//@version=5
strategy("AutoTrade Signal", overlay=true)

// Entry conditions
long_condition = ta.crossover(ta.sma(close, 9), ta.sma(close, 21))
short_condition = ta.crossunder(ta.sma(close, 9), ta.sma(close, 21))

// Send webhook alerts
if long_condition
    alert('{"secret":"your_webhook_secret","action":"open","coin":"BTC","is_buy":true,"size_usd":100,"leverage":10,"tp_price":"3%","sl_price":"1.5%"}', alert.freq_once_per_bar)

if short_condition
    alert('{"secret":"your_webhook_secret","action":"open","coin":"BTC","is_buy":false,"size_usd":100,"leverage":10,"tp_price":"3%","sl_price":"1.5%"}', alert.freq_once_per_bar)
```

### **Webhook URL**
```
http://your-server.com:28791/webhook
```

## 🛡️ Security Best Practices

### **API Keys**
- Never commit `config.json` to version control
- Use environment variables in production
- Regularly rotate API keys
- Use testnet for development

### **Webhook Security**
- Always use strong webhook secrets
- Implement IP whitelisting if possible
- Monitor for unusual trading patterns
- Set up alerts for failed authentications

### **Risk Management**
```json
{
    "trade_cooldown_seconds": 60,     // Prevent rapid-fire trades
    "max_position_size": 1000,        // USD limit per position
    "daily_loss_limit": 500,          // Daily stop-loss
    "max_leverage": 20                // Leverage cap
}
```

## 🔍 Monitoring & Troubleshooting

### **Health Checks**
```bash
# Test API connectivity
curl http://localhost:28791/balance

# Test webhook endpoint
curl -X POST http://localhost:28791/webhook \
  -H "Content-Type: application/json" \
  -d '{"secret":"test","action":"close","coin":"BTC"}'
```

### **Common Issues**

**❌ "Trading service not initialized"**
- Check your `config.json` configuration
- Verify Ethereum private key format
- Ensure all required fields are present

**❌ "Invalid webhook secret"**
- Verify webhook secret matches in TradingView and config
- Check for extra spaces or special characters

**❌ "Position already exists"**
- AutoTrade enforces one-way trading
- Close existing positions before opening new ones
- Check current positions on Hyperliquid

**❌ "Appwrite connection failed"**
- Verify Appwrite credentials in config
- Check database and table IDs
- Ensure API key has correct permissions

### **Logs Location**
```bash
# Application logs
tail -f app.log

# Check trading service initialization
poetry run python -c "from src.services.trading_service import TradingService; TradingService()"
```

## 📈 Performance Optimization

### **Production Deployment**
```bash
# Use Gunicorn for production
poetry run gunicorn --workers 2 --bind 0.0.0.0:28791 --timeout 60 "run:app"

# With process manager
sudo systemctl enable autotrade
sudo systemctl start autotrade
```

### **Database Optimization**
- Index frequently queried fields (symbol, timestamp)
- Set up regular database backups
- Monitor query performance
- Archive old trades periodically

## 🧪 Testing

### **Unit Tests**
```bash
# Run integration tests
poetry run python setup_py/test_appwrite_integration.py

# Test trading service
poetry run python -c "
from src.services.trading_service import TradingService
service = TradingService()
print('✅ Service initialized successfully')
"
```

### **Manual Testing**
1. **Balance Check**: Visit `http://localhost:28791/balance`
2. **Webhook Test**: Send test JSON to `/webhook` endpoint
3. **Database Test**: Run Appwrite integration test
4. **TradingView Test**: Set up paper trading alerts

## 📚 Additional Resources

- **Hyperliquid Documentation**: [docs.hyperliquid.xyz](https://hyperliquid-python-sdk.readthedocs.io/)
- **Appwrite Guides**: [appwrite.io/docs](https://appwrite.io/docs)
- **TradingView Webhooks**: [tradingview.com/support/solutions](https://www.tradingview.com/support/solutions/)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Important**: This software is for educational and informational purposes only. Trading cryptocurrencies involves substantial risk and may result in significant financial losses. Always:

- Test thoroughly on testnet before live trading
- Start with small position sizes
- Never trade more than you can afford to lose
- Understand the risks of automated trading
- Comply with your local financial regulations

The authors are not responsible for any financial losses incurred through the use of this software.

---

## 🌟 Support

If you find this project helpful, please give it a ⭐ on GitHub!

For support, please open an issue or contact the maintainers.

**Happy Trading! 🚀📈**