#!/usr/bin/env python3
"""
Complete script to set up trade_history database and populate it with demo data.
This script will work with an existing database or guide you to create one.
"""

import json
import time
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

def create_database_if_needed(databases):
    """Try to create database, or prompt user to create it manually"""
    try:
        # Try to create database
        database = databases.create(
            database_id=ID.unique(),
            name='TradeHistoryDB'
        )
        print(f"✅ Created database: {database['name']} (ID: {database['$id']})")
        return database
    except Exception as e:
        print(f"⚠️ Could not create database via API: {e}")
        print("\n📋 MANUAL SETUP REQUIRED:")
        print("1. Go to: https://fra.cloud.appwrite.io/console/project/.../databases")
        print("2. Click 'Create Database'")
        print("3. Name it 'TradeHistoryDB'")
        print("4. Copy the Database ID and run this script again")
        print("\nAlternatively, provide an existing database ID when prompted.")
        
        # Ask user for existing database ID
        db_id = input("\nEnter existing Database ID (or press Enter to exit): ").strip()
        if not db_id:
            return None
        
        try:
            # Try to get the database
            database = databases.get(database_id=db_id)
            print(f"✅ Using existing database: {database['name']} (ID: {database['$id']})")
            return database
        except Exception as e2:
            print(f"❌ Could not access database {db_id}: {e2}")
            return None

def create_collection_and_attributes(databases, database_id):
    """Create collection and all attributes"""
    try:
        # Create collection
        collection = databases.create_collection(
            database_id=database_id,
            collection_id=ID.unique(),
            name='trade_history'
        )
        print(f"✅ Created collection: {collection['name']} (ID: {collection['$id']})")
        
        # Define attributes
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
        
        print(f"\n🔧 Creating {len(attributes)} attributes...")
        
        for attr in attributes:
            try:
                if attr['type'] == 'string':
                    databases.create_string_attribute(
                        database_id=database_id,
                        collection_id=collection['$id'],
                        key=attr['name'],
                        size=attr['size'],
                        required=attr['required']
                    )
                elif attr['type'] == 'float':
                    databases.create_float_attribute(
                        database_id=database_id,
                        collection_id=collection['$id'],
                        key=attr['name'],
                        required=attr['required']
                    )
                
                print(f"  ✅ {attr['name']}")
                time.sleep(0.5)  # Avoid rate limiting
                
            except Exception as e:
                print(f"  ❌ {attr['name']}: {e}")
        
        return collection
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return None

def add_demo_data(databases, database_id, collection_id):
    """Add demo trading data"""
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
    successful = 0
    
    for trade in demo_trades:
        try:
            databases.create_document(
                database_id=database_id,
                collection_id=collection_id,
                document_id=ID.unique(),
                data=trade
            )
            print(f"  ✅ {trade['trade_id']}: {trade['trade_type']} {trade['amount']} {trade['symbol']} @ ${trade['price']}")
            successful += 1
            time.sleep(0.2)  # Avoid rate limiting
        except Exception as e:
            print(f"  ❌ {trade['trade_id']}: {e}")
    
    return successful

def main():
    """Main function"""
    print("🚀 Setting up Appwrite trade history database...\n")
    
    try:
        # Load config and setup client
        config = load_config()
        client = setup_appwrite_client(config)
        databases = Databases(client)
        
        print(f"✅ Connected to: {config['appwrite_endpoint']}")
        print(f"✅ Project: {config['appwrite_project_id']}\n")
        
        # Create or get database
        database = create_database_if_needed(databases)
        if not database:
            print("❌ Could not create or access database. Exiting.")
            return False
        
        # Create collection and attributes
        collection = create_collection_and_attributes(databases, database['$id'])
        if not collection:
            print("❌ Could not create collection. Exiting.")
            return False
        
        # Add demo data
        successful_trades = add_demo_data(databases, database['$id'], collection['$id'])
        
        # Save configuration
        result_data = {
            'database_id': database['$id'],
            'database_name': database['name'],
            'collection_id': collection['$id'],
            'collection_name': collection['name'],
            'created_at': datetime.now().isoformat(),
            'successful_trades': successful_trades,
            'total_demo_trades': 7
        }
        
        with open('trade_history_ids.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n🎉 Setup completed successfully!")
        print(f"📊 Database: {database['name']} ({database['$id']})")
        print(f"📋 Collection: {collection['name']} ({collection['$id']})")
        print(f"✅ Added {successful_trades}/7 demo trades")
        print(f"💾 Details saved to trade_history_ids.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🌟 Your trade history database is ready!")
        print("You can now use it to store and query trading data.")
    else:
        print("\n💥 Setup incomplete. Please check the errors above.")