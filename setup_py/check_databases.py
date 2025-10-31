#!/usr/bin/env python3
"""
Script to check existing databases and create trade_history collection if needed.
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

def main():
    """Main function to check databases"""
    print("🔍 Checking existing Appwrite databases...\n")
    
    config = load_config()
    client = setup_appwrite_client(config)
    databases = Databases(client)
    
    try:
        # List existing databases
        existing_databases = databases.list()
        print(f"📊 Found {existing_databases['total']} existing databases:")
        
        for db in existing_databases['databases']:
            print(f"  - {db['name']} (ID: {db['$id']})")
            
            # List collections in this database
            try:
                collections = databases.list_collections(database_id=db['$id'])
                print(f"    Collections ({collections['total']}):")
                for collection in collections['collections']:
                    print(f"      - {collection['name']} (ID: {collection['$id']})")
            except Exception as e:
                print(f"    ❌ Error listing collections: {e}")
        
        print(f"\n✅ Database check completed")
        
        # If no databases exist, suggest creating one manually first
        if existing_databases['total'] == 0:
            print("\n💡 No databases found. You may need to create one manually in the Appwrite console first.")
            print("   Visit: https://fra.cloud.appwrite.io/console/project/.../databases")
        
    except Exception as e:
        print(f"❌ Error checking databases: {e}")
        print(f"   This might be due to API permissions or configuration issues.")

if __name__ == "__main__":
    main()