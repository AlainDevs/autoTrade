# Trade History Database Setup Guide

## 🎯 Overview
This guide will help you complete the setup of your trade_history database in Appwrite with demo data.

## ✅ Current Status
- **Database Created**: `TradeHistoryDB` (ID: `...`)
- **Appwrite Configuration**: ✅ Working
- **Scripts Ready**: ✅ Available

## 📋 Manual Setup Required

Due to API restrictions, you need to manually create the collection and attributes in the Appwrite console.

### Step 1: Create Collection

1. Go to: https://fra.cloud.appwrite.io/console/project/.../databases/...
2. Click **"Create Collection"**
3. **Collection Name**: `trade_history`
4. **Collection ID**: Leave auto-generated or use `trade_history`
5. Click **Create**

### Step 2: Add Attributes

In your new collection, create these attributes:

| Attribute Key | Type | Size | Required | Default | Description |
|---------------|------|------|----------|---------|-------------|
| `trade_id` | String | 50 | ✅ Yes | - | Unique trade identifier |
| `symbol` | String | 20 | ✅ Yes | - | Trading pair (e.g., BTC/USD) |
| `trade_type` | String | 10 | ✅ Yes | - | buy or sell |
| `amount` | Float | - | ✅ Yes | - | Quantity traded |
| `price` | Float | - | ✅ Yes | - | Price per unit |
| `total_value` | Float | - | ✅ Yes | - | Total trade value |
| `fees` | Float | - | ❌ No | 0.0 | Trading fees |
| `status` | String | 20 | ✅ Yes | - | completed/pending/failed/cancelled |
| `exchange` | String | 50 | ❌ No | - | Exchange name |
| `trade_timestamp` | String | 50 | ✅ Yes | - | ISO timestamp |

### Step 3: Add Demo Data

Once your collection is ready:

1. Copy the **Collection ID** from the Appwrite console
2. Run the demo data script:
   ```bash
   poetry run python add_demo_data.py
   ```
3. Enter your Database ID: `...`
4. Enter your Collection ID when prompted

## 📊 Demo Data Included

The script will add 7 realistic trade records:

| Trade ID | Symbol | Type | Amount | Price | Exchange | Status |
|----------|---------|------|--------|-------|----------|--------|
| TRADE_001 | BTC/USD | buy | 0.1 | $65,000 | binance | completed |
| TRADE_002 | ETH/USD | buy | 2.5 | $2,400 | coinbase | completed |
| TRADE_003 | BTC/USD | sell | 0.05 | $66,000 | binance | completed |
| TRADE_004 | SOL/USD | buy | 10.0 | $180 | kraken | completed |
| TRADE_005 | ETH/USD | sell | 1.0 | $2,450 | coinbase | completed |
| TRADE_006 | ADA/USD | buy | 1000.0 | $0.35 | binance | pending |
| TRADE_007 | DOT/USD | buy | 50.0 | $4.20 | kraken | failed |

## 🔧 Available Scripts

- **`add_demo_data.py`** - Adds demo trades to your collection
- **`check_databases.py`** - Lists all databases and collections
- **`setup_trade_history_final.py`** - Complete setup script (requires manual database creation)

## 🎉 After Setup

Once complete, you'll have:
- ✅ TradeHistoryDB database
- ✅ trade_history collection with proper schema
- ✅ 7 demo trade records
- ✅ Configuration saved in `trade_history_ids.json`

## 📝 Using the Database

Your trade history database will be ready to:
- Store real trading data from your application
- Query trades by symbol, status, exchange, etc.
- Track trading performance and history
- Integrate with your existing autoTrade system

## 🔍 Verification

After setup, you can verify everything works by checking the Appwrite console or using the query examples in your application.

---

**Need Help?** 
- Check the Appwrite console for any error messages
- Ensure all attributes are created with correct types
- Verify your API key has the necessary permissions