# File: src/routes/balance_routes.py

from flask import Blueprint, jsonify, current_app
import logging

balance_bp = Blueprint('balance', __name__)

@balance_bp.route('/balance')
def check_balance():
    """Endpoint to test API connection by fetching balance."""
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized. Check config.json and server logs.")
        return jsonify({
            "status": "error",
            "message": "Trading service not initialized. Please check config.json and restart the server.",
            "details": "The server failed to initialize the trading service. Check the logs for more details."
        }), 503
    
    try:
        balance_info = service.check_balance()
        logging.info(f"Successfully fetched balance for {balance_info['address']}")
        return jsonify({
            "status": "success",
            "message": "API connection and account_address are correct.",
            **balance_info
        }), 200
    except Exception as e:
        logging.error(f"Error checking balance: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to fetch balance. Check config and API.",
            "details": str(e)
        }), 500