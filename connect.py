import os
import sys
import json
from datetime import datetime
from kiteconnect import KiteConnect, KiteTicker

def ConnectZerodha():

    kite = None
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
    if os.path.exists(f"AccessToken/{datetime.now().date()}.json"):
        with open(f"AccessToken/{datetime.now().date()}.json", "r") as f:
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
            with open(f"AccessToken/{datetime.now().date()}.json", "w") as f:
                json.dump(access_token, f)
            print("Login successful...")
        except Exception as e:
            print(f"Login Failed {{{e}}}")
            sys.exit()

    # WebSocket Connection
    kws = KiteTicker(login_credential["api_key"], access_token)

    return kite, kws


def ShowProfile(kite):

    profile = kite.profile()
    print(profile)
    print("Logged in as: ",(profile["user_name"]))
    print("UID: ",(profile["user_id"]))

