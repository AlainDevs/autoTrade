# File: src/routes/webhook_routes.py

from flask import Blueprint, request, jsonify, current_app
import logging

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def tradingview_webhook():
    """Endpoint to receive trading signals."""
    service = current_app.trading_service
    
    if service is None:
        logging.error("Trading service not initialized. Check config.json and server logs.")
        return jsonify({
            "error": "Trading service not initialized",
            "details": "The server failed to initialize the trading service. Check the logs and config.json."
        }), 503
    
    secret = service.config.get("webhook_secret")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        logging.info(f"Received webhook payload: {data}")

        if secret and data.get("secret") != secret:
            logging.warning("Invalid webhook secret.")
            return jsonify({"error": "Invalid secret"}), 403

        order_result = service.handle_order(data)
        return jsonify(order_result), 200

    except Exception as e:
        logging.error(f"Error in webhook: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500