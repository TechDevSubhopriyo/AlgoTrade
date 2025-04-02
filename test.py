import os
import time
import datetime
try:
    import kiteconnect
except ImportError:
    os.system('python -m pip install kiteconnect')

import sys
import json

import logging
from kiteconnect import KiteConnect, KiteTicker
import pandas as pd

instrument_tokens = {
    "RELIANCE": 738561,
    "TCS": 2953217,
    "SUZLON": 3076609,
    "SASKEN": 3067649,
    "ONGC":128079876
}

kws = 0


def ConnectZerodha():
    global kite, kws

    login_credential = {"api_key": "", "api_secret": ""}
    print("Zerodha Login Credentials")
    try:
        with open(f"credentials.json", "r") as f:
            login_credential = json.load(f)
            print("Loggin in as: ", login_credential)
    except:
        login_credential = {"api_key": str(input("Enter API Key :")),
                        "api_secret": str(input("Enter API Secret :"))}
        if input("Press Y to save login credential and any key to bypass : ").upper() == "Y":
            with open(f"credentials.json", "w") as f:
                json.dump(login_credential, f)
            print("Credentials Saved in credentials.json")
        else:
            print("Credentials not saved!")

    print("Getting Access Token")
    if os.path.exists(f"AccessToken/{datetime.datetime.now().date()}.json"):
        with open(f"AccessToken/{datetime.datetime.now().date()}.json", "r") as f:
            access_token = json.load(f)
            kite = KiteConnect(api_key=login_credential["api_key"])
            kite.set_access_token(access_token)
    else:
        print("Trying Log In...")
        kite = KiteConnect(api_key=login_credential["api_key"])
        print("Login url : ", kite.login_url())
        request_tkn = input("Login and enter your 'request token' here : ")
        try:
            access_token = kite.generate_session(request_token=request_tkn,
                                                 api_secret=login_credential["api_secret"])['access_token']
            os.makedirs(f"AccessToken", exist_ok=True)
            with open(f"AccessToken/{datetime.datetime.now().date()}.json", "w") as f:
                json.dump(access_token, f)
            print("Login successful...")
        except Exception as e:
            print(f"Login Failed {{{e}}}")
            sys.exit()

    # WebSocket Connection
    kws = KiteTicker(login_credential["api_key"], access_token)



def ShowProfile():
    global kite

    profile = kite.profile()
    print(profile)
    print("Logged in as: ",(profile["user_name"]))
    print("UID: ",(profile["user_id"]))

def EMA(df, column, span):
    return df[column].ewm(span=span, adjust=False).mean()

def SMA(df, column, span):
    return df[column].rolling(window=span).mean()

def RSI(df, column, period=14):
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def FetchData(token, column, interval="15minute"):
    try:
        data = kite.historical_data(token, pd.Timestamp.now() - pd.Timedelta(days=10), pd.Timestamp.now(), interval)
        df = pd.DataFrame(data)

        # Calculate EMA and RSI values and add it to the dataframe
        df["EMA_5"] = EMA(df, column, 5)
        df["EMA_13"] = EMA(df, column, 13)
        df["EMA_55"] = EMA(df, column, 55)
        df["RSI"] = RSI(df, column)

        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

def CheckSignal(stock, data):
    # Get the calculated EMAs
    ema_data = data.iloc[-1]
    ema_prev = data.iloc[-2]

    if ema_data is None:
        return
    if ema_prev is None:
        ema_prev = ema_data

    ema_5 = ema_data["EMA_5"]
    ema_13 = ema_data["EMA_13"]
    ema_55 = ema_data["EMA_55"]
    rsi = ema_data["RSI"]

    # to make it simpler, remove last condition
    if ema_5 > ema_13 and ema_5 > ema_55 and ema_13 > ema_55 and rsi > 50 and ema_prev["EMA_5"] < ema_prev["EMA_13"]:
        print("BUY: ", stock)

    elif ema_5 < ema_13 and ema_5 < ema_55 and ema_13 < ema_55 and rsi < 50 and ema_prev["EMA_5"] > ema_prev["EMA_13"]:
        print("SELL: ", stock)

def on_connect(ws, response):
    ws.subscribe(list(instrument_tokens.values()))
    ws.set_mode(ws.MODE_FULL, list(instrument_tokens.values()))
    print("Websocket connecteed")

def on_close(ws, code, reason):
    print("WebSocket closed:", reason)

def on_ticks(ws, ticks):
    return
    for tick in ticks:
        token = tick["instrument_token"]
        for stock, inst_token in instrument_tokens.items():
            if token == inst_token:
                print(f"📊 {stock} | Live Price: {tick['last_price']}")


def main():
    while True:
        for stock, token in instrument_tokens.items():
            data = FetchData(token, "close", interval="minute")
            CheckSignal(stock, data)

        time.sleep(60)  # Fetch every 10 minutes


def start_websocket():
    global kws

    # Connect to zerodha using access token
    ConnectZerodha()

    # Display profile information
    ShowProfile()

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.connect(threaded=True)

    main()

# Start WebSocket connection
start_websocket()

