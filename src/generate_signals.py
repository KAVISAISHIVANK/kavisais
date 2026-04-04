import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from datetime import datetime
import requests
import os

# =========================
# TELEGRAM CONFIG (SECURE)
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
def send_alert(msg):
    if TOKEN is None or CHAT_ID is None:
        print("Telegram not configured")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram error:", e)
send_alert("✅ System is running")
# =========================
# STOCK LIST
# =========================
stocks = [
    "ADANIENT.NS","ADANIPORTS.NS","APOLLOHOSP.NS","ASIANPAINT.NS","AXISBANK.NS",
    "BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BEL.NS","BHARTIARTL.NS",
    "BPCL.NS","BRITANNIA.NS","CIPLA.NS","COALINDIA.NS","DRREDDY.NS",
    "EICHERMOT.NS","GRASIM.NS","HCLTECH.NS","HDFCBANK.NS","HDFCLIFE.NS",
    "HEROMOTOCO.NS","HINDALCO.NS","HINDUNILVR.NS","ICICIBANK.NS","INDUSINDBK.NS",
    "INFY.NS","ITC.NS","JSWSTEEL.NS","KOTAKBANK.NS","LT.NS",
    "M&M.NS","MARUTI.NS","NESTLEIND.NS","NTPC.NS","ONGC.NS",
    "POWERGRID.NS","RELIANCE.NS","SBILIFE.NS","SBIN.NS","SHRIRAMFIN.NS",
    "SUNPHARMA.NS","TATACONSUM.NS","TATAMOTORS.NS","TATASTEEL.NS","TCS.NS",
    "TECHM.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","LTIM.NS"
]


signals_data = []

# =========================
# MAIN LOOP
# =========================
for stock in stocks:
    try:
        df = yf.download(stock, period="6mo", interval="1d", progress=False)

        if df is None or df.empty:
            print(f"No data for {stock}")
            continue

        # Fix MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if "Close" not in df.columns or len(df) < 50:
            print(f"Invalid data for {stock}")
            continue

        # =========================
        # FIX CLOSE COLUMN (CRITICAL)
        # =========================
        close = df["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        close = close.astype(float)

        # =========================
        # INDICATORS
        # =========================
        df["RSI"] = RSIIndicator(close).rsi()

        macd = MACD(close)
        df["MACD"] = macd.macd()
        df["MACD_signal"] = macd.macd_signal()

        # =========================
        # LATEST VALUES
        # =========================
        latest = df.iloc[-1]

        signal = None

        # =========================
        # STRATEGY
        # =========================
        if latest["RSI"] < 35 and latest["MACD"] > latest["MACD_signal"]:
            signal = "BUY"

        elif latest["RSI"] > 65 and latest["MACD"] < latest["MACD_signal"]:
            signal = "EXIT"

        if signal is None:
            continue

        # =========================
        # CONFIDENCE
        # =========================
        momentum = (close.iloc[-1] / close.iloc[-20]) - 1
        confidence = round(min(max(momentum * 100, 50), 90), 2)

        price = float(close.iloc[-1])

        signals_data.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Stock": stock,
            "Signal": signal,
            "Price": round(price, 2),
            "Confidence": confidence
        })

        # Telegram alert
        send_alert(f"{signal}: {stock} @ {round(price,2)} | Conf: {confidence}%")

        print(f"{stock} → {signal}")

    except Exception as e:
        print(f"Error processing {stock}: {e}")

# =========================
# SAVE SIGNALS
# =========================
import os
os.makedirs("data", exist_ok=True)

df_signals = pd.DataFrame(signals_data)

if df_signals.empty:
    print("No signals generated")

    # ✅ Create empty file with columns (VERY IMPORTANT)
    df_signals = pd.DataFrame(columns=["Date","Stock","Signal","Price","Confidence"])

df_signals.to_csv("data/signals.csv", index=False)
print("signals.csv updated")
if len(signals_data) == 0:
    send_alert("📊 No trading signals today")

else:
    msg = "📊 Trading Signals Today:\n\n"
    
    for s in signals_data:
        msg += f"{s['Signal']} → {s['Stock']} @ {s['Price']} (Conf: {s['Confidence']}%)\n"
    
    send_alert(msg)
