import json
import os
import logging
from eth_account import Account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

def setup_exchange():
    """Loads configuration and initializes the Exchange and Info objects."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path) as f:
        config = json.load(f)

    if not config.get("secret_key"):
        raise ValueError("secret_key must be set in config.json")

    account: LocalAccount = Account.from_key(config["secret_key"])
    address = config.get("account_address") or account.address
    
    logging.info(f"Initializing exchange for account: {address}")
    
    # Use TESTNET for development, MAINNET for production
    base_url = constants.MAINNET_API_URL if config.get("is_mainnet") else constants.TESTNET_API_URL
    
    info = Info(base_url, skip_ws=True)
    exchange = Exchange(account, base_url, account_address=address)
    
    return config, exchange, info

def handle_order(data, exchange: Exchange, info: Info):
    """Parses webhook data and executes the appropriate trade action."""
    action = data.get("action")
    coin = data.get("coin")
    
    if not action or not coin:
        return {"error": "Missing 'action' or 'coin' in payload"}

    if action.lower() == "open":
        return open_position(data, exchange, info)
    elif action.lower() == "close":
        return close_position(data, exchange)
    else:
        return {"error": f"Unsupported action: {action}"}

def open_position(data, exchange: Exchange, info: Info):
    """Opens a new market position with optional leverage, TP, and SL."""
    coin = data["coin"]
    is_buy = data["is_buy"]
    size_usd = float(data["size_usd"])
    leverage = int(data.get("leverage", 10))
    slippage = float(data.get("slippage", 0.05))

    # 1. Update Leverage
    logging.info(f"Setting leverage for {coin} to {leverage}x")
    exchange.update_leverage(leverage, coin, is_cross=True) # Assuming cross margin

    # 2. Calculate size in coin units
    mid_price = float(info.all_mids()[coin])
    size_in_coin = size_usd / mid_price
    
    # 3. Place Market Order
    logging.info(f"Placing market {'BUY' if is_buy else 'SELL'} order for {size_in_coin:.4f} {coin} (~${size_usd})")
    order_result = exchange.market_open(coin, is_buy, size_in_coin, None, slippage)
    
    # 4. Handle TP/SL if the order was filled
    if order_result["status"] == "ok" and "filled" in order_result["response"]["data"]["statuses"][0]:
        filled_status = order_result["response"]["data"]["statuses"][0]["filled"]
        position_size = float(filled_status["totalSz"])
        
        tp_price = data.get("tp_price")
        sl_price = data.get("sl_price")
        
        tpsl_orders = []
        # Set Take Profit
        if tp_price:
            tp_order_type = {"trigger": {"triggerPx": float(tp_price), "isMarket": True, "tpsl": "tp"}}
            tp_result = exchange.order(coin, not is_buy, position_size, float(tp_price), tp_order_type, reduce_only=True)
            tpsl_orders.append({"tp_result": tp_result})
            logging.info(f"TP order placed: {tp_result}")

        # Set Stop Loss
        if sl_price:
            sl_order_type = {"trigger": {"triggerPx": float(sl_price), "isMarket": True, "tpsl": "sl"}}
            sl_result = exchange.order(coin, not is_buy, position_size, float(sl_price), sl_order_type, reduce_only=True)
            tpsl_orders.append({"sl_result": sl_result})
            logging.info(f"SL order placed: {sl_result}")
            
        return {"market_order": order_result, "tpsl_orders": tpsl_orders}
        
    return {"market_order": order_result}


def close_position(data, exchange: Exchange):
    """Closes an existing market position for a given coin."""
    coin = data["coin"]
    logging.info(f"Closing market position for {coin}")
    order_result = exchange.market_close(coin)
    return {"close_order": order_result}