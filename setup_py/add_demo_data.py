#!/usr/bin/env python3
"""
Script to add demo data to existing trade_history collection.
Run this after manually creating the database and collection in Appwrite console.
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

def add_demo_data(databases, database_id, collection_id):
    """Add demo trading data"""
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
    
    print(f"📝 Adding {len(demo_trades)} demo trades...")
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
    print("📝 Adding demo data to trade_history collection...\n")
    
    try:
        config = load_config()
        client = setup_appwrite_client(config)
        databases = Databases(client)
        
        print(f"✅ Connected to: {config['appwrite_endpoint']}")
        print(f"✅ Project: {config['appwrite_project_id']}\n")
        
        # Get database and collection IDs from user
        database_id = input("Enter Database ID: ").strip()
        collection_id = input("Enter Collection ID: ").strip()
        
        if not database_id or not collection_id:
            print("❌ Both Database ID and Collection ID are required.")
            return False
        
        # Add demo data
        successful_trades = add_demo_data(databases, database_id, collection_id)
        
        # Save configuration
        result_data = {
            'database_id': database_id,
            'collection_id': collection_id,
            'created_at': datetime.now().isoformat(),
            'successful_trades': successful_trades,
            'total_demo_trades': 7
        }
        
        with open('trade_history_ids.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n🎉 Demo data added successfully!")
        print(f"✅ Added {successful_trades}/7 demo trades")
        print(f"💾 Details saved to trade_history_ids.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🌟 Your trade history database is ready with demo data!")
    else:
        print("\n💥 Failed to add demo data.")