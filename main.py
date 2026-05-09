"""
Main Entry Point - Execute the complete swing trading backtest
"""

import os
import sys

# Create required directories
os.makedirs('results', exist_ok=True)
os.makedirs('data/cache', exist_ok=True)
os.makedirs('strategy', exist_ok=True)
os.makedirs('backtester', exist_ok=True)

# Import and run backtest
from backtester.backtest import run_backtest

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🚀 SWING TRADING BACKTEST - NIFTY 50 STRATEGY 🚀")
    print("="*70)
    print("\n📊 Momentum Mean Reversion Strategy")
    print("   • Hold 5 NIFTY 50 stocks")
    print("   • Entry: RSI <35, Price >MA50, Volume, MACD>0")
    print("   • Exit: +5% profit, -2% loss, 15 days hold")
    print("   • Initial Capital: ₹10,00,000")
    print("\n" + "="*70)
    
    try:
        # Run the backtest
        results = run_backtest()
        
        if results:
            print("\n" + "="*70)
            print(" ✅ BACKTEST COMPLETED SUCCESSFULLY!")
            print("="*70)
            print("\n📁 Results saved in 'results/' folder:")
            print("   📊 equity_curve.csv - Daily portfolio values")
            print("   📄 trades.csv - Individual trade details")
            print("   📋 metrics.json - Performance metrics")
            print("\n💡 Next Steps:")
            print("   1. Review the CSV files for detailed analysis")
            print("   2. Adjust config.py parameters if needed")
            print("   3. Run again to test new settings")
            print("   4. Paper trade before using real capital")
            print("\n⚠️  IMPORTANT:")
            print("   • Past performance ≠ Future results")
            print("   • Consult SEBI-registered advisor")
            print("   • Test thoroughly before trading real money")
            print("="*70 + "\n")
        else:
            print("\n❌ Backtest failed! Check errors above.\n")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
