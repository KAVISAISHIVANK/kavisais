# src/backtest_local.py (updated for guaranteed CSV output)

import pandas as pd
import os

# -------------------------
# CONFIG
# -------------------------
INITIAL_CAPITAL = 1000000
POSITION_SIZE = 0.10
DATA_DIR = "stocks"
RESULTS_DIR = "data"
os.makedirs(RESULTS_DIR, exist_ok=True)
CSV_FILE = os.path.join(RESULTS_DIR, "backtest_results.csv")

# -------------------------
# Nifty 50 list
# -------------------------
NIFTY_50 = [
    "ADANIENT","ASIANPAINT","AXISBANK","BAJAJ-AUTO","BAJFINANCE",
    "BAJAJFINSV","BPCL","BHARTIARTL","BRITANNIA","CIPLA",
    "COALINDIA","DIVISLAB","DRREDDY","EICHERMOT","GRASIM",
    "HCLTECH","HDFCBANK","HDFC","HEROMOTOCO","HINDALCO",
    "HINDUNILVR","ICICIBANK","ITC","INDUSINDBK","INFY",
    "JSWSTEEL","KOTAKBANK","LT","M&M","MARUTI",
    "NESTLEIND","NTPC","ONGC","POWERGRID","RELIANCE",
    "SBILIFE","SBIN","SHREECEM","TATACONSUM","TATAMOTORS",
    "TATASTEEL","TECHM","TITAN","ULTRACEMCO","UPL",
    "WIPRO","TCS","HDFCLIFE"
]

# -------------------------
# Helper: simulate trades
# -------------------------
def simulate_trades(df):
    df = df.copy()
    df['Price'] = pd.to_datetime(df['Price'], format="%m/%d/%Y")
    df.set_index('Price', inplace=True)
    df['20DMA'] = df['Close'].rolling(20).mean()
    df['50DMA'] = df['Close'].rolling(50).mean()
    df = df.dropna(subset=['20DMA','50DMA'])

    trades = []
    holding = False
    entry_price = 0.0

    for i in range(1,len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]

        # BUY
        if not holding and row['Close'] > row['50DMA'] and abs(row['Close'] - row['20DMA'])/row['20DMA'] < 0.02:
            holding = True
            entry_price = row['Close']
            trades.append({
                "Date": row.name.strftime("%Y-%m-%d"),
                "Signal":"BUY",
                "Price": entry_price,
                "PnL": 0
            })

        # EXIT
        elif holding and row['Close'] < row['20DMA']:
            holding = False
            exit_price = row['Close']
            trades.append({
                "Date": row.name.strftime("%Y-%m-%d"),
                "Signal":"EXIT",
                "Price": exit_price,
                "PnL": exit_price - entry_price
            })

    return pd.DataFrame(trades)

# -------------------------
# MAIN BACKTEST
# -------------------------
capital = INITIAL_CAPITAL
df_all_trades = pd.DataFrame()

for file in os.listdir(DATA_DIR):
    if not file.endswith(".csv"):
        continue

    stock = file.replace(".csv","").upper()
    if stock not in NIFTY_50:
        print(f"{stock}: Skipped (not Nifty 50)")
        continue

    path = os.path.join(DATA_DIR, file)

    try:
        df = pd.read_csv(path, skiprows=[1,2])
        if 'Price' not in df.columns or 'Close' not in df.columns:
            print(f"{stock}: Missing columns")
            continue

        trades = simulate_trades(df)
        trades['Stock'] = stock
        trades['Qty'] = (capital * POSITION_SIZE / trades['Price']).apply(lambda x: int(x))

        # Safe capital update
        exit_trades = trades[trades['Signal']=="EXIT"]
        for _, t in exit_trades.iterrows():
            pnl = t['Qty'] * t['PnL']
            capital += pnl

        df_all_trades = pd.concat([df_all_trades, trades], ignore_index=True)
        print(f"{stock}: {len(trades)} trades")

    except Exception as e:
        print(f"Error processing {stock}: {e}")

# -------------------------
# METRICS
# -------------------------
if not df_all_trades.empty:
    exit_trades = df_all_trades[df_all_trades["Signal"]=="EXIT"]
    total_trades = len(exit_trades)
    wins = len(exit_trades[exit_trades["PnL"]>0])
    win_rate = round(wins/total_trades*100,2) if total_trades>0 else 0
    cagr = round(((capital/INITIAL_CAPITAL)**(1/10)-1)*100,2)
else:
    total_trades = 0
    win_rate = 0
    cagr = 0

# -------------------------
# SAVE CSV
# -------------------------
summary = pd.DataFrame([{
    "Total Trades": total_trades,
    "Win Rate (%)": win_rate,
    "CAGR (%)": cagr,
    "Final Capital": capital
}])

# Save both trades + summary
summary.to_csv(CSV_FILE, index=False)
df_all_trades.to_csv(CSV_FILE.replace(".csv","_details.csv"), index=False)

print("Backtest completed.")
print(f"Summary saved to {CSV_FILE}")
print(f"Detailed trades saved to {CSV_FILE.replace('.csv','_details.csv')}")
