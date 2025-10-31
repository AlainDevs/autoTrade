#!/usr/bin/env python3
"""
Script to create trade_history table using the TablesDB API and add demo data.
"""

import json
import time
from datetime import datetime, timedelta
from appwrite.client import Client
from appwrite.services.tables_db import TablesDB
from appwrite.id import ID

def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)

def setup_appwrite_client(config):
    """Initialize Appwrite client with configuration"""
    client = Client()
    client.set_endpoint(config['appwrite_endpoint'])
    client.set_project(config['appwrite_project_id'])
    client.set_key(config['appwrite_api_secret'])
    return client

def create_trade_table(tablesDB, database_id):
    """Create the trade_history table using TablesDB"""
    try:
        # Create table
        table = tablesDB.create_table(
            database_id=database_id,
            table_id=ID.unique(),
            name='trade_history'
        )
        print(f"✅ Created table: {table['name']} (ID: {table['$id']})")
        return table
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return None

def create_table_columns(tablesDB, database_id, table_id):
    """Create all columns for the trade_history table"""
    print(f"\n🔧 Creating table columns...")
    
    columns = [
        # Trade identifier - string column
        {
            'method': 'create_string_column',
            'params': {
                'key': 'trade_id',
                'size': 50,
                'required': True
            }
        },
        # Trading symbol (e.g., BTC/USD) - string column
        {
            'method': 'create_string_column',
            'params': {
                'key': 'symbol',
                'size': 20,
                'required': True
            }
        },
        # Trade type: buy or sell - string column
        {
            'method': 'create_string_column',
            'params': {
                'key': 'trade_type',
                'size': 10,
                'required': True
            }
        },
        # Amount of asset traded - float column
        {
            'method': 'create_float_column',
            'params': {
                'key': 'amount',
                'required': True
            }
        },
        # Price per unit - float column
        {
            'method': 'create_float_column',
            'params': {
                'key': 'price',
                'required': True
            }
        },
        # Total value of trade - float column
        {
            'method': 'create_float_column',
            'params': {
                'key': 'total_value',
                'required': True
            }
        },
        # Trading fees - float column (optional)
        {
            'method': 'create_float_column',
            'params': {
                'key': 'fees',
                'required': False,
                'default': 0.0
            }
        },
        # Trade status - string column
        {
            'method': 'create_string_column',
            'params': {
                'key': 'status',
                'size': 20,
                'required': True,
                'default': 'pending'
            }
        },
        # Exchange name - string column (optional)
        {
            'method': 'create_string_column',
            'params': {
                'key': 'exchange',
                'size': 50,
                'required': False
            }
        },
        # Trade timestamp - string column for ISO datetime
        {
            'method': 'create_string_column',
            'params': {
                'key': 'trade_timestamp',
                'size': 50,
                'required': True
            }
        }
    ]
    
    successful_columns = 0
    
    for column in columns:
        try:
            method = getattr(tablesDB, column['method'])
            result = method(
                database_id=database_id,
                table_id=table_id,
                **column['params']
            )
            print(f"  ✅ {column['params']['key']} ({column['method'].replace('create_', '').replace('_column', '')})")
            successful_columns += 1
            time.sleep(1)  # Wait between column creation to avoid rate limiting
        except Exception as e:
            print(f"  ❌ {column['params']['key']}: {e}")
    
    print(f"\n✅ Created {successful_columns}/{len(columns)} columns successfully")
    return successful_columns

