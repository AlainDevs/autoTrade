# File: src/routes/dashboard_routes.py

from flask import Blueprint, jsonify, current_app, request, send_from_directory, send_file
import logging
import os
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def serve_dashboard():
    """Serve the dashboard HTML file."""
    try:
        dashboard_path = os.path.join(os.path.dirname(__file__), "..", "..", "dashboard")
        return send_from_directory(dashboard_path, 'index.html')
    except Exception as e:
        logging.error(f"Error serving dashboard: {e}")
        return jsonify({
            "error": "Dashboard not found",
            "message": "Please ensure the dashboard files are properly installed"
        }), 404

@dashboard_bp.route('/dashboard/<path:filename>')
def serve_dashboard_assets(filename):
    """Serve dashboard static assets (CSS, JS, etc.)."""
    try:
        dashboard_path = os.path.join(os.path.dirname(__file__), "..", "..", "dashboard")
        return send_from_directory(dashboard_path, filename)
    except Exception as e:
        logging.error(f"Error serving dashboard asset {filename}: {e}")
        return jsonify({
            "error": "Asset not found",
            "message": f"Asset {filename} not found"
        }), 404

@dashboard_bp.route('/api/trading-stats')
def get_trading_stats():
    """Get comprehensive trading statistics."""
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized.")
        return jsonify({
            "status": "error",
            "message": "Trading service not initialized"
        }), 503
    
    try:
        stats = service.get_trading_stats()
        logging.info("Successfully fetched trading statistics")
        return jsonify({
            "status": "success",
            "data": stats
        }), 200
    except Exception as e:
        logging.error(f"Error fetching trading stats: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to fetch trading statistics",
            "details": str(e)
        }), 500

@dashboard_bp.route('/api/trade-history')
def get_trade_history():
    """Get trade history with optional filtering."""
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized.")
        return jsonify({
            "status": "error",
            "message": "Trading service not initialized"
        }), 503
    
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        symbol = request.args.get('symbol', None)
        
        # Validate limit
        if limit > 1000:
            limit = 1000
        if limit < 1:
            limit = 50
        
        trades = service.get_trade_history(limit=limit, symbol=symbol)
        
        logging.info(f"Successfully fetched {len(trades)} trade records")
        return jsonify({
            "status": "success",
            "data": trades,
            "count": len(trades)
        }), 200
    except Exception as e:
        logging.error(f"Error fetching trade history: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to fetch trade history",
            "details": str(e)
        }), 500

@dashboard_bp.route('/api/chart-data')
def get_chart_data():
    """Get formatted data for charts (volume and P&L over time)."""
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized.")
        return jsonify({
            "status": "error",
            "message": "Trading service not initialized"
        }), 503
    
    try:
        # Get all trades for chart calculations
        trades = service.get_trade_history(limit=1000)
        
        if not trades:
            return jsonify({
                "status": "success",
                "data": {
                    "volume_data": [],
                    "pnl_data": []
                }
            }), 200
        
        # Process trades for chart data
        volume_data = []
        pnl_data = []
        cumulative_pnl = 0
        
        # Group trades by date for volume chart
        date_volume = {}
        
        for trade in reversed(trades):  # Process in chronological order
            try:
                # Parse trade timestamp
                trade_date = datetime.fromisoformat(trade['trade_timestamp'].replace('Z', '+00:00'))
                date_str = trade_date.strftime('%Y-%m-%d')
                
                # Calculate volume for this trade
                trade_volume = float(trade.get('total_value', 0))
                
                # Aggregate volume by date
                if date_str in date_volume:
                    date_volume[date_str] += trade_volume
                else:
                    date_volume[date_str] = trade_volume
                
                # Calculate P&L (simplified - assumes all completed trades are profitable)
                trade_type = trade.get('trade_type', 'buy')
                if trade_type == 'sell':
                    # For sells, add to P&L (simplified calculation)
                    cumulative_pnl += trade_volume * 0.01  # Assume 1% profit per trade
                
                # Add P&L data point
                pnl_data.append({
                    'date': date_str,
                    'pnl': round(cumulative_pnl, 2)
                })
                
            except Exception as trade_error:
                logging.warning(f"Error processing trade for charts: {trade_error}")
                continue
        
        # Convert volume data to chart format
        for date_str, volume in sorted(date_volume.items()):
            volume_data.append({
                'date': date_str,
                'volume': round(volume, 2)
            })
        
        # Remove duplicate P&L entries (keep latest per date)
        pnl_by_date = {}
        for item in pnl_data:
            pnl_by_date[item['date']] = item['pnl']
        
        pnl_data = [{'date': date, 'pnl': pnl} 
                   for date, pnl in sorted(pnl_by_date.items())]
        
        logging.info(f"Successfully generated chart data: {len(volume_data)} volume points, {len(pnl_data)} P&L points")
        return jsonify({
            "status": "success",
            "data": {
                "volume_data": volume_data,
                "pnl_data": pnl_data
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating chart data: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to generate chart data",
            "details": str(e)
        }), 500

@dashboard_bp.route('/api/account-summary')
def get_account_summary():
    """Get current account balance and summary."""
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized.")
        return jsonify({
            "status": "error",
            "message": "Trading service not initialized"
        }), 503
    
    try:
        balance_info = service.check_balance()
        logging.info("Successfully fetched account summary")
        return jsonify({
            "status": "success",
            "data": balance_info
        }), 200
    except Exception as e:
        logging.error(f"Error fetching account summary: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to fetch account summary",
            "details": str(e)
        }), 500