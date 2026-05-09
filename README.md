# 🎯 Swing Trading Backtest - NIFTY 50

A complete **Python-based swing trading backtesting framework** for NIFTY 50 stocks with automated signal generation, portfolio management, and performance analysis.

## 📋 Overview

This framework implements a **Momentum Mean Reversion Swing Trading Strategy** that:
- Holds exactly **5 stocks** from NIFTY 50
- Generates automated **Buy/Sell signals** based on technical indicators
- Manages positions with **profit targets** and **stop losses**
- Calculates comprehensive **performance metrics** (Sharpe Ratio, Sortino, Max Drawdown, CAGR, Win Rate)
- Generates **professional visualizations** and reports

## 🎯 Strategy Rules

### Buy Signals (ALL must be true):
1. **RSI(14) < 35** - Oversold condition
2. **Price > 50-day MA** - Above long-term trend
3. **Volume > 20-day Average** - High volume confirmation
4. **MACD Histogram > 0** - Positive momentum

### Sell Signals (ANY one):
1. **RSI > 70** - Overbought condition
2. **+5% Profit Target** - Take profit
3. **-2% Stop Loss** - Cut losses
4. **15 Days Holding** - Time-based exit

## 📁 Project Structure

```
swing-trading-strategy/
├── main.py                      # 🚀 RUN THIS FILE
├── config.py                    # ⚙️  Strategy parameters
├── requirements.txt             # 📦 Dependencies
├── README.md                    # 📖 This file
│
├── data/
│   ├── fetch_data.py           # 📥 Download NIFTY 50 data
│   └── cache/                  # 💾 Cached data
│
├── strategy/
│   ├── indicators.py           # 📊 Technical indicators (RSI, MACD, MA, BB)
│   └── signal_generator.py     # 🎯 Buy/Sell signal generation
│
├── backtester/
│   ├── backtest.py             # 🔄 Main backtesting engine
│   ├── portfolio.py            # 💼 Position management
│   ├── metrics.py              # 📈 Performance calculations
│   └── visualizer.py           # 📉 Charts & visualizations
│
└── results/                     # 📊 Output files
    ├── equity_curve.csv        # Daily portfolio values
    ├── trades.csv              # All trades
    ├── metrics.json            # Performance metrics
    ├── equity_curve.png        # Portfolio growth chart
    ├── drawdown.png            # Drawdown analysis
    ├── trade_analysis.png      # Trade statistics
    └── metrics_summary.png     # Performance summary
```

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Backtest
```bash
python main.py
```

### 3. View Results
- **Terminal Output**: Performance metrics displayed
- **CSV Files**: `results/equity_curve.csv` and `results/trades.csv`
- **Charts**: 4 PNG files with visualizations

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Strategy Parameters
RSI_OVERSOLD = 35              # Buy signal threshold
PROFIT_TARGET = 0.05           # 5% profit target
STOP_LOSS = 0.02               # 2% stop loss
MAX_HOLD_DAYS = 15             # 15 days max hold

# Portfolio Management
INITIAL_CAPITAL = 1000000      # ₹10 lakhs
MAX_POSITIONS = 5              # Hold 5 stocks
POSITION_SIZE_PERCENT = 0.18   # 18% per stock

# Data
DATA_START_DATE = '2022-01-01'
DATA_END_DATE = '2026-05-09'
```

## 📊 Performance Metrics Explained

| Metric | Interpretation |
|--------|-----------------|
| **CAGR** | Compound Annual Growth Rate (should be > 15%) |
| **Sharpe Ratio** | Risk-adjusted returns (> 1.0 is good) |
| **Sortino Ratio** | Downside risk measure (> 1.0 is good) |
| **Max Drawdown** | Largest decline from peak (should be < 25%) |
| **Win Rate** | % of profitable trades (> 50% is good) |
| **Profit Factor** | Total wins / Total losses (> 1.5 is good) |

## 📈 Sample Output

```
======================================================
🎯 SWING TRADING BACKTEST - NIFTY 50
======================================================

💰 Capital & Returns:
   Initial Capital: ₹1,000,000
   Final Equity: ₹1,287,500
   Total Return: +28.75%
   CAGR: 22.3%

📈 Risk-Adjusted Returns:
   Sharpe Ratio: 1.45 (Good)
   Sortino Ratio: 1.82
   Max Drawdown: -12.5%

🎯 Trading Performance:
   Total Trades: 48
   Win Rate: 58.3%
   Profit Factor: 2.15
   Avg Trade Return: +1.85%
```

## ⚠️ IMPORTANT DISCLAIMERS

### ❌ What This Is NOT:
- **NOT financial advice** - Consult a SEBI-registered advisor
- **NOT a guarantee** - Past performance ≠ future results
- **NOT perfect** - Backtests have limitations:
  - Doesn't account for gaps, slippage, taxes
  - Market conditions change
  - News events can break strategies
  - Survivorship bias in NIFTY 50 constituents

### ✅ What To Do Before Trading:
1. **Paper trade** - Test with virtual money first
2. **Analyze backtest results** - Understand the metrics
3. **Consult professional advisors** - Get expert guidance
4. **Risk management** - Position sizing and stop losses are MANDATORY
5. **Start small** - Risk only 1-2% of capital initially

## 🔄 Next Steps

### To Improve the Strategy:
1. Add **more indicators** (Bollinger Bands, Stochastic, ADX)
2. Implement **machine learning** for signal optimization
3. Add **live trading** automation
4. Scale to **NIFTY 100, 200, 500**
5. Implement **portfolio optimization** (Markowitz)

### To Add Features:
1. **Real-time alerts** - SMS/Email notifications
2. **Paper trading** - Live signal generation
3. **Parameter optimization** - Find best RSI, profit target, etc.
4. **Multi-timeframe** - Combine daily + weekly signals
5. **Risk parity** - Dynamic position sizing

## 📚 Resources

- **Backtesting**: https://en.wikipedia.org/wiki/Backtesting
- **Technical Analysis**: https://www.investopedia.com/technical-analysis-4689657
- **Sharpe Ratio**: https://en.wikipedia.org/wiki/Sharpe_ratio
- **NSE Data**: https://www.nseindia.com/

## 💡 Tips for Success

1. **Don't over-optimize** - Avoid curve-fitting to historical data
2. **Test different periods** - Run backtest on various date ranges
3. **Track all trades** - Maintain detailed trade logs
4. **Review regularly** - Update strategy based on market changes
5. **Risk management** - Never risk more than 1-2% per trade

## 📞 Support

- Check `results/` folder for detailed outputs
- Review individual trade logs in `trades.csv`
- Analyze metrics in `metrics.json`
- Inspect visualizations in PNG files

---

**Happy Trading! 🚀** 

Remember: *"In the world of swing trading, the best strategy is the one you understand completely and can execute consistently."*

⚖️ **Risk Disclaimer**: Trading stocks involves substantial risk of loss. This framework is for educational purposes only. Always consult financial professionals before trading real capital.
