#!/usr/bin/env python3
"""
Simplified script to create trade_history database and populate it with demo data.
"""

import json
import time
from datetime import datetime, timedelta
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def setup_appwrite_client(config):
    """Initialize Appwrite client with configuration"""
    try:
        client = Client()
        client.set_endpoint(config['appwrite_endpoint'])
        client.set_project(config['appwrite_project_id'])
        client.set_key(config['appwrite_api_secret'])
        
        print(f"✅ Connected to Appwrite at {config['appwrite_endpoint']}")
        print(f"✅ Using project: {config['appwrite_project_id']}")
        return client
    except Exception as e:
        print(f"❌ Error setting up client: {e}")
        return None

def create_database(databases):
    """Create the trade history database"""
    try:
        database = databases.create(
            database_id=ID.unique(),
            name='TradeHistoryDB'
        )
        print(f"✅ Created database: {database['name']} (ID: {database['$id']})")
        return database
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return None

def create_collection(databases, database_id):
    """Create the trade history collection"""
    try:
        collection = databases.create_collection(
            database_id=database_id,
            collection_id=ID.unique(),
            name='trade_history'
        )
        print(f"✅ Created collection: {collection['name']} (ID: {collection['$id']})")
        return collection
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return None

def create_attributes(databases, database_id, collection_id):
    """Create attributes for the trade history collection"""
    
    attributes = [
        {'name': 'trade_id', 'type': 'string', 'size': 50, 'required': True},
        {'name': 'symbol', 'type': 'string', 'size': 20, 'required': True},
        {'name': 'trade_type', 'type': 'string', 'size': 10, 'required': True},
        {'name': 'amount', 'type': 'float', 'required': True},
        {'name': 'price', 'type': 'float', 'required': True},
        {'name': 'total_value', 'type': 'float', 'required': True},
        {'name': 'fees', 'type': 'float', 'required': False},
        {'name': 'status', 'type': 'string', 'size': 20, 'required': True},
        {'name': 'exchange', 'type': 'string', 'size': 50, 'required': False},
        {'name': 'trade_timestamp', 'type': 'string', 'size': 50, 'required': True},
    ]
    
    for attr in attributes:
        try:
            if attr['type'] == 'string':
                result = databases.create_string_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=attr['name'],
                    size=attr['size'],
                    required=attr['required']
                )
            elif attr['type'] == 'float':
                result = databases.create_float_attribute(
                    database_id=database_id,
                    collection_id=collection_id,
                    key=attr['name'],
                    required=attr['required']
                )
            
            print(f"✅ Created attribute: {attr['name']}")
            time.sleep(1)  # Wait between attribute creation
            
        except Exception as e:
            print(f"❌ Error creating attribute {attr['name']}: {e}")
            continue

def add_demo_data(databases, database_id, collection_id):
    """Add demo trading data"""
    
    # Wait for attributes to be fully created
    print("\n⏳ Waiting for attributes to be ready...")
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
    
    print(f"\n📝 Adding {len(demo_trades)} demo trades...")
    successful_trades = 0
    
    for trade in demo_trades:
        try:
            result = databases.create_document(
                database_id=database_id,
                collection_id=collection_id,
                document_id=ID.unique(),
                data=trade
            )
            print(f"✅ Added: {trade['trade_id']} - {trade['trade_type']} {trade['amount']} {trade['symbol']} @ ${trade['price']}")
            successful_trades += 1
        except Exception as e:
            print(f"❌ Failed to add {trade['trade_id']}: {e}")
    
    return successful_trades

def main():
    """Main function"""
    print("🚀 Setting up Appwrite trade history database...\n")
    
    # Load configuration
    config = load_config()
    if not config:
        return False
    
    # Initialize client
    client = setup_appwrite_client(config)
    if not client:
        return False
    
    databases = Databases(client)
    
    # Create database
    database = create_database(databases)
    if not database:
        return False
    
    # Create collection
    collection = create_collection(databases, database['$id'])
    if not collection:
        return False
    
    # Create attributes
    print(f"\n🔧 Creating attributes...")
    create_attributes(databases, database['$id'], collection['$id'])
    
    # Add demo data
    successful_trades = add_demo_data(databases, database['$id'], collection['$id'])
    
    # Save IDs for future reference
    ids_data = {
        'database_id': database['$id'],
        'collection_id': collection['$id'],
        'created_at': datetime.now().isoformat(),
        'successful_trades': successful_trades
    }
    
    try:
        with open('trade_history_ids.json', 'w') as f:
            json.dump(ids_data, f, indent=2)
        print(f"💾 Database IDs saved to trade_history_ids.json")
    except Exception as e:
        print(f"⚠️ Could not save IDs file: {e}")
    
    print(f"\n🎉 Setup completed!")
    print(f"📊 Database ID: {database['$id']}")
    print(f"📋 Collection ID: {collection['$id']}")
    print(f"✅ Successfully added {successful_trades} demo trades")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💥 Setup failed. Please check the errors above.")
        exit(1)
    
    print("\n🌟 Trade history database is ready for use!")