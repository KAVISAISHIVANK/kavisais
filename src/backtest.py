import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

stocks = [
    "RELIANCE.NS","ICICIBANK.NS","HDFCBANK.NS","INFY.NS","TCS.NS"
]

initial_capital = 500000
capital = initial_capital

trades = []

for stock in stocks:
    print(f"Backtesting {stock}")

    df = yf.download(stock, period="2y", interval="1d", progress=False)

    if df.empty:
        continue

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns or len(df) < 50:
        continue

    # Fix Close
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.astype(float)

    # Indicators
    df["RSI"] = RSIIndicator(close).rsi()
    macd = MACD(close)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    position = None

    for i in range(50, len(df)):
        row = df.iloc[i]

        price = float(close.iloc[i])

        # BUY
        if position is None:
            if row["RSI"] < 35 and row["MACD"] > row["MACD_signal"]:
                qty = int((capital * 0.1) / price)

                if qty > 0:
                    position = {
                        "buy_price": price,
                        "qty": qty
                    }

        # EXIT
        elif position is not None:
            buy_price = position["buy_price"]

            change_pct = (price - buy_price) / buy_price * 100

            if (
                row["RSI"] > 65 and row["MACD"] < row["MACD_signal"]
                or change_pct >= 12
                or change_pct <= -5
            ):
                pnl = (price - buy_price) * position["qty"]
                capital += pnl

                trades.append({
                    "Stock": stock,
                    "Buy": buy_price,
                    "Sell": price,
                    "PnL": pnl,
                    "Return %": change_pct
                })

                position = None

# =========================
# RESULTS
# =========================

trades_df = pd.DataFrame(trades)

if trades_df.empty:
    print("No trades in backtest")
else:
    total_trades = len(trades_df)
    wins = len(trades_df[trades_df["PnL"] > 0])
    win_rate = (wins / total_trades) * 100

    total_pnl = trades_df["PnL"].sum()

    print("\n===== BACKTEST RESULTS =====")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total PnL: ₹{total_pnl:.2f}")
    print(f"Final Capital: ₹{capital:.2f}")

    trades_df.to_csv("data/backtest_results.csv", index=False)
