#!/usr/bin/env python3
"""
Test script for the AutoTrade Dashboard
This script tests all API endpoints and verifies the dashboard functionality.
"""

import requests
import json
import sys
import time
from datetime import datetime

class DashboardTester:
    def __init__(self, base_url="http://localhost:28791"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AutoTrade-Dashboard-Tester/1.0'
        })

    def test_server_connection(self):
        """Test basic server connectivity"""
        print("🔍 Testing server connection...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Server is running and accessible")
                return True
            else:
                print(f"❌ Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Is it running?")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def test_balance_endpoint(self):
        """Test the balance endpoint"""
        print("\n🔍 Testing balance endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/balance")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    print("✅ Balance endpoint working")
                    print(f"   Account: {data.get('address', 'N/A')}")
                    print(f"   Perp Value: ${data.get('perp_account_value', 'N/A')}")
                    return True
                else:
                    print(f"❌ Balance endpoint returned error: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Balance endpoint returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing balance endpoint: {e}")
            return False

    def test_dashboard_api_endpoints(self):
        """Test all dashboard API endpoints"""
        endpoints = [
            ("/api/trading-stats", "Trading Statistics"),
            ("/api/trade-history", "Trade History"),
            ("/api/chart-data", "Chart Data"),
            ("/api/account-summary", "Account Summary")
        ]

        results = {}
        
        for endpoint, name in endpoints:
            print(f"\n🔍 Testing {name} endpoint...")
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        print(f"✅ {name} endpoint working")
                        
                        # Print some sample data
                        if endpoint == "/api/trading-stats":
                            stats_data = data.get("data", {})
                            print(f"   Total Trades: {stats_data.get('total_trades', 0)}")
                            print(f"   Success Rate: {stats_data.get('success_rate', 0)}%")
                            print(f"   Total Volume: ${stats_data.get('total_volume', 0)}")
                        
                        elif endpoint == "/api/trade-history":
                            trades = data.get("data", [])
                            count = data.get("count", 0)
                            print(f"   Trade Count: {count}")
                            if trades:
                                print(f"   Latest Trade: {trades[0].get('symbol', 'N/A')} - {trades[0].get('trade_type', 'N/A')}")
                        
                        elif endpoint == "/api/chart-data":
                            chart_data = data.get("data", {})
                            volume_points = len(chart_data.get("volume_data", []))
                            pnl_points = len(chart_data.get("pnl_data", []))
                            print(f"   Volume Data Points: {volume_points}")
                            print(f"   P&L Data Points: {pnl_points}")
                        
                        elif endpoint == "/api/account-summary":
                            account_data = data.get("data", {})
                            print(f"   Account Value: ${account_data.get('perp_account_value', 'N/A')}")
                        
                        results[endpoint] = True
                    else:
                        print(f"❌ {name} endpoint returned error: {data.get('message', 'Unknown error')}")
                        results[endpoint] = False
                else:
                    print(f"❌ {name} endpoint returned status code: {response.status_code}")
                    results[endpoint] = False
            except Exception as e:
                print(f"❌ Error testing {name} endpoint: {e}")
                results[endpoint] = False

        return results

    def test_dashboard_page(self):
        """Test the dashboard page accessibility"""
        print("\n🔍 Testing dashboard page...")
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code == 200:
                content = response.text
                if "AutoTrade Dashboard" in content:
                    print("✅ Dashboard page is accessible")
                    print("   HTML content loaded successfully")
                    return True
                else:
                    print("❌ Dashboard page content appears to be incorrect")
                    return False
            else:
                print(f"❌ Dashboard page returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing dashboard page: {e}")
            return False

    def test_dashboard_assets(self):
        """Test dashboard static assets"""
        assets = [
            ("/dashboard/css/dashboard.css", "CSS Stylesheet"),
            ("/dashboard/js/api.js", "API Module"),
            ("/dashboard/js/charts.js", "Charts Module"),
            ("/dashboard/js/dashboard.js", "Dashboard Module")
        ]

        results = {}
        
        for asset_path, name in assets:
            print(f"\n🔍 Testing {name}...")
            try:
                response = self.session.get(f"{self.base_url}{asset_path}")
                if response.status_code == 200:
                    print(f"✅ {name} is accessible")
                    results[asset_path] = True
                else:
                    print(f"❌ {name} returned status code: {response.status_code}")
                    results[asset_path] = False
            except Exception as e:
                print(f"❌ Error testing {name}: {e}")
                results[asset_path] = False

        return results

    def run_full_test(self):
        """Run all tests and provide a summary"""
        print("🚀 Starting AutoTrade Dashboard Tests")
        print("=" * 50)
        
        start_time = time.time()
        
        # Test server connection
        server_ok = self.test_server_connection()
        if not server_ok:
            print("\n❌ Cannot proceed with tests - server is not accessible")
            return False

        # Test balance endpoint (validates trading service)
        balance_ok = self.test_balance_endpoint()
        
        # Test dashboard API endpoints
        api_results = self.test_dashboard_api_endpoints()
        
        # Test dashboard page
        page_ok = self.test_dashboard_page()
        
        # Test dashboard assets
        asset_results = self.test_dashboard_assets()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        print(f"🌐 Server Connection: {'✅ PASS' if server_ok else '❌ FAIL'}")
        print(f"💰 Balance Endpoint: {'✅ PASS' if balance_ok else '❌ FAIL'}")
        print(f"📄 Dashboard Page: {'✅ PASS' if page_ok else '❌ FAIL'}")
        
        print("\n📡 API Endpoints:")
        for endpoint, status in api_results.items():
            print(f"   {endpoint}: {'✅ PASS' if status else '❌ FAIL'}")
        
        print("\n📁 Static Assets:")
        for asset, status in asset_results.items():
            print(f"   {asset}: {'✅ PASS' if status else '❌ FAIL'}")
        
        # Overall status
        api_passed = all(api_results.values())
        assets_passed = all(asset_results.values())
        all_passed = server_ok and balance_ok and page_ok and api_passed and assets_passed
        
        print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        if all_passed:
            print("\n🎉 Your AutoTrade Dashboard is ready to use!")
            print(f"🔗 Access it at: {self.base_url}/dashboard")
        else:
            print("\n🔧 Please check the failed tests and fix any issues.")
        
        return all_passed

def main():
    """Main function to run the tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AutoTrade Dashboard")
    parser.add_argument("--url", default="http://localhost:28791", 
                       help="Base URL of the AutoTrade server (default: http://localhost:28791)")
    
    args = parser.parse_args()
    
    tester = DashboardTester(args.url)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()