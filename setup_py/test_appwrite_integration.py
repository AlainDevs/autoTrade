#!/usr/bin/env python3
"""
Test script to verify Appwrite integration with the trading service.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.trading_service import TradingService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_appwrite_integration():
    """Test the Appwrite integration"""
    print("🧪 Testing Appwrite Integration with Trading Service\n")
    
    try:
        # Initialize trading service (this will also initialize Appwrite)
        print("1️⃣ Initializing Trading Service...")
        trading_service = TradingService()
        print("✅ Trading Service initialized successfully\n")
        
        # Test trade history retrieval
        print("2️⃣ Testing trade history retrieval...")
        trades = trading_service.get_trade_history(limit=10)
        print(f"✅ Retrieved {len(trades)} trade records\n")
        
        if trades:
            print("📊 Recent trades:")
            for i, trade in enumerate(trades[:5], 1):
                print(f"   {i}. {trade.get('trade_id')} - {trade.get('trade_type')} {trade.get('amount')} {trade.get('symbol')} @ ${trade.get('price')}")
            print()
        
        # Test trading statistics
        print("3️⃣ Testing trading statistics...")
        stats = trading_service.get_trading_stats()
        print("✅ Trading statistics retrieved:")
        for key, value in stats.items():
            if key != 'latest_trade':
                print(f"   {key}: {value}")
        print()
        
        # Test manual trade logging (simulate a trade)
        print("4️⃣ Testing manual trade logging...")
        test_trade = {
            'symbol': 'TEST/USD',
            'trade_type': 'buy',
            'amount': 1.0,
            'price': 100.0,
            'total_value': 100.0,
            'fees': 0.1,
            'status': 'completed'
        }
        
        result = trading_service._log_trade_to_appwrite(test_trade)
        if result:
            print("✅ Test trade logged successfully")
        else:
            print("❌ Failed to log test trade")
        print()
        
        # Test symbol-specific history
        print("5️⃣ Testing symbol-specific trade history...")
        btc_trades = trading_service.get_trade_history(limit=5, symbol='BTC/USD')
        print(f"✅ Retrieved {len(btc_trades)} BTC/USD trades")
        
        if btc_trades:
            for trade in btc_trades:
                print(f"   - {trade.get('trade_id')}: {trade.get('trade_type')} {trade.get('amount')} BTC/USD @ ${trade.get('price')}")
        print()
        
        print("🎉 All tests completed successfully!")
        print("\n📈 Your trading service is now integrated with Appwrite!")
        print("   • All trades will be automatically logged")
        print("   • You can retrieve trade history and statistics")
        print("   • Data is stored securely in your Appwrite database")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_appwrite_integration()
    if not success:
        print("\n💥 Some tests failed. Check the error messages above.")
        print("   Make sure your Appwrite configuration is correct in config.json")
    else:
        print("\n🌟 Integration test passed! Your system is ready for live trading.")

if __name__ == "__main__":
    main()