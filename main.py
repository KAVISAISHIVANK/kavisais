import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# --- TELEGRAM ---
TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# --- STRATEGY ---
def get_signal(df):
    df['20DMA'] = df['Close'].rolling(20).mean()
    df['50DMA'] = df['Close'].rolling(50).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if latest['Close'] > latest['50DMA']:
        if abs(latest['Close'] - latest['20DMA']) < 0.02 * latest['20DMA']:
            if latest['High'] > prev['High']:
                return "BUY"

    if latest['Close'] < latest['20DMA']:
        return "EXIT"

    return None

# --- RUN ---
stocks = ["RELIANCE.NS","ICICIBANK.NS","HDFCBANK.NS","INFY.NS","TCS.NS"]

signals = []

for stock in stocks:
    df = yf.download(stock, period="6mo", interval="1d")

    if len(df) < 50:
        continue

    signal = get_signal(df)

    if signal:
        msg = f"{signal}: {stock}"
        signals.append(msg)

# --- ALERT ---
if signals:
    final_msg = "\n".join(signals)
    send_alert(final_msg)
