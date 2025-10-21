# File: src/__init__.py

from flask import Flask
import logging
from .services.trading_service import init_trading_service

def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize the trading service
    try:
        init_trading_service(app)
        logging.info("Trading service initialized successfully.")
    except Exception as e:
        logging.critical(f"CRITICAL: Failed to initialize trading service: {e}")
        # Set to None so routes can check if service is available
        app.trading_service = None

    with app.app_context():
        # Import and register Blueprints
        from .routes import webhook_routes
        from .routes import balance_routes

        app.register_blueprint(webhook_routes.webhook_bp)
        app.register_blueprint(balance_routes.balance_bp)

    # A simple health check / welcome endpoint
    @app.route('/')
    def welcome():
        return "Hyperliquid Trading Server is running."

    return app