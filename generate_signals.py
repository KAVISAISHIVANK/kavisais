import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD

stocks = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"]

data_list = []

for stock in stocks:
    df = yf.download(stock, period="6mo", interval="1d")

    if df.empty:
        continue

    df["RSI"] = RSIIndicator(df["Close"]).rsi()
    macd = MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    latest = df.iloc[-1]

    signal = "HOLD"
    confidence = 50

    # BUY condition
    if latest["RSI"] < 35 and latest["MACD"] > latest["MACD_signal"]:
        signal = "BUY"
        confidence = 70

    # EXIT condition
    elif latest["RSI"] > 65 and latest["MACD"] < latest["MACD_signal"]:
        signal = "EXIT"
        confidence = 70

    data_list.append({
        "Stock": stock,
        "Signal": signal,
        "Price": latest["Close"],
        "Confidence": confidence
    })

signals_df = pd.DataFrame(data_list)
signals_df.to_csv("signals.csv", index=False)

print("signals.csv updated")
