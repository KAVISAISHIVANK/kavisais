import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# --- STOCK LIST ---
stocks = [
    "RELIANCE.NS",
    "ICICIBANK.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "TCS.NS"
]

# --- TELEGRAM ---
TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# --- STRATEGY ---
def get_signal(df):
    df['20DMA'] = df['Close'].rolling(20).mean()
    latest = df.iloc[-1]

    if latest['Close'] > latest['20DMA']:
        return "BUY"
    else:
        return "EXIT"

# --- RUN ---
signals_data = []

for stock in stocks:
    df = yf.download(stock, period="6mo", interval="1d")

    if len(df) < 50:
        continue

    signal = get_signal(df)
    price = df['Close'].iloc[-1]

    signals_data.append({
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Stock": stock,
        "Signal": signal,
        "Price": round(price, 2)
    })

    send_alert(f"{signal}: {stock} @ {price}")

# Save to CSV
df_signals = pd.DataFrame(signals_data)
df_signals.to_csv("signals.csv", index=False)
