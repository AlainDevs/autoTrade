# File: src/services/trading_service.py

import json
import os
import logging
from eth_account import Account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

class TradingService:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
        with open(config_path) as f:
            self.config = json.load(f)

        # Validate configuration
        secret_key = self.config.get("secret_key")
        if not secret_key:
            raise ValueError("secret_key must be set in config.json")
        
        # Check for placeholder values
        if secret_key == "0xYOUR_ETHEREUM_PRIVATE_KEY" or "YOUR" in secret_key.upper():
            raise ValueError(
                "Please replace the placeholder secret_key in config.json with your actual Ethereum private key. "
                "The private key should be a 64-character hex string (with or without '0x' prefix)."
            )

        account: LocalAccount = Account.from_key(secret_key)
        self.address = self.config.get("account_address") or account.address
        
        logging.info(f"Initializing trading service for account: {self.address}")
        
        base_url = constants.MAINNET_API_URL if self.config.get("is_mainnet") else constants.TESTNET_API_URL
        
        self.info = Info(base_url, skip_ws=True)
        self.exchange = Exchange(account, base_url, account_address=self.address)

    def check_balance(self):
        """Fetches perpetual and spot balances for the configured account."""
        user_state = self.info.user_state(self.address)
        perp_value = user_state["marginSummary"]["accountValue"]
        spot_balances = self.info.spot_user_state(self.address).get("balances", [])
        return {
            "address": self.address,
            "perp_account_value": perp_value,
            "spot_balances": spot_balances
        }

    def handle_order(self, data):
        """Routes webhook data to the appropriate action."""
        action = data.get("action", "").lower()
        if action == "open":
            return self._open_position(data)
        elif action == "close":
            return self._close_position(data)
        else:
            raise ValueError(f"Unsupported action: {action}")

    def _open_position(self, data):
        """Opens a market position with optional leverage, TP, and SL."""
        coin = data["coin"]
        is_buy = data["is_buy"]
        size_usd = float(data["size_usd"])
        leverage = int(data.get("leverage", 10))
        slippage = float(data.get("slippage", 0.05))

        logging.info(f"Setting leverage for {coin} to {leverage}x")
        self.exchange.update_leverage(leverage, coin, is_cross=True)

        mid_price = float(self.info.all_mids()[coin])
        size_in_coin = size_usd / mid_price
        
        logging.info(f"Placing market {'BUY' if is_buy else 'SELL'} for {size_in_coin:.4f} {coin} (~${size_usd})")
        order_result = self.exchange.market_open(coin, is_buy, size_in_coin, None, slippage)
        
        # Handle TP/SL if the order was filled
        if order_result["status"] == "ok" and "filled" in order_result["response"]["data"]["statuses"][0]:
            filled = order_result["response"]["data"]["statuses"][0]["filled"]
            pos_size = float(filled["totalSz"])
            
            tpsl_orders = self._place_tpsl_orders(data, coin, not is_buy, pos_size)
            return {"market_order": order_result, "tpsl_orders": tpsl_orders}
            
        return {"market_order": order_result}

    def _close_position(self, data):
        """Closes a market position."""
        coin = data["coin"]
        logging.info(f"Closing market position for {coin}")
        return {"close_order": self.exchange.market_close(coin)}

    def _place_tpsl_orders(self, data, coin, is_buy_tpsl, size):
        """Places take profit and stop loss orders."""
        results = []
        tp_price = data.get("tp_price")
        sl_price = data.get("sl_price")

        if tp_price:
            tp_order = {"trigger": {"triggerPx": float(tp_price), "isMarket": True, "tpsl": "tp"}}
            tp_result = self.exchange.order(coin, is_buy_tpsl, size, float(tp_price), tp_order, reduce_only=True)
            results.append({"tp_result": tp_result})
            logging.info(f"TP order placed: {tp_result}")

        if sl_price:
            sl_order = {"trigger": {"triggerPx": float(sl_price), "isMarket": True, "tpsl": "sl"}}
            sl_result = self.exchange.order(coin, is_buy_tpsl, size, float(sl_price), sl_order, reduce_only=True)
            results.append({"sl_result": sl_result})
            logging.info(f"SL order placed: {sl_result}")
        
        return results

def init_trading_service(app):
    """Factory function to create and attach the trading service to the app context."""
    app.trading_service = TradingService()