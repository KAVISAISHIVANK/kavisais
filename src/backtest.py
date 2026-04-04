import os
import pandas as pd

# =========================
# PARAMETERS
# =========================
STOCK_DIR = 'stocks'           # folder where CSVs are stored
MOMENTUM_LOOKBACK_DAYS = 5     # number of days for momentum
INITIAL_CAPITAL = 500000       # starting capital (₹5L)
MAX_STOCKS = 5                 # max positions at a time

# =========================
# HELPER FUNCTION TO LOAD CSV
# =========================
def load_stock_csv(file_path):
    """
    Load stock CSV with multi-header format:
    Row1: Column names (Price, Close, High, Low, Open, Volume)
    Row2: Ticker (ignore)
    Row3: extra (ignore)
    Data starts from row 4
    """
    df = pd.read_csv(
        file_path,
        skiprows=[1, 2],  # skip Ticker row and extra
        index_col=0,       # 'Price' column = date
        parse_dates=True
    )

    # keep only required columns
    df = df.rename(columns=lambda x: x.strip())
    df = df[['Close', 'High', 'Low', 'Open', 'Volume']]

    # Add PriceToUse for backtest (use Close)
    df['PriceToUse'] = df['Close']

    # Drop any NaNs
    df.dropna(subset=['PriceToUse'], inplace=True)

    # Sort by date
    df = df.sort_index()

    # Momentum
    df['Momentum'] = df['PriceToUse'].pct_change(periods=MOMENTUM_LOOKBACK_DAYS)
    
    return df

# =========================
# BACKTEST LOGIC
# =========================
def backtest_nifty50():
    capital = INITIAL_CAPITAL
    positions = {}   # current positions {ticker: {'qty': int, 'entry_price': float}}
    history = []     # store trades for review

    # load all CSV files
    stock_files = [f for f in os.listdir(STOCK_DIR) if f.endswith('.CSV')]

    for file in stock_files:
        ticker = file.replace('.CSV','')
        file_path = os.path.join(STOCK_DIR, file)
        try:
            df = load_stock_csv(file_path)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

        for date, row in df.iterrows():
            price = row['PriceToUse']

            # --- SELL LOGIC ---
            if ticker in positions:
                entry_price = positions[ticker]['entry_price']
                target_price = entry_price * 1.12   # 12% profit target
                stop_loss = entry_price * 0.95      # 5% stop loss

                if price >= target_price or price <= stop_loss:
                    qty = positions[ticker]['qty']
                    pnl = (price - entry_price) * qty
                    capital += price * qty
                    history.append({
                        'Date': date,
                        'Ticker': ticker,
                        'Action': 'SELL',
                        'Price': price,
                        'Qty': qty,
                        'P&L': pnl,
                        'Capital': capital
                    })
                    del positions[ticker]

            # --- BUY LOGIC ---
            if len(positions) < MAX_STOCKS:
                # simple momentum entry: positive MOMENTUM
                if row['Momentum'] > 0:
                    alloc_per_stock = capital / (MAX_STOCKS - len(positions))
                    qty_to_buy = int(alloc_per_stock / price)
                    if qty_to_buy > 0:
                        positions[ticker] = {'qty': qty_to_buy, 'entry_price': price}
                        capital -= price * qty_to_buy
                        history.append({
                            'Date': date,
                            'Ticker': ticker,
                            'Action': 'BUY',
                            'Price': price,
                            'Qty': qty_to_buy,
                            'P&L': 0,
                            'Capital': capital
                        })

    # --- FINAL POSITIONS VALUE ---
    for ticker, pos in positions.items():
        df = load_stock_csv(os.path.join(STOCK_DIR, ticker + '.CSV'))
        last_price = df['PriceToUse'][-1]
        capital += last_price * pos['qty']
        history.append({
            'Date': df.index[-1],
            'Ticker': ticker,
            'Action': 'FINAL SELL',
            'Price': last_price,
            'Qty': pos['qty'],
            'P&L': (last_price - pos['entry_price']) * pos['qty'],
            'Capital': capital
        })

    # --- OUTPUT RESULTS ---
    result_df = pd.DataFrame(history)
    result_df.to_csv('nifty50_backtest_history.csv', index=False)
    print(f"Backtest completed. Final capital: ₹{capital:,.2f}")
    print("Trade history saved to nifty50_backtest_history.csv")

# =========================
# RUN BACKTEST
# =========================
if __name__ == "__main__":
    backtest_nifty50()
