import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# ------------------------------
# CONFIG
# ------------------------------
START_DATE = "2016-01-01"
END_DATE = "2026-04-04"
INITIAL_CAPITAL = 1_000_000
MAX_POSITIONS = 5
POSITION_SIZE = 0.10  # 10% of capital
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "backtest_results.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------------
# NIFTY 50 TICKERS
# ------------------------------
NIFTY50 = [
    "ADANIENT.NS","ASIANPAINT.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS",
    "BAJAJFINSV.NS","BPCL.NS","BHARTIARTL.NS","BRITANNIA.NS","CIPLA.NS",
    "COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS",
    "HCLTECH.NS","HDFCBANK.NS","HDFC.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDUNILVR.NS","ICICIBANK.NS","ITC.NS","INDUSINDBK.NS","INFY.NS",
    "JSWSTEEL.NS","KOTAKBANK.NS","LT.NS","M&M.NS","MARUTI.NS",
    "NESTLEIND.NS","NTPC.NS","ONGC.NS","POWERGRID.NS","RELIANCE.NS",
    "SBILIFE.NS","SBIN.NS","SUNPHARMA.NS","TCS.NS","TATACONSUM.NS",
    "TATASTEEL.NS","TECHM.NS","ULTRACEMCO.NS","UPL.NS","WIPRO.NS",
    "HINDPETRO.NS","SHREECEM.NS","HDFCLIFE.NS"
]

# ------------------------------
# PORTFOLIO VARIABLES
# ------------------------------
capital = INITIAL_CAPITAL
positions = {}  # stock -> dict(entry_price, qty, date)
trades = []

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def generate_signals(df):
    df = df.copy()
    df["20DMA"] = df["Close"].rolling(20).mean()
    df["50DMA"] = df["Close"].rolling(50).mean()

    signals = []

    for i in range(20, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        signal = None

        # Buy Signal
        if row["Close"] > row["50DMA"] and abs(row["Close"] - row["20DMA"])/row["20DMA"] < 0.02:
            if row["High"] > prev["High"]:
                signal = "BUY"

        # Exit Signal
        elif row["Close"] < row["20DMA"]:
            signal = "EXIT"

        if signal:
            momentum = (row["Close"] / df["Close"].iloc[i-20]) - 1
            confidence = round(min(max(momentum * 100, 50), 90), 2)
            signals.append({
                "Date": row.name.strftime("%Y-%m-%d"),
                "Signal": signal,
                "Price": row["Close"],
                "Confidence": confidence
            })
    return signals

# ------------------------------
# BACKTEST LOOP
# ------------------------------
for stock in NIFTY50:
    print(f"Processing {stock}...")
    try:
        df = yf.download(stock, start=START_DATE, end=END_DATE, interval="1d", progress=False)
        if df.empty or len(df) < 50:
            print(f"Skipping {stock}, insufficient data")
            continue

        df.index = pd.to_datetime(df.index)
        signals = generate_signals(df)
        if not signals:
            continue

        for sig in signals:
            date = sig["Date"]
            signal = sig["Signal"]
            price = sig["Price"]

            if signal == "BUY":
                if stock not in positions and len(positions) < MAX_POSITIONS:
                    allocation = capital * POSITION_SIZE
                    qty = int(allocation // price)
                    if qty > 0:
                        positions[stock] = {"entry_price": price, "qty": qty, "date": date}
                        capital -= qty * price
                        trades.append({
                            "Date": date, "Stock": stock, "Signal": "BUY",
                            "Price": price, "Qty": qty, "Capital": capital, "PnL": 0
                        })

            elif signal == "EXIT":
                if stock in positions:
                    qty = positions[stock]["qty"]
                    entry_price = positions[stock]["entry_price"]
                    pnl = (price - entry_price) * qty
                    capital += price * qty
                    trades.append({
                        "Date": date, "Stock": stock, "Signal": "EXIT",
                        "Price": price, "Qty": qty, "Capital": capital, "PnL": pnl
                    })
                    del positions[stock]

    except Exception as e:
        print(f"Error processing {stock}: {e}")
        continue

# ------------------------------
# CLOSE REMAINING POSITIONS
# ------------------------------
for stock, pos in positions.items():
    try:
        last_price = yf.download(stock, start=END_DATE, end=END_DATE, interval="1d", progress=False)["Close"].iloc[-1]
        qty = pos["qty"]
        capital += qty * last_price
        trades.append({
            "Date": END_DATE, "Stock": stock, "Signal": "EXIT",
            "Price": last_price, "Qty": qty, "Capital": capital, "PnL": (last_price - pos["entry_price"])*qty
        })
    except:
        continue

# ------------------------------
# SAVE CSV
# ------------------------------
df_trades = pd.DataFrame(trades)
#if not df_trades.empty:
#    df_trades.to_csv(CSV_FILE, index=False)
#    print(f"Backtest results saved to {CSV_FILE}")
    # Save CSV even if empty
df_trades.to_csv(CSV_FILE, index=False)
print(f"Backtest results saved to {CSV_FILE}")
# Metrics
exit_trades = df_trades[df_trades["Signal"]=="EXIT"]
total_trades = len(exit_trades)
wins = len(exit_trades[exit_trades["PnL"]>0])
win_rate = round(wins/total_trades*100,2) if total_trades>0 else 0
cagr = round(((capital/INITIAL_CAPITAL)**(1/10) -1)*100,2)
print(f"Initial Capital: ₹{INITIAL_CAPITAL}")
print(f"Final Capital: ₹{capital:.2f}")
print(f"Total Trades: {total_trades}")
print(f"Win Rate: {win_rate}%")
print(f"CAGR: {cagr}%")
#else:
#    print("No trades were executed in this backtest.")
