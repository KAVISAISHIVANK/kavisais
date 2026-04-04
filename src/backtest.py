import pandas as pd
import numpy as np
import os

# --- CONFIG ---
STOCKS_DIR = 'stocks'
OUTPUT_DIR = 'data'
START_DATE = '2000-01-01'
END_DATE = '2025-01-01'
INITIAL_CAPITAL = 1_000_000
MAX_HOLDINGS = 10
MOMENTUM_LOOKBACK_DAYS = 20
PROFIT_TARGET_PERCENT = 0.07   # 7% profit
STOP_LOSS_PERCENT = 0.05       # 5% loss
BROKERAGE_PER_TRADE = 20.0
STT_BUY = 0.001
STT_SELL = 0.001

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- NIFTY50 tickers ---
NIFTY50_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "BHARTIARTL.NS", "ITC.NS", "LT.NS", "SBIN.NS", "HINDUNILVR.NS",
    "BAJFINANCE.NS", "KOTAKBANK.NS", "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "NESTLEIND.NS", "ASIANPAINT.NS", "ULTRACEMCO.NS", "TITAN.NS", "M&M.NS",
    "TECHM.NS", "INDUSINDBK.NS", "NTPC.NS", "TATAMOTORS.NS", "JSWSTEEL.NS",
    "GRASIM.NS", "ADANIENT.NS", "POWERGRID.NS", "ONGC.NS", "CIPLA.NS",
    "DRREDDY.NS", "HDFC.NS", "WIPRO.NS", "COALINDIA.NS", "BPCL.NS",
    "GAIL.NS", "HEROMOTOCO.NS", "SHREECEM.NS", "UPL.NS", "DIVISLAB.NS",
    "APOLLOHOSP.NS", "EICHERMOT.NS", "DMART.NS", "LTIM.NS", "SIEMENS.NS",
    "PIDILITIND.NS", "HDFCLIFE.NS", "SBILIFE.NS", "GODREJCP.NS", "DABUR.NS"
]

# --- Load stock data ---
all_stock_data = {}
for ticker in NIFTY50_TICKERS:
    file_path = os.path.join(STOCKS_DIR, f"{ticker}.csv")
    if not os.path.exists(file_path):
        continue
    try:
        df = pd.read_csv(file_path, skiprows=[1,2])
        df['Price'] = pd.to_datetime(df['Price'])
        df.set_index('Price', inplace=True)
        df.sort_index(inplace=True)
        df['PriceToUse'] = df['Close']
        df['Momentum'] = df['PriceToUse'].pct_change(periods=MOMENTUM_LOOKBACK_DAYS)
        all_stock_data[ticker] = df
    except Exception as e:
        print(f"Error loading {ticker}: {e}")

if not all_stock_data:
    raise ValueError("No stock data loaded. Check CSV files in 'stocks/'.")

# --- Backtest Initialization ---
portfolio = {'capital': INITIAL_CAPITAL, 'holdings': {}}
trade_log = []
daily_capital_history = []

# --- Trading Dates ---
min_date = max(df.index.min() for df in all_stock_data.values())
max_date = min(df.index.max() for df in all_stock_data.values())
trading_dates = pd.date_range(start=max(min_date, pd.to_datetime(START_DATE)),
                              end=min(max_date, pd.to_datetime(END_DATE)),
                              freq='B')

def get_day_data(df_stock, date):
    if date in df_stock.index:
        return df_stock.loc[date]
    idx = df_stock.index.searchsorted(date)
    if idx < len(df_stock.index):
        next_date = df_stock.index[idx]
        if (next_date - date).days <= 5:
            return df_stock.loc[next_date]
    return None

