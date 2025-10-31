#!/usr/bin/env python3
"""
Script to create trade_history database and populate it with demo data.
"""

import json
from datetime import datetime, timedelta
from appwrite.client import Client
from appwrite.services.databases import Databases
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

def create_trade_history_database(databases):
    """Create trade_history database and table"""
    
    # Create database
    trade_database = databases.create(
        database_id=ID.unique(),
        name='TradeHistoryDB'
    )
    
    print(f"Created database: {trade_database['name']} (ID: {trade_database['$id']})")
    
    # Create collection (table)
    trade_table = databases.create_collection(
        database_id=trade_database['$id'],
        collection_id=ID.unique(),
        name='trade_history'
    )
    
    print(f"Created collection: {trade_table['name']} (ID: {trade_table['$id']})")
    
    # Create columns for trade data
    columns = [
        # Trade identifier
        {
            'method': 'create_string_attribute',
            'params': {
                'key': 'trade_id',
                'size': 50,
                'required': True
            }
        },
        # Trading symbol (e.g., BTC/USD)
        {
            'method': 'create_string_attribute',
            'params': {
                'key': 'symbol',
                'size': 20,
                'required': True
            }
        },
        # Trade type: buy or sell
        {
            'method': 'create_enum_attribute',
            'params': {
                'key': 'trade_type',
                'elements': ['buy', 'sell'],
                'required': True
            }
        },
        # Amount of asset traded
        {
            'method': 'create_float_attribute',
            'params': {
                'key': 'amount',
                'required': True,
                'min': 0.0
            }
        },
        # Price per unit
        {
            'method': 'create_float_attribute',
            'params': {
                'key': 'price',
                'required': True,
                'min': 0.0
            }
        },
        # Total value of trade (amount * price)
        {
            'method': 'create_float_attribute',
            'params': {
                'key': 'total_value',
                'required': True,
                'min': 0.0
            }
        },
        # Trading fees
        {
            'method': 'create_float_attribute',
            'params': {
                'key': 'fees',
                'required': False,
                'default': 0.0,
                'min': 0.0
            }
        },
        # Trade status
        {
            'method': 'create_enum_attribute',
            'params': {
                'key': 'status',
                'elements': ['completed', 'pending', 'failed', 'cancelled'],
                'required': True,
                'default': 'pending'
            }
        },
        # Exchange name
        {
            'method': 'create_string_attribute',
            'params': {
                'key': 'exchange',
                'size': 50,
                'required': False,
                'default': 'demo_exchange'
            }
        },
        # Trade timestamp
        {
            'method': 'create_datetime_attribute',
            'params': {
                'key': 'trade_timestamp',
                'required': True
            }
        }
    ]
    
    # Create each column
    for column in columns:
        method_name = column['method']
        method = getattr(databases, method_name)
        
        try:
            result = method(
                database_id=trade_database['$id'],
                collection_id=trade_table['$id'],
                **column['params']
            )
            print(f"Created column: {column['params']['key']}")
        except Exception as e:
            print(f"Error creating column {column['params']['key']}: {e}")
    
    return trade_database, trade_table

def add_demo_trade_data(databases, database_id, collection_id):
    """Add demo trading data to the table"""
    
    # Generate demo trades
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
    
    # Insert demo trades
    for trade in demo_trades:
        try:
            result = databases.create_document(
                database_id=database_id,
                collection_id=collection_id,
                document_id=ID.unique(),
                data=trade
            )
            print(f"Added trade: {trade['trade_id']} - {trade['trade_type']} {trade['amount']} {trade['symbol']} @ ${trade['price']}")
        except Exception as e:
            print(f"Error adding trade {trade['trade_id']}: {e}")

def main():
    """Main function to set up trade history database"""
    print("Setting up trade history database...")
    
    # Load configuration
    config = load_config()
    print(f"Loaded config for project: {config['appwrite_project_id']}")
    
    # Initialize Appwrite client
    client = setup_appwrite_client(config)
    databases = Databases(client)
    
    try:
        # Create database and table
        trade_database, trade_table = create_trade_history_database(databases)
        
        print("\nWaiting a moment for database setup to complete...")
        import time
        time.sleep(2)
        
        # Add demo data
        print("\nAdding demo trade data...")
        add_demo_trade_data(databases, trade_database['$id'], trade_table['$id'])
        
        print(f"\n✅ Successfully created trade_history database!")
        print(f"Database ID: {trade_database['$id']}")
        print(f"Collection ID: {trade_table['$id']}")
        print(f"Added 7 demo trades")
        
        # Save IDs to a file for future reference
        with open('trade_history_ids.json', 'w') as f:
            json.dump({
                'database_id': trade_database['$id'],
                'collection_id': trade_table['$id'],
                'created_at': datetime.now().isoformat()
            }, f, indent=2)
        
        print("💾 Database IDs saved to trade_history_ids.json")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Trade history database setup completed successfully!")
    else:
        print("\n💥 Setup failed. Check the error messages above.")