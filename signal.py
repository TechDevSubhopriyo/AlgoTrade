### THIS FILE CONTAINS TRADING STRATEGIES ###
### THE FOLLOWING ARE THE RETURN VALUES:
### 1 -> BUY
### 2 -> SELL
### 3 -> HOLD


import pandas as pd
import constant
from algorithm import *


### THIS METHOD IS USED TO FETCH THE HISTORICAL DATA AND CALCULATE COMMONLY USED INDICATORS ###
def FetchData(token, column, interval="15minute"):
    try:
        data = constant.kite.historical_data(token, pd.Timestamp.now() - pd.Timedelta(days=10), pd.Timestamp.now()- pd.Timedelta(days=1), interval)
        df = pd.DataFrame(data)

        # Commonly used indicators
        df["EMA_5"] = EMA(df, column, 5)
        df["EMA_13"] = EMA(df, column, 13)
        df["EMA_50"] = EMA(df, column, 50)
        df["EMA_55"] = EMA(df, column, 55)
        df["RSI"] = RSI(df, column, 14)
        df["RSI_7"] = RSI(df, column, 7)

        # Calculate ATR (Average True Range) for Dynamic SL/TP
        df['TR'] = df[['high', 'low', 'close']].max(axis=1) - df[['high', 'low', 'close']].min(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()

        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

def EMA_5_13_50(data, stock, token=""):
    if data is None:
        return
    # Get the calculated EMAs
    ema_data = data.iloc[-1]
    ema_prev = data.iloc[-2]

    if ema_data is None or ema_prev is None:
        return

    ema_5 = ema_data["EMA_5"]
    ema_13 = ema_data["EMA_13"]
    ema_50 = ema_data["EMA_50"]
    ema_50_prev = ema_prev["EMA_50"]
    rsi = ema_data["RSI_7"]

    momentum = 1
    if token != "":
        # Additional data to check momentum on 5min and 15min
        data_5 = FetchData(token, "close", interval="5minute")
        data_15 = FetchData(token, "close", interval="15minute")

        if data_5 is not None and data_15 is not None and data_5.iloc[-1]["EMA_50"] < data_15.iloc[-1]["EMA_50"]:
            momentum = 0

    if ema_5 > ema_13 and ema_13 > ema_50 and rsi > 55 and ema_50 > ema_50_prev and momentum == 1:
        return 1

    elif ema_5 < ema_13 and ema_13 < ema_50 and rsi < 45 :
        return 2

    else:
        return 3

def EMA_RSI(data, stock, token):
    ema_data = data.iloc[-1]
    ema_prev = data.iloc[-2]

    if ema_data is None or ema_prev is None:
        return

    rsi = ema_data["RSI"]
    ema_50 = ema_data["EMA_50"]
    ema_50_prev = ema_prev["EMA_50"]
    close_price = ema_data["close"]

    # Buy Condition: RSI > 30 & price > EMA(50)
    if rsi > 30 and close_price > ema_50 and ema_50 > ema_50_prev:
        return 1

    # Sell Condition: RSI < 70 & price < EMA(50)
    elif rsi < 70 and close_price < ema_50:
        return 2

    else:
        return 3
