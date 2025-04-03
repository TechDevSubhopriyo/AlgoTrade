import time
import pandas as pd

from connect import *
from handler import *
from constant import instrument_tokens
from signal import *
import constant


bought_stocks = {}
trade_history = {}



def Execute(stock, token, data):
    signal = EMA_5_13_50(data, stock, token)
    quantity = 1

    ema_data = data.iloc[-1]
    atr = ema_data["ATR"]
    close_price = ema_data["close"]

    stop_loss = close_price - (atr * 1.5)
    take_profit = close_price + (atr * 2)

    if stock in bought_stocks:
        for position in bought_stocks[stock]:
            entry_price = position['entry_price']
            if close_price <= position['stop_loss'] or close_price >= position['take_profit']:
                Order(stock, "SELL", close_price)
                return

    if signal == 1:
        Order(stock, "BUY", close_price, stop_loss, take_profit)

    elif signal==2 and stock in bought_stocks:
        Order(stock, "SELL", close_price)

def Order(stock, order_type, price=None, stop_loss=None, take_profit=None):
    try:
        quantity = 1  # Modify as needed
        #order = kite.place_order(
        #    variety=kite.VARIETY_REGULAR,
        #    exchange=kite.EXCHANGE_NSE,
        #    tradingsymbol=stock,
        #    transaction_type=kite.TRANSACTION_TYPE_BUY if order_type == "BUY" else kite.TRANSACTION_TYPE_SELL,
        #    quantity=quantity,
        #    order_type=kite.ORDER_TYPE_MARKET,
        #    product=kite.PRODUCT_MIS
        #)
        order = 0

        if order_type == "BUY":
            print(f"🔼 {order_type} Order Placed for {stock} @ {price}")
            if stock not in bought_stocks:
                bought_stocks[stock] = []
            bought_stocks[stock].append({'quantity': quantity, 'entry_price': price, 'stop_loss': stop_loss, 'take_profit': take_profit})
        elif order_type == "SELL" and stock in bought_stocks:
            print(f"🔽 {order_type} Order Placed for {stock} @ {price}")
            if bought_stocks[stock]:
                bought_stocks[stock].pop(0)  # Remove oldest position first
            if not bought_stocks[stock]:
                del bought_stocks[stock]  # Remove stock entry if all positions are sold
    except Exception as e:
        print(f"❌ Order Failed for {stock}: {e}")

def main():

    constant.init()
    # Connect to zerodha using access token
    constant.kite, constant.kws = ConnectZerodha()

    # Display profile information
    ShowProfile(constant.kite)

    constant.kws.on_ticks = on_ticks
    constant.kws.on_connect = on_connect
    constant.kws.on_close = on_close
    constant.kws.connect(threaded=True)

    while not constant.kws.is_connected():
        print("🚀 Waiting for WebSocket connection...")
        time.sleep(2)

    while True:
        for stock, token in instrument_tokens.items():
            data = FetchData(token, "close", interval="minute")
            if data is None:
                continue
            Execute(stock, token, data)

        time.sleep(60)  # Fetch every 1 minute


main()