# --- Backtest Loop ---
for current_date in trading_dates:
    # Daily portfolio value
    daily_value = portfolio['capital']
    for t, h in portfolio['holdings'].items():
        df_t = all_stock_data[t]
        day_data = get_day_data(df_t, current_date)
        if day_data is not None:
            daily_value += h['qty'] * day_data['PriceToUse']
    daily_capital_history.append({'date': current_date, 'capital': daily_value})

    # Check existing holdings for Profit/Loss
    for t, h in list(portfolio['holdings'].items()):
        df_t = all_stock_data[t]
        day_data = get_day_data(df_t, current_date)
        if day_data is None: continue
        price = day_data['PriceToUse']
        buy_price = h['buy_price']
        sell_reason = None
        if price >= buy_price * (1+PROFIT_TARGET_PERCENT):
            sell_reason = 'PROFIT'
        elif price <= buy_price * (1-STOP_LOSS_PERCENT):
            sell_reason = 'LOSS'
        if sell_reason:
            qty = h['qty']
            gross = qty*price
            total_costs = BROKERAGE_PER_TRADE + gross*STT_SELL
            net = gross - total_costs
            portfolio['capital'] += net
            trade_log.append({'date': current_date, 'type': f'SELL_{sell_reason}', 'ticker': t,
                              'qty': qty, 'buy_price': buy_price, 'sell_price': price,
                              'capital_after_trade': portfolio['capital']})
            del portfolio['holdings'][t]

    # Weekly rebalance (Monday)
    if current_date.weekday() == 0:
        momentum_scores = []
        for t, df_t in all_stock_data.items():
            day_data = get_day_data(df_t, current_date)
            if day_data is not None and pd.notna(day_data['Momentum']):
                momentum_scores.append({'ticker': t, 'momentum': day_data['Momentum']})
        momentum_scores.sort(key=lambda x: x['momentum'], reverse=True)
        top_tickers = [x['ticker'] for x in momentum_scores[:MAX_HOLDINGS]]

        # Buy new positions if slots available
        slots = MAX_HOLDINGS - len(portfolio['holdings'])
        for t in top_tickers:
            if slots <= 0: break
            if t in portfolio['holdings']: continue
            df_t = all_stock_data[t]
            day_data = get_day_data(df_t, current_date)
            if day_data is None: continue
            price = day_data['PriceToUse']
            allocation = portfolio['capital'] / slots
            qty = int(allocation / price)
            if qty == 0: continue
            gross = qty*price
            total_costs = BROKERAGE_PER_TRADE + gross*STT_BUY
            net = gross + total_costs
            if portfolio['capital'] >= net:
                portfolio['capital'] -= net
                portfolio['holdings'][t] = {'qty': qty, 'buy_price': price}
                trade_log.append({'date': current_date, 'type':'BUY', 'ticker': t,
                                  'qty': qty, 'buy_price': price,
                                  'capital_after_trade': portfolio['capital']})
                slots -= 1

# --- Final liquidation ---
for t, h in portfolio['holdings'].items():
    df_t = all_stock_data[t]
    last_day = df_t.index.max()
    price = df_t.loc[last_day]['PriceToUse']
    qty = h['qty']
    gross = qty*price
    total_costs = BROKERAGE_PER_TRADE + gross*STT_SELL
    net = gross - total_costs
    portfolio['capital'] += net
    trade_log.append({'date': last_day, 'type':'FINAL_SELL', 'ticker': t,
                      'qty': qty, 'buy_price': h['buy_price'], 'sell_price': price,
                      'capital_after_trade': portfolio['capital']})

# --- Save results ---
trade_log_df = pd.DataFrame(trade_log)
trade_log_df.to_csv(os.path.join(OUTPUT_DIR, 'nifty50_trade_log.csv'), index=False)

daily_capital_df = pd.DataFrame(daily_capital_history)
daily_capital_df.set_index('date', inplace=True)
daily_capital_df.to_csv(os.path.join(OUTPUT_DIR, 'nifty50_equity_curve.csv'))

print("Backtest complete. Results saved in 'data/' folder:")
print(" - nifty50_trade_log.csv")
print(" - nifty50_equity_curve.csv")
# Save trade log as expected by the pipeline
trade_log_df.to_csv(os.path.join(OUTPUT_DIR, 'backtest_results.csv'), index=False)
