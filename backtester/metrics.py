"""
Performance Metrics - Calculate risk-adjusted returns
"""

import numpy as np
import pandas as pd
from datetime import datetime

def calculate_cagr(initial_value, final_value, years):
    """Calculate Compound Annual Growth Rate"""
    if initial_value <= 0:
        return 0
    
    cagr = (final_value / initial_value) ** (1 / years) - 1
    return cagr * 100

def calculate_sharpe_ratio(returns, risk_free_rate=0.06):
    """Calculate Sharpe Ratio (annualized)"""
    if len(returns) == 0:
        return 0
    
    excess_returns = returns - (risk_free_rate / 252)
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    return sharpe

def calculate_sortino_ratio(returns, target_return=0, risk_free_rate=0.06):
    """Calculate Sortino Ratio (downside risk)"""
    if len(returns) == 0:
        return 0
    
    excess_returns = returns - (risk_free_rate / 252)
    downside_returns = excess_returns[excess_returns < target_return]
    
    downside_deviation = downside_returns.std() * np.sqrt(252)
    
    if downside_deviation == 0:
        return 0
    
    sortino = excess_returns.mean() * 252 / downside_deviation
    
    return sortino

def calculate_max_drawdown(equity_curve):
    """Calculate Maximum Drawdown"""
    if len(equity_curve) == 0:
        return 0
    
    cumulative_max = equity_curve.expanding().max()
    drawdown = (equity_curve - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()
    
    return max_drawdown * 100

def calculate_win_rate(trades):
    """Calculate percentage of winning trades"""
    if len(trades) == 0:
        return 0
    
    winning_trades = len([t for t in trades if t['net_pnl'] > 0])
    win_rate = (winning_trades / len(trades)) * 100
    
    return win_rate

def calculate_profit_factor(trades):
    """Calculate Profit Factor (wins / losses)"""
    if len(trades) == 0:
        return 0
    
    wins = sum([t['net_pnl'] for t in trades if t['net_pnl'] > 0])
    losses = abs(sum([t['net_pnl'] for t in trades if t['net_pnl'] < 0]))
    
    if losses == 0:
        return 0 if wins == 0 else wins
    
    profit_factor = wins / losses
    
    return profit_factor

def calculate_all_metrics(equity_df, trades, initial_capital, years=4):
    """Calculate all performance metrics"""
    
    equity_values = equity_df['equity'].values if 'equity' in equity_df.columns else equity_df.values
    equity_values = pd.Series(equity_values)
    
    final_value = equity_values.iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital * 100
    cagr = calculate_cagr(initial_capital, final_value, years)
    
    # Calculate daily returns
    daily_returns = equity_values.pct_change().dropna()
    sharpe = calculate_sharpe_ratio(daily_returns)
    sortino = calculate_sortino_ratio(daily_returns)
    max_dd = calculate_max_drawdown(equity_values)
    
    # Trade statistics
    win_rate = calculate_win_rate(trades)
    profit_factor = calculate_profit_factor(trades)
    
    metrics = {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return_pct': total_return,
        'cagr_pct': cagr,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown_pct': max_dd,
        'total_trades': len(trades),
        'winning_trades': len([t for t in trades if t['net_pnl'] > 0]),
        'losing_trades': len([t for t in trades if t['net_pnl'] < 0]),
        'win_rate_pct': win_rate,
        'profit_factor': profit_factor,
        'avg_trade_return_pct': np.mean([t['return_pct'] for t in trades]) if trades else 0
    }
    
    return metrics

def format_metrics(metrics):
    """Format metrics for display"""
    output = "\n" + "="*70
    output += "\n💰 CAPITAL & RETURNS:\n"
    output += f"   Initial Capital: ₹{metrics['initial_capital']:,.0f}\n"
    output += f"   Final Value: ₹{metrics['final_value']:,.0f}\n"
    output += f"   Total Return: {metrics['total_return_pct']:+.2f}%\n"
    output += f"   CAGR: {metrics['cagr_pct']:+.2f}%\n"
    
    output += "\n📈 RISK-ADJUSTED RETURNS:\n"
    output += f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n"
    output += f"   Sortino Ratio: {metrics['sortino_ratio']:.2f}\n"
    output += f"   Max Drawdown: {metrics['max_drawdown_pct']:.2f}%\n"
    
    output += "\n🎯 TRADING PERFORMANCE:\n"
    output += f"   Total Trades: {metrics['total_trades']}\n"
    output += f"   Winning Trades: {metrics['winning_trades']}\n"
    output += f"   Losing Trades: {metrics['losing_trades']}\n"
    output += f"   Win Rate: {metrics['win_rate_pct']:.2f}%\n"
    output += f"   Profit Factor: {metrics['profit_factor']:.2f}x\n"
    output += f"   Avg Trade Return: {metrics['avg_trade_return_pct']:+.2f}%\n"
    output += "="*70 + "\n"
    
    return output
