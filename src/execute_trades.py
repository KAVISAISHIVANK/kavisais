import pandas as pd
from datetime import datetime

initial_capital = 500000
max_positions = 5

signals = pd.read_csv("data/signals.csv")

# Load or create portfolio
try:
    portfolio = pd.read_csv("data/portfolio.csv")
except:
    portfolio = pd.DataFrame(columns=["Stock","Buy Price","Quantity","Buy Date"])

# Load or create trades
try:
    trades = pd.read_csv("data/trades.csv")
except:
    trades = pd.DataFrame(columns=["Stock","Buy Price","Sell Price","Quantity","Buy Date","Sell Date","PnL","PnL %"])

new_portfolio = portfolio.copy()
new_trades = trades.copy()

holding_stocks = portfolio["Stock"].tolist()

for _, row in signals.iterrows():
    stock = row["Stock"]
    signal = row["Signal"]
    price = row["Price"]
    confidence = row["Confidence"]

    # ---------------- BUY ----------------
    if signal == "BUY":
        if stock not in holding_stocks and len(new_portfolio) < max_positions:

            allocation = initial_capital * (0.05 + confidence/100 * 0.10)
            qty = int(allocation / price)

            if qty > 0:
                new_entry = pd.DataFrame([{
                    "Stock": stock,
                    "Buy Price": price,
                    "Quantity": qty,
                    "Buy Date": datetime.today().strftime('%Y-%m-%d')
                }])

                new_portfolio = pd.concat([new_portfolio, new_entry], ignore_index=True)
                print(f"BUY: {stock}")

    # ---------------- EXIT ----------------
    elif signal == "EXIT":
        if stock in holding_stocks:

            row_data = portfolio[portfolio["Stock"] == stock].iloc[0]

            buy_price = row_data["Buy Price"]
            qty = row_data["Quantity"]

            pnl = (price - buy_price) * qty
            pnl_pct = ((price - buy_price) / buy_price) * 100

            trade = pd.DataFrame([{
                "Stock": stock,
                "Buy Price": buy_price,
                "Sell Price": price,
                "Quantity": qty,
                "Buy Date": row_data["Buy Date"],
                "Sell Date": datetime.today().strftime('%Y-%m-%d'),
                "PnL": pnl,
                "PnL %": pnl_pct
            }])

            new_trades = pd.concat([new_trades, trade], ignore_index=True)
            new_portfolio = new_portfolio[new_portfolio["Stock"] != stock]

            print(f"EXIT: {stock} | PnL: {pnl:.2f}")

# Save files
new_portfolio.to_csv("data/portfolio.csv", index=False)
new_trades.to_csv("dta/trades.csv", index=False)

print("Portfolio & Trades updated")
