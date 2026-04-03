def load_portfolio():
    try:
        df = pd.read_csv("portfolio.csv")
        return df
    except:
        return pd.DataFrame(columns=["Stock","Entry","Qty","SL","Status"])
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
portfolio = load_portfolio()
holding_stocks = portfolio[portfolio["Status"] == "HOLD"]["Stock"].tolist()
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
        # Indicators
        df['20DMA'] = df['Close'].rolling(20).mean()
        df['50DMA'] = df['Close'].rolling(50).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        close = float(latest['Close'])
        dma20 = float(latest['20DMA'])
        dma50 = float(latest['50DMA'])
        
        # Strategy: Trend + Pullback + Breakout
        signal = None
        
        if close > dma50:
            if abs(close - dma20) / dma20 < 0.02:
                if float(latest['High']) > float(prev['High']):
                    signal = "BUY"
        
        elif close < dma20:
            signal = "EXIT"
    
        price = close
        # Confidence score (simple momentum-based)
        momentum = (df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1
        confidence = round(min(max(momentum * 100, 50), 90), 2)
        # Skip useless EXIT signals
        if signal == "EXIT" and stock not in holding_stocks:
            continue
        
        # Skip duplicate BUY signals
        if signal == "BUY" and stock in holding_stocks:
            continue
            
        if stock in holding_stocks and signal != "EXIT":
            signal = "HOLD"
            
        if signal is None:
            continue
        signals_data.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Stock": stock,
            "Signal": signal,
            "Price": round(price, 2),
            "Confidence": confidence
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
    # Sort by confidence (highest first)
    signals_data = sorted(signals_data, key=lambda x: x['Confidence'], reverse=True)

    # Keep only top 5
    signals_data = signals_data[:5]
    df_signals.to_csv("signals.csv", index=False)
