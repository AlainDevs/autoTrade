# File: src/services/trading_service.py

import json
import os
import logging
import time
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
        
        # Track last trade time per coin for cooldown
        self.last_trade_time = {}
        self.trade_cooldown_seconds = self.config.get("trade_cooldown_seconds", 5)
        logging.info(f"Trade cooldown set to {self.trade_cooldown_seconds} seconds")

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
        
        # Check cooldown for "open" actions
        if action == "open":
            coin = data.get("coin")
            current_time = time.time()
            
            # Check if we have a recent trade for this coin
            if coin in self.last_trade_time:
                time_since_last_trade = current_time - self.last_trade_time[coin]
                if time_since_last_trade < self.trade_cooldown_seconds:
                    remaining_cooldown = self.trade_cooldown_seconds - time_since_last_trade
                    logging.warning(
                        f"Trade rejected for {coin}: cooldown active. "
                        f"Time since last trade: {time_since_last_trade:.2f}s, "
                        f"remaining cooldown: {remaining_cooldown:.2f}s"
                    )
                    return {
                        "error": "Trade rejected due to cooldown",
                        "coin": coin,
                        "time_since_last_trade": round(time_since_last_trade, 2),
                        "cooldown_remaining": round(remaining_cooldown, 2)
                    }
            
            # Update last trade time for this coin
            self.last_trade_time[coin] = current_time
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

        # Get asset metadata to determine correct decimal precision
        meta = self.info.meta()
        asset_info = next((asset for asset in meta["universe"] if asset["name"] == coin), None)
        if not asset_info:
            raise ValueError(f"Asset {coin} not found in metadata")
        
        # Log the full asset_info to understand available fields
        logging.info(f"Asset metadata for {coin}: {json.dumps(asset_info, indent=2)}")
        
        sz_decimals = asset_info["szDecimals"]
        
        mid_price = float(self.info.all_mids()[coin])
        size_in_coin = size_usd / mid_price
        # Round to the correct number of decimals for this specific coin
        size_in_coin = round(size_in_coin, sz_decimals)
        
        logging.info(f"Placing market {'BUY' if is_buy else 'SELL'} for {size_in_coin:.4f} {coin} (~${size_usd})")
        order_result = self.exchange.market_open(coin, is_buy, size_in_coin, None, slippage)
        
        # Log the complete order result for debugging
        logging.info(f"Order result: {json.dumps(order_result, indent=2)}")
        
        # Check if order was successful
        if order_result.get("status") != "ok":
            logging.error(f"Order failed with status: {order_result.get('status')}")
            return {"market_order": order_result, "error": "Order placement failed"}
        
        # Handle TP/SL if the order was filled
        if "filled" in order_result["response"]["data"]["statuses"][0]:
            filled = order_result["response"]["data"]["statuses"][0]["filled"]
            pos_size = float(filled["totalSz"])
            entry_price = float(filled["avgPx"])
            
            tpsl_orders = self._place_tpsl_orders(data, coin, not is_buy, pos_size, entry_price, is_buy, meta)
            
            # Log successful order details
            logging.info(f"Order filled successfully! Size: {pos_size} {coin}, Entry Price: {entry_price}")
            return {"market_order": order_result, "tpsl_orders": tpsl_orders}
        
        # If we get here, the order was placed but not filled
        logging.warning(f"Order placed but not filled. Full response: {json.dumps(order_result, indent=2)}")
        
        # Check actual position state after order attempt
        try:
            user_state = self.info.user_state(self.address)
            positions = user_state.get("assetPositions", [])
            coin_position = next((p for p in positions if p["position"]["coin"] == coin), None)
            if coin_position:
                logging.info(f"Current position for {coin}: {json.dumps(coin_position, indent=2)}")
            else:
                logging.warning(f"No position found for {coin} after order attempt")
        except Exception as e:
            logging.error(f"Error checking position state: {e}")
        
        return {"market_order": order_result}

    def _close_position(self, data):
        """Closes a market position."""
        coin = data["coin"]
        logging.info(f"Closing market position for {coin}")
        return {"close_order": self.exchange.market_close(coin)}

    def _parse_price_or_percentage(self, value, entry_price, is_buy, is_take_profit):
        """
        Parses a price value that can be either a precise price or a percentage.
        
        Args:
            value: Either a percentage string (e.g., "5%", "0.05") or a precise price
            entry_price: The entry price of the position
            is_buy: Whether the position is a buy (long)
            is_take_profit: Whether this is for take profit (True) or stop loss (False)
        
        Returns:
            The calculated price as a float
        """
        value_str = str(value).strip()
        
        # Check if it's a percentage string (ends with %)
        if value_str.endswith('%'):
            percentage = float(value_str[:-1]) / 100.0
        # Check if it's a small decimal value (likely a percentage in decimal form)
        elif 0 < float(value_str) < 1:
            percentage = float(value_str)
        else:
            # It's a precise price
            return float(value_str)
        
        # Calculate the target price based on percentage
        if is_take_profit:
            # For take profit: long positions go up, short positions go down
            if is_buy:
                return entry_price * (1 + percentage)
            else:
                return entry_price * (1 - percentage)
        else:
            # For stop loss: long positions go down, short positions go up
            if is_buy:
                return entry_price * (1 - percentage)
            else:
                return entry_price * (1 + percentage)

    def _place_tpsl_orders(self, data, coin, is_buy_tpsl, size, entry_price, is_buy, meta):
        """Places take profit and stop loss orders."""
        results = []
        tp_price_input = data.get("tp_price")
        sl_price_input = data.get("sl_price")

        # Find the asset in metadata to get its szDecimals
        asset_info = next((asset for asset in meta["universe"] if asset["name"] == coin), None)
        if not asset_info:
            raise ValueError(f"Asset {coin} not found in metadata for TP/SL pricing")
        
        sz_decimals = asset_info.get("szDecimals")
        if sz_decimals is None:
             raise ValueError(f"'szDecimals' not found for asset {coin} in metadata")

        # From Hyperliquid docs/examples, price precision is derived from szDecimals.
        # MAX_DECIMALS is 6 for perpetuals.
        MAX_DECIMALS_FOR_PRICE = 6
        price_decimals = MAX_DECIMALS_FOR_PRICE - sz_decimals
        
        logging.info(f"Using {price_decimals} decimals for {coin} TP/SL prices (derived from szDecimals={sz_decimals})")

        if tp_price_input:
            tp_price = self._parse_price_or_percentage(tp_price_input, entry_price, is_buy, True)
            
            # Apply rounding rules from Hyperliquid docs: 5 significant figures, then round to derived decimal places.
            tp_price_rounded = round(float(f"{tp_price:.5g}"), price_decimals)
            
            logging.info(f"TP trigger price: {tp_price_rounded} (calculated from {tp_price_input}, entry: {entry_price})")

            # FIX: Pass the rounded FLOAT to the order dictionary, not the formatted string.
            tp_order = {"trigger": {"triggerPx": tp_price_rounded, "isMarket": True, "tpsl": "tp"}}
            
            # FIX: Pass the rounded FLOAT as the limit_px argument as well.
            tp_result = self.exchange.order(coin, is_buy_tpsl, size, tp_price_rounded, tp_order, reduce_only=True)
            
            results.append({"tp_result": tp_result})
            logging.info(f"TP order result: {tp_result}")

        if sl_price_input:
            sl_price = self._parse_price_or_percentage(sl_price_input, entry_price, is_buy, False)

            # Apply rounding rules from Hyperliquid docs.
            sl_price_rounded = round(float(f"{sl_price:.5g}"), price_decimals)
            
            logging.info(f"SL trigger price: {sl_price_rounded} (calculated from {sl_price_input}, entry: {entry_price})")

            # FIX: Pass the rounded FLOAT to the order dictionary, not the formatted string.
            sl_order = {"trigger": {"triggerPx": sl_price_rounded, "isMarket": True, "tpsl": "sl"}}
            
            # FIX: Pass the rounded FLOAT as the limit_px argument as well.
            sl_result = self.exchange.order(coin, is_buy_tpsl, size, sl_price_rounded, sl_order, reduce_only=True)
            
            results.append({"sl_result": sl_result})
            logging.info(f"SL order result: {sl_result}")
        
        return results

def init_trading_service(app):
    """Factory function to create and attach the trading service to the app context."""
    app.trading_service = TradingService()