import os
import pandas as pd
from datetime import datetime
import requests

# =========================
# Telegram alert function
# =========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_alert(msg):
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# Load signals
# =========================
signals_file = "data/signals.csv"  # adjust if needed
try:
    df_signals = pd.read_csv(signals_file)
except Exception as e:
    send_alert(f"⚠️ Backtest Error: signals.csv not found or empty.\n{e}")
    exit()

if df_signals.empty:
    send_alert("⚠️ Backtest: No signals to process.")
    exit()

# =========================
# Parameters
# =========================
initial_capital = 1000000  # ₹1,000,000
capital = initial_capital
max_per_trade = 0.1  # 10% of capital per trade
trades = []

# =========================
# Backtest loop
# =========================
for idx, row in df_signals.iterrows():
    stock = row['Stock']
    price = row['Price']
    signal = row['Signal']

    # Determine position size
    allocation = capital * max_per_trade
    qty = allocation / price

    if signal == "BUY":
        capital -= allocation
        trades.append({
            "Date": row['Date'],
            "Stock": stock,
            "Signal": signal,
            "Price": price,
            "Qty": round(qty, 2),
            "Capital Left": round(capital, 2)
        })
    elif signal == "EXIT":
        # simulate exit: assume sold at signal price
        # find matching buy
        for t in trades:
            if t["Stock"] == stock and t["Signal"] == "BUY":
                pnl = (price - t["Price"]) * t["Qty"]
                capital += t["Qty"] * price
                t["Exit_Price"] = price
                t["PnL"] = round(pnl, 2)
                trades.append({
                    "Date": row['Date'],
                    "Stock": stock,
                    "Signal": signal,
                    "Price": price,
                    "Qty": t["Qty"],
                    "Capital Left": round(capital, 2),
                    "PnL": round(pnl, 2)
                })
                break

# =========================
# Results summary
# =========================
df_trades = pd.DataFrame(trades)
wins = df_trades[df_trades.get('PnL', 0) > 0].shape[0]
total_trades = df_trades[df_trades['Signal'] == "EXIT"].shape[0]
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

# Send Telegram message
msg = f"📊 Backtest Completed ({datetime.now().strftime('%Y-%m-%d')}):\n" \
      f"Initial Capital: ₹{initial_capital:.2f}\n" \
      f"Final Capital: ₹{capital:.2f}\n" \
      f"Total Trades: {total_trades}\n" \
      f"Win Rate: {win_rate:.2f}%"
send_alert(msg)

# =========================
# Save detailed CSV
# =========================
df_trades.to_csv("data/backtest_results.csv", index=False)
