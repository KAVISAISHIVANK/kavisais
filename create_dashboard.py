import pandas as pd

try:
    trades = pd.read_csv("trades.csv")
except:
    print("No trades yet")
    exit()

total_trades = len(trades)
wins = len(trades[trades["PnL"] > 0])
losses = len(trades[trades["PnL"] <= 0])

win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
total_pnl = trades["PnL"].sum()
avg_return = trades["PnL %"].mean()

summary = pd.DataFrame({
    "Metric": ["Total Trades","Wins","Losses","Win Rate","Total PnL","Avg Return %"],
    "Value": [total_trades,wins,losses,win_rate,total_pnl,avg_return]
})

with pd.ExcelWriter("summary.xlsx") as writer:
    trades.to_excel(writer, sheet_name="Trades", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)

print("summary.xlsx created")
