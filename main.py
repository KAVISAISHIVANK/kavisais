import pandas as pd
from datetime import datetime

signals_data = []

for stock in stocks:
    df = yf.download(stock, period="6mo", interval="1d")

    if len(df) < 50:
        continue

    signal = get_signal(df)

    if signal:
        price = df['Close'].iloc[-1]

        signals_data.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Stock": stock,
            "Signal": signal,
            "Price": round(price, 2)
        })

        msg = f"{signal}: {stock} @ {price}"
        send_alert(msg)

# Save to CSV
if signals_data:
    df_signals = pd.DataFrame(signals_data)

    try:
        old = pd.read_csv("signals.csv")
        df_signals = pd.concat([old, df_signals])
    except:
        pass

    df_signals.to_csv("signals.csv", index=False)
