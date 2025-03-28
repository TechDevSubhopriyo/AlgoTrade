import os
import datetime
try:
    import kiteconnect
except ImportError:
    os.system('python3 -m pip install kiteconnect')

import sys
import json

import logging
from kiteconnect import KiteConnect

from tkinter import *
root = Tk()
#root.geometry("400x300")

login_credential = {"api_key": "", "api_secret": ""}

def ConnectZerodha():
    global login_credential
    global kite

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
            access_token = kite.generate_session(request_token=request_tkn, api_secret=login_credential["api_secret"])[
                'access_token']
            os.makedirs(f"AccessToken", exist_ok=True)
            with open(f"AccessToken/{datetime.datetime.now().date()}.json", "w") as f:
                json.dump(access_token, f)
            print("Login successful...")
        except Exception as e:
            print(f"Login Failed {{{e}}}")
            sys.exit()


def ShowProfile():
    global kite
    logging.basicConfig(level=logging.DEBUG)

    profile = kite.profile()
    print(profile)
    name['text'] = (profile["user_name"])
    uid['text'] = ("UID: "+profile["user_id"])

def AddStock():
    global kite
    instruments = kite.instruments()

    for instrument in instruments:
        if (instrument["exchange"] == "NSE"):
            stockList.insert(stockList.size(), instrument["name"])


# Connect to zerodha using access token
ConnectZerodha()

name = Label(root, text="Not logged in!")
name.grid(row=0, column=0)
uid = Label(root, text="")
uid.grid(row=1, column=0)

# Display profile information
ShowProfile()

Button(root, text="All Stocks", command=AddStock).grid(row=2, column=0)
stockList = Listbox(root, width=40)
stockList.grid(row=2, column=1)

root.mainloop()
