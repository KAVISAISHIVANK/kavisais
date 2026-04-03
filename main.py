import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# =========================
# STOCK LIST
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
# LOAD PORTFOLIO
# =========================
def load_portfolio():
    try:
        df = pd.read_csv("portfolio.csv")
        return df
    except:
        return pd.DataFrame(columns=["Stock","Entry","Qty","SL","Status"])

# =========================
# MAIN EXECUTION
# =========================
portfolio = load_portfolio()
holding_stocks = portfolio[portfolio["Status"] == "HOLD"]["Stock"].tolist()

signals_data = []

for stock in stocks:
    try:
        df = yf.download(stock, period="6mo", interval="1d", progress=False)

        # Validate data
        if df is None or df.empty:
            print(f"No data for {stock}")
            continue

        # Fix MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        print(f"{stock} columns: {df.columns}")

        # Check Close exists
        if 'Close' not in df.columns:
            print(f"'Close' missing for {stock}")
            continue

        if len(df) < 50:
            continue

        # =========================
        # STRATEGY (Step 3)
        # =========================
        df['20DMA'] = df['Close'].rolling(20).mean()
        df['50DMA'] = df['Close'].rolling(50).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close = float(latest['Close'])
        dma20 = float(latest['20DMA'])
        dma50 = float(latest['50DMA'])

        signal = None

        if close > dma50:
            if abs(close - dma20) / dma20 < 0.02:
                if float(latest['High']) > float(prev['High']):
                    signal = "BUY"

        elif close < dma20:
            signal = "EXIT"

        # =========================
        # PORTFOLIO FILTER
        # =========================
        if signal == "EXIT" and stock not in holding_stocks:
            print(f"Skipping EXIT for {stock} (not in portfolio)")
            continue

        if signal == "BUY" and stock in holding_stocks:
            print(f"Skipping BUY for {stock} (already holding)")
            continue

        if signal is None:
            continue

        # =========================
        # CONFIDENCE (Step 4)
        # =========================
        momentum = (df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1
        confidence = round(min(max(momentum * 100, 50), 90), 2)

        price = close

        # =========================
        # SAVE SIGNAL
        # =========================
        signals_data.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Stock": stock,
            "Signal": signal,
            "Price": round(price, 2),
            "Confidence": confidence
        })

        # Telegram alert
        send_alert(f"{signal}: {stock} @ {round(price,2)} | Conf: {confidence}%")

    except Exception as e:
        print(f"Error processing {stock}: {e}")

# =========================
# DEBUG
# =========================
print(f"Signals generated: {len(signals_data)}")
print(signals_data)

# =========================
# STEP 5: TOP 5 FILTER
# =========================
signals_data = sorted(signals_data, key=lambda x: x['Confidence'], reverse=True)
signals_data = signals_data[:5]

# =========================
# SAVE TO CSV (IMPORTANT FIX)
# =========================
df_signals = pd.DataFrame(signals_data)

if df_signals.empty:
    print("No signals today")
else:
    try:
        old = pd.read_csv("signals.csv")
        df_signals = pd.concat([old, df_signals], ignore_index=True)
    except:
        pass

df_signals.to_csv("signals.csv", index=False)
