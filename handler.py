
from constant import instrument_tokens

def on_connect(ws, response):
    ws.subscribe(list(instrument_tokens.values()))
    ws.set_mode(ws.MODE_FULL, list(instrument_tokens.values()))
    print("✅ WebSocket connected!")

def on_close(ws, code, reason):
    print("WebSocket closed:", reason)

def on_ticks(ws, ticks):
    return
    for tick in ticks:
        token = tick["instrument_token"]
        for stock, inst_token in instrument_tokens.items():
            if token == inst_token:
                print(f"📊 {stock} | Live Price: {tick['last_price']}")

