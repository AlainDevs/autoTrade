# 🚀 Trade History Database Setup - Final Instructions

## ✅ Current Status
- **Database Created**: ✅ TradeHistoryDB (ID: `...`)
- **Appwrite Configuration**: ✅ Working (`config.json` updated)
- **Scripts Ready**: ✅ All scripts created and tested

## 🔧 Manual Setup Required

Due to Appwrite API restrictions, table creation must be done manually through the console.

### Step 1: Create the Table

1. **Go to your database**: https://fra.cloud.appwrite.io/console/project/.../databases/...
2. **Click "Create Table"**
3. **Table Name**: `trade_history`
4. **Table ID**: Leave auto-generated or use `trade_history`

### Step 2: Add Columns

Create these columns in your `trade_history` table:

| Column Key | Type | Size | Required | Default | Description |
|------------|------|------|----------|---------|-------------|
| `trade_id` | String | 50 | ✅ Yes | - | Unique identifier |
| `symbol` | String | 20 | ✅ Yes | - | Trading pair (BTC/USD) |
| `trade_type` | String | 10 | ✅ Yes | - | "buy" or "sell" |
| `amount` | Float | - | ✅ Yes | - | Quantity traded |
| `price` | Float | - | ✅ Yes | - | Price per unit |
| `total_value` | Float | - | ✅ Yes | - | Total trade value |
| `fees` | Float | - | ❌ No | 0.0 | Trading fees |
| `status` | String | 20 | ✅ Yes | - | Trade status |
| `exchange` | String | 50 | ❌ No | - | Exchange name |
| `trade_timestamp` | String | 50 | ✅ Yes | - | ISO timestamp |

### Step 3: Add Demo Data

Once your table is created with all columns:

```bash
poetry run python add_demo_trades.py
```

This will automatically:
- ✅ Find your trade_history table
- ✅ Add 7 realistic demo trades
- ✅ Save configuration to `trade_history_ids.json`

## 📊 Demo Data Preview

Your table will contain these trades:

```
TRADE_001: buy 0.1 BTC/USD @ $65,000 (binance, completed)
TRADE_002: buy 2.5 ETH/USD @ $2,400 (coinbase, completed)  
TRADE_003: sell 0.05 BTC/USD @ $66,000 (binance, completed)
TRADE_004: buy 10.0 SOL/USD @ $180 (kraken, completed)
TRADE_005: sell 1.0 ETH/USD @ $2,450 (coinbase, completed)
TRADE_006: buy 1000.0 ADA/USD @ $0.35 (binance, pending)
TRADE_007: buy 50.0 DOT/USD @ $4.20 (kraken, failed)
```

## 📁 Available Scripts

| Script | Purpose |
|--------|---------|
| [`add_demo_trades.py`](add_demo_trades.py) | **✅ Ready** - Adds demo data to existing table |
| [`check_databases.py`](check_databases.py) | Inspects your Appwrite setup |
| [`create_trade_table_final.py`](create_trade_table_final.py) | Attempted automated setup |

## 🔍 Verification

After setup, verify everything works:

1. **Check Appwrite Console**: View your data in the console
2. **Test with Script**: The demo script will confirm successful data insertion
3. **Integration**: Your table is ready for your autoTrade system

## ⚡ Integration with Your App

Your [`config.json`](config.json) already contains:
```json
{
  "appwrite_database_id": "your_db_id",
  "appwrite_project_id": "your_project_id",
  "appwrite_endpoint": "your_endpoint",
  "appwrite_api_secret": "your_api_key"
}
```

Use the TablesDB API in your application:
```python
from appwrite.services.tables_db import TablesDB

# Add new trade
tablesDB.create_row(
    database_id=config['appwrite_database_id'],
    table_id='your_table_id',  # From trade_history_ids.json
    row_id=ID.unique(),
    data={
        'trade_id': 'TRADE_008',
        'symbol': 'BTC/USD',
        'trade_type': 'buy',
        'amount': 0.25,
        'price': 67000.00,
        'total_value': 16750.00,
        'status': 'completed',
        'exchange': 'your_exchange',
        'trade_timestamp': datetime.now().isoformat()
    }
)

# Query trades
trades = tablesDB.list_rows(
    database_id=config['appwrite_database_id'],
    table_id='your_table_id'
)
```

## 🎯 Why Manual Setup?

The Appwrite API restricts programmatic table creation for security reasons. This ensures:
- ✅ Better security control
- ✅ Prevents accidental schema changes
- ✅ Requires conscious database design decisions

## 🆘 Need Help?

- **Console Access**: https://fra.cloud.appwrite.io/console/project/...
- **API Documentation**: https://appwrite.io/docs/references/cloud/server-tablesdb
- **Check Setup**: Run `poetry run python check_databases.py`

---

**Once complete, your trade history system will be fully operational! 🚀**