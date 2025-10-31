# File: src/routes/balance_routes.py

from flask import Blueprint, jsonify, current_app, request
import logging

balance_bp = Blueprint('balance', __name__)

def add_cors_headers(response):
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@balance_bp.route('/balance', methods=['GET', 'OPTIONS'])
def check_balance():
    """Endpoint to test API connection by fetching balance."""
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response)
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized. Check config.json and server logs.")
        response = jsonify({
            "status": "error",
            "message": "Trading service not initialized. Please check config.json and restart the server.",
            "details": "The server failed to initialize the trading service. Check the logs for more details."
        })
        response.status_code = 503
        return add_cors_headers(response)
    
    try:
        balance_info = service.check_balance()
        logging.info(f"Successfully fetched balance for {balance_info['address']}")
        response = jsonify({
            "status": "success",
            "message": "API connection and account_address are correct.",
            **balance_info
        })
        return add_cors_headers(response)
    except Exception as e:
        logging.error(f"Error checking balance: {e}", exc_info=True)
        response = jsonify({
            "status": "error",
            "message": "Failed to fetch balance. Check config and API.",
            "details": str(e)
        })
        response.status_code = 500
        return add_cors_headers(response)