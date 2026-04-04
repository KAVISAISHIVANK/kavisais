# src/backtest.py
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
START_DATE = "2016-01-01"
END_DATE = "2026-01-01"
INITIAL_CAPITAL = 1000000  # 10L
POSITION_SIZE = 0.10  # 10% per trade

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "backtest_results.csv")

# Nifty 50 list (2026 snapshot, remove delisted if needed)
NIFTY50 = [
    "ADANIENT.NS","ASIANPAINT.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS",
    "BAJAJFINSV.NS","BPCL.NS","BHARTIARTL.NS","BRITANNIA.NS","CIPLA.NS",
    "COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS",
    "HCLTECH.NS","HDFCBANK.NS","HDFC.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDUNILVR.NS","ICICIBANK.NS","INDUSINDBK.NS","INFY.NS","ITC.NS",
    "JSWSTEEL.NS","KOTAKBANK.NS","LT.NS","M&M.NS","MARUTI.NS",
    "NESTLEIND.NS","NTPC.NS","ONGC.NS","POWERGRID.NS","RELIANCE.NS",
    "SBILIFE.NS","SHREECEM.NS","SBIN.NS","SUNPHARMA.NS","TCS.NS",
    "TATACONSUM.NS","TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS","TITAN.NS",
    "ULTRACEMCO.NS","UPL.NS","WIPRO.NS"
]

# -------------------------
# Helper functions
# -------------------------
def simulate_trades(df):
    """
    Generates BUY/EXIT signals using 20DMA and 50DMA strategy,
    returns a DataFrame of trades with PnL
    """
    df = df.copy()
    df['20DMA'] = df['Close'].rolling(20).mean()
    df['50DMA'] = df['Close'].rolling(50).mean()
    df = df.dropna(subset=['20DMA','50DMA'])  # avoid NaN issues

    trades = []
    holding = False
    entry_price = 0.0

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]

        # BUY signal: close > 50DMA and close near 20DMA, momentum check
        if not holding and row['Close'] > row['50DMA'] and abs(row['Close'] - row['20DMA'])/row['20DMA'] < 0.02 and row['High'] > prev['High']:
            holding = True
            entry_price = row['Close']
            trades.append({
                "Date": row.name.strftime("%Y-%m-%d"),
                "Signal": "BUY",
                "Price": entry_price
            })

        # EXIT signal: close < 20DMA
        elif holding and row['Close'] < row['20DMA']:
            holding = False
            exit_price = row['Close']
            trades.append({
                "Date": row.name.strftime("%Y-%m-%d"),
                "Signal": "EXIT",
                "Price": exit_price,
                "PnL": exit_price - entry_price
            })

    return pd.DataFrame(trades)

# -------------------------
# MAIN BACKTEST
# -------------------------
capital = INITIAL_CAPITAL
df_all_trades = pd.DataFrame()

for stock in NIFTY50:
    try:
        print(f"Processing {stock}...")
        df = yf.download(stock, start=START_DATE, end=END_DATE, interval="1d", progress=False)
        if df.empty or len(df) < 50:
            print(f"Skipping {stock}, insufficient data")
            continue

        trades = simulate_trades(df)
        if trades.empty:
            continue

        # Calculate position sizing
        trades['Qty'] = (capital * POSITION_SIZE / trades['Price']).apply(lambda x: int(x))
        trades['Stock'] = stock

        # Update capital for each exit
        exit_trades = trades[trades['Signal']=="EXIT"]
        for _, t in exit_trades.iterrows():
            pnl = t['Qty'] * t['PnL']
            capital += pnl

        df_all_trades = pd.concat([df_all_trades, trades], ignore_index=True)

    except Exception as e:
        print(f"Error processing {stock}: {e}")
        continue

# -------------------------
# CALCULATE METRICS
# -------------------------
if not df_all_trades.empty:
    exit_trades = df_all_trades[df_all_trades["Signal"]=="EXIT"]
    total_trades = len(exit_trades)
    wins = len(exit_trades[exit_trades["PnL"]>0])
    win_rate = round(wins/total_trades*100,2) if total_trades>0 else 0
    cagr = round(((capital/INITIAL_CAPITAL)**(1/10) -1)*100,2)  # 10 years
else:
    total_trades = 0
    win_rate = 0
    cagr = 0

# -------------------------
# SAVE CSV
# -------------------------
df_all_trades.to_csv(CSV_FILE, index=False)
print(f"Backtest completed. Results saved to {CSV_FILE}")
print(f"Total trades: {total_trades}, Win rate: {win_rate}%, CAGR: {cagr}%")
