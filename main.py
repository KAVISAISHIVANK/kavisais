import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# =========================
# STOCK LIST (NIFTY SAMPLE)
# =========================
stocks = [
    "RELIANCE.NS",
    "ICICIBANK.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "TCS.NS"
]

# =========================
# TELEGRAM CONFIG
# =========================
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =========================
# STRATEGY FUNCTION
# =========================
def get_signal(df):
    df['20DMA'] = df['Close'].rolling(20).mean()

    latest = df.iloc[-1]

    # Convert to float (fix pandas issue)
    close = float(latest['Close'])
    dma20 = float(latest['20DMA'])

    if close > dma20:
        return "BUY"
    else:
        return "EXIT"

# =========================
# MAIN EXECUTION
# =========================
signals_data = []

for stock in stocks:
    try:
        df = yf.download(stock, period="6mo", interval="1d", progress=False)

        # Check if data exists
        if df is None or df.empty:
            print(f"No data for {stock}")
            continue

        # Fix MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        print(f"{stock} columns: {df.columns}")  # DEBUG

        # Ensure Close column exists
        if 'Close' not in df.columns:
            print(f"'Close' missing for {stock}")
            continue

        if len(df) < 50:
            continue

        # Calculate indicator
        df['20DMA'] = df['Close'].rolling(20).mean()

        latest = df.iloc[-1]

        close = float(latest['Close'])
        dma20 = float(latest['20DMA'])

        if close > dma20:
            signal = "BUY"
        else:
            signal = "EXIT"

        price = close

        signals_data.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Stock": stock,
            "Signal": signal,
            "Price": round(price, 2)
        })

        send_alert(f"{signal}: {stock} @ {round(price,2)}")

    except Exception as e:
        print(f"Error processing {stock}: {e}")
        
# =========================
# SAVE TO CSV
# =========================
if signals_data:
    df_signals = pd.DataFrame(signals_data)

    try:
        old = pd.read_csv("signals.csv")
        df_signals = pd.concat([old, df_signals], ignore_index=True)
    except:
        pass

    df_signals.to_csv("signals.csv", index=False)