def add_demo_data(tablesDB, database_id, table_id):
    """Add demo trading data to the table"""
    print(f"\n⏳ Waiting for columns to be ready...")
    time.sleep(5)  # Wait for columns to be fully created
    
    base_time = datetime.now() - timedelta(days=7)
    
    demo_trades = [
        {
            'trade_id': 'TRADE_001',
            'symbol': 'BTC/USD',
            'trade_type': 'buy',
            'amount': 0.1,
            'price': 65000.00,
            'total_value': 6500.00,
            'fees': 19.50,
            'status': 'completed',
            'exchange': 'binance',
            'trade_timestamp': (base_time + timedelta(hours=1)).isoformat()
        },
        {
            'trade_id': 'TRADE_002', 
            'symbol': 'ETH/USD',
            'trade_type': 'buy',
            'amount': 2.5,
            'price': 2400.00,
            'total_value': 6000.00,
            'fees': 18.00,
            'status': 'completed',
            'exchange': 'coinbase',
            'trade_timestamp': (base_time + timedelta(hours=3)).isoformat()
        },
        {
            'trade_id': 'TRADE_003',
            'symbol': 'BTC/USD', 
            'trade_type': 'sell',
            'amount': 0.05,
            'price': 66000.00,
            'total_value': 3300.00,
            'fees': 9.90,
            'status': 'completed',
            'exchange': 'binance',
            'trade_timestamp': (base_time + timedelta(hours=12)).isoformat()
        },
        {
            'trade_id': 'TRADE_004',
            'symbol': 'SOL/USD',
            'trade_type': 'buy',
            'amount': 10.0,
            'price': 180.00,
            'total_value': 1800.00,
            'fees': 5.40,
            'status': 'completed',
            'exchange': 'kraken',
            'trade_timestamp': (base_time + timedelta(days=1)).isoformat()
        },
        {
            'trade_id': 'TRADE_005',
            'symbol': 'ETH/USD',
            'trade_type': 'sell',
            'amount': 1.0,
            'price': 2450.00,
            'total_value': 2450.00,
            'fees': 7.35,
            'status': 'completed',
            'exchange': 'coinbase',
            'trade_timestamp': (base_time + timedelta(days=2)).isoformat()
        },
        {
            'trade_id': 'TRADE_006',
            'symbol': 'ADA/USD',
            'trade_type': 'buy',
            'amount': 1000.0,
            'price': 0.35,
            'total_value': 350.00,
            'fees': 1.05,
            'status': 'pending',
            'exchange': 'binance',
            'trade_timestamp': (base_time + timedelta(days=3)).isoformat()
        },
        {
            'trade_id': 'TRADE_007',
            'symbol': 'DOT/USD',
            'trade_type': 'buy',
            'amount': 50.0,
            'price': 4.20,
            'total_value': 210.00,
            'fees': 0.63,
            'status': 'failed',
            'exchange': 'kraken',
            'trade_timestamp': (base_time + timedelta(days=4)).isoformat()
        }
    ]
    
    print(f"\n📝 Adding {len(demo_trades)} demo trades...")
    successful_trades = 0
    
    for trade in demo_trades:
        try:
            result = tablesDB.create_row(
                database_id=database_id,
                table_id=table_id,
                row_id=ID.unique(),
                data=trade
            )
            print(f"  ✅ {trade['trade_id']}: {trade['trade_type']} {trade['amount']} {trade['symbol']} @ ${trade['price']}")
            successful_trades += 1
            time.sleep(0.5)  # Small delay to avoid rate limiting
        except Exception as e:
            print(f"  ❌ {trade['trade_id']}: {e}")
    
    return successful_trades

def main():
    """Main function to create table and add demo data"""
    print("🚀 Creating trade_history table using TablesDB API...\n")
    
    try:
        # Load configuration
        config = load_config()
        print(f"✅ Loaded config for project: {config['appwrite_project_id']}")
        print(f"✅ Database ID: {config['appwrite_database_id']}")
        
        # Initialize Appwrite client
        client = setup_appwrite_client(config)
        tablesDB = TablesDB(client)
        
        # Create the table
        table = create_trade_table(tablesDB, config['appwrite_database_id'])
        if not table:
            print("❌ Failed to create table. Exiting.")
            return False
        
        # Create columns
        successful_columns = create_table_columns(tablesDB, config['appwrite_database_id'], table['$id'])
        if successful_columns == 0:
            print("❌ Failed to create any columns. Exiting.")
            return False
        
        # Add demo data
        successful_trades = add_demo_data(tablesDB, config['appwrite_database_id'], table['$id'])
        
        # Save IDs for future reference
        result_data = {
            'database_id': config['appwrite_database_id'],
            'table_id': table['$id'],
            'table_name': table['name'],
            'created_at': datetime.now().isoformat(),
            'successful_columns': successful_columns,
            'successful_trades': successful_trades,
            'total_demo_trades': 7
        }
        
        with open('trade_history_ids.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n🎉 Setup completed successfully!")
        print(f"📊 Database ID: {config['appwrite_database_id']}")
        print(f"📋 Table ID: {table['$id']}")
        print(f"🔧 Created {successful_columns}/10 columns")
        print(f"📝 Added {successful_trades}/7 demo trades")
        print(f"💾 Details saved to trade_history_ids.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🌟 Your trade_history table is ready with demo data!")
        print("You can now use it to store and query trading data in your autoTrade system.")
    else:
        print("\n💥 Setup failed. Please check the errors above.")