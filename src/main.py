import logging
from flask import Flask, request, jsonify
from src.trading_utils import setup_exchange, handle_order

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Load configuration and initialize the exchange instance
try:
    config, exchange, info = setup_exchange()
    WEBHOOK_SECRET = config.get("webhook_secret")
    if not WEBHOOK_SECRET:
        logging.warning("Webhook secret is not set in config.json. The webhook endpoint will be insecure.")
except Exception as e:
    logging.critical(f"Failed to initialize the application: {e}")
    exchange = None
    info = None
    WEBHOOK_SECRET = None

@app.route('/')
def welcome():
    """A simple test endpoint to confirm the server is running."""
    return "Hyperliquid Trading Server is running."

@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    """
    The main endpoint to receive and process trading signals from TradingView.
    """
    if not exchange or not info:
        return jsonify({"error": "Exchange not initialized. Check server logs."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        logging.info(f"Received webhook payload: {data}")

        # Basic security check
        if WEBHOOK_SECRET and data.get("secret") != WEBHOOK_SECRET:
            logging.warning("Invalid webhook secret received.")
            return jsonify({"error": "Invalid secret"}), 403

        # Handle the order based on the received data
        order_result = handle_order(data, exchange, info)
        
        return jsonify(order_result), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    # Note: For production, it's recommended to use a proper WSGI server like Gunicorn
    app.run(host='0.0.0.0', port=28791)