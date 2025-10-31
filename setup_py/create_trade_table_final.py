#!/usr/bin/env python3
"""
Final script to create trade_history table with comprehensive error handling.
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

def check_existing_tables(tablesDB, database_id):
    """Check what tables already exist"""
    try:
        tables = tablesDB.list_tables(database_id=database_id)
        print(f"📋 Found {tables['total']} existing tables:")
        for table in tables['tables']:
            print(f"  - {table['name']} (ID: {table['$id']})")
        return tables['tables']
    except Exception as e:
        print(f"⚠️ Could not list tables: {e}")
        return []

def create_trade_table(tablesDB, database_id):
    """Create the trade_history table"""
    try:
        print(f"🔧 Creating trade_history table...")
        table = tablesDB.create_table(
            database_id=database_id,
            table_id=ID.unique(),
            name='trade_history'
        )
        print(f"✅ Created table: {table['name']} (ID: {table['$id']})")
        return table
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        
        # Try to find if table already exists
        existing_tables = check_existing_tables(tablesDB, database_id)
        for table in existing_tables:
            if table['name'] == 'trade_history':
                print(f"💡 Found existing trade_history table: {table['$id']}")
                return table
        
        return None

def create_table_columns(tablesDB, database_id, table_id):
    """Create all columns for the trade_history table"""
    print(f"\n🔧 Creating table columns...")
    
    columns = [
        {'key': 'trade_id', 'method': 'create_string_column', 'size': 50, 'required': True},
        {'key': 'symbol', 'method': 'create_string_column', 'size': 20, 'required': True},
        {'key': 'trade_type', 'method': 'create_string_column', 'size': 10, 'required': True},
        {'key': 'amount', 'method': 'create_float_column', 'required': True},
        {'key': 'price', 'method': 'create_float_column', 'required': True},
        {'key': 'total_value', 'method': 'create_float_column', 'required': True},
        {'key': 'fees', 'method': 'create_float_column', 'required': False, 'default': 0.0},
        {'key': 'status', 'method': 'create_string_column', 'size': 20, 'required': True},
        {'key': 'exchange', 'method': 'create_string_column', 'size': 50, 'required': False},
        {'key': 'trade_timestamp', 'method': 'create_string_column', 'size': 50, 'required': True},
    ]
    
    successful_columns = 0
    
    for column in columns:
        try:
            method = getattr(tablesDB, column['method'])
            
            # Build parameters based on column type
            params = {
                'database_id': database_id,
                'table_id': table_id,
                'key': column['key'],
                'required': column['required']
            }
            
            # Add size for string columns
            if 'size' in column:
                params['size'] = column['size']
            
            # Add default if specified
            if 'default' in column:
                params['default'] = column['default']
            
            result = method(**params)
            print(f"  ✅ {column['key']}")
            successful_columns += 1
            time.sleep(1)  # Wait between column creation
            
        except Exception as e:
            print(f"  ❌ {column['key']}: {e}")
    
    print(f"\n✅ Created {successful_columns}/{len(columns)} columns successfully")
    return successful_columns

def add_demo_data(tablesDB, database_id, table_id):
    """Add demo trading data to the table"""
    print(f"\n📝 Adding demo data...")
    print(f"⏳ Waiting for columns to be ready...")
    time.sleep(5)
    
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
        }
    ]
    
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
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ {trade['trade_id']}: {e}")
    
    return successful_trades

def main():
    """Main function"""
    print("🚀 Setting up trade_history table with TablesDB API...\n")
    
    try:
        # Load configuration
        config = load_config()
        print(f"✅ Config loaded for project: {config['appwrite_project_id']}")
        print(f"✅ Database ID: {config['appwrite_database_id']}")
        
        # Initialize client
        client = setup_appwrite_client(config)
        tablesDB = TablesDB(client)
        
        # Check existing tables first
        existing_tables = check_existing_tables(tablesDB, config['appwrite_database_id'])
        
        # Create or find table
        table = create_trade_table(tablesDB, config['appwrite_database_id'])
        if not table:
            print("❌ Could not create or find trade_history table.")
            return False
        
        # Create columns
        successful_columns = create_table_columns(tablesDB, config['appwrite_database_id'], table['$id'])
        
        # Add demo data (even if some columns failed)
        if successful_columns > 0:
            successful_trades = add_demo_data(tablesDB, config['appwrite_database_id'], table['$id'])
        else:
            successful_trades = 0
        
        # Save results
        result_data = {
            'database_id': config['appwrite_database_id'],
            'table_id': table['$id'],
            'table_name': table['name'],
            'created_at': datetime.now().isoformat(),
            'successful_columns': successful_columns,
            'successful_trades': successful_trades
        }
        
        with open('trade_history_ids.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n🎉 Setup completed!")
        print(f"📊 Database ID: {config['appwrite_database_id']}")
        print(f"📋 Table ID: {table['$id']}")
        print(f"🔧 Columns created: {successful_columns}/10")
        print(f"📝 Demo trades added: {successful_trades}/5")
        print(f"💾 Details saved to trade_history_ids.json")
        
        if successful_columns > 0 or successful_trades > 0:
            print("\n🌟 Your trade_history table is ready!")
            return True
        else:
            print("\n⚠️ Setup had issues. Check the output above.")
            return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("You can now use it in your autoTrade system!")
    else:
        print("Please review any error messages above.")