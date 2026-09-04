# 📊 Backtesting Guide - Nifty First Candle ORB Strategy

## Table of Contents
1. [Overview](#overview)
2. [Data Requirements](#data-requirements)
3. [Backtesting Methods](#backtesting-methods)
4. [Creating a Backtest Script](#creating-a-backtest-script)
5. [Metrics to Track](#metrics-to-track)
6. [Optimization Parameters](#optimization-parameters)
7. [Validation](#validation)

---

## Overview

Backtesting validates your strategy against historical data before risking real capital. For this ORB strategy, you need:

- **Historical Data:** Nifty 1-minute OHLC data
- **Option Pricing:** Historical option premiums or pricing model
- **Transaction Costs:** Brokerage, taxes, slippage
- **Market Hours:** 09:15-15:30 IST data only

---

## Data Requirements

### 1. Nifty Spot Data (Essential)
```
Date, Time, Open, High, Low, Close, Volume
2026-01-02, 09:15:00, 24500, 24520, 24480, 24515, 1500000
2026-01-02, 09:16:00, 24515, 24530, 24510, 24525, 1200000
...
```

**Sources:**
- **Free:** Yahoo Finance, NSE India website
- **Paid:** Zerodha Kite, Upstox, TrueData, Global Datafeeds
- **Python APIs:** `yfinance`, `nsepy`, broker APIs

### 2. Option Premium Data (Ideal)
```
Date, Time, Strike, Type, Premium, IV, Delta, Theta
2026-01-02, 09:17:00, 24500, CE, 120.50, 18.5, 0.52, -0.35
2026-01-02, 09:17:00, 24500, PE, 110.25, 19.2, -0.48, -0.32
```

**Sources:**
- Broker historical data
- Option chain archives
- Market data vendors

### 3. Alternative: Black-Scholes Model
If historical option data unavailable, estimate premiums using:
- Spot price
- Strike price
- Time to expiry
- Risk-free rate
- Implied volatility (from historical ATM IV)

---

## Backtesting Methods

### Method 1: Python Backtest Script (Recommended)

Create a dedicated backtesting version of your strategy.

#### Step 1: Create Backtest Script

```python
#!/usr/bin/env python3
"""
Nifty ORB Strategy - Backtesting Version
"""

import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time
import json

class NiftyORBBacktest:
    def __init__(self, config_path='nifty_orb_config.json'):
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Capital & Risk
        self.capital = config['capital_management']['starting_capital']
        self.risk_pct = config['capital_management']['risk_per_trade_pct']
        self.max_daily_loss_pct = config['capital_management']['max_daily_loss_pct']
        
        # ORB Parameters
        self.orb_threshold = config['orb_parameters']['orb_range_threshold']
        self.breakout_buffer = config['orb_parameters']['breakout_buffer']
        
        # TP & Trailing
        self.tp1_mult = config['tp_trailing']['tp1_multiplier']
        self.tp2_mult = config['tp_trailing']['tp2_multiplier']
        self.trailing_points = config['tp_trailing']['trailing_stop_points']
        
        # Trade limits
        self.max_trades_per_day = config['trade_limits']['max_trades_per_day']
        
        # Position sizing
        self.position_lots = config['position_sizing']['position_size_lots']
        self.tp1_exit_lots = config['position_sizing']['tp1_exit_lots']
        self.tp2_exit_lots = config['position_sizing']['tp2_exit_lots']
        self.lot_size = config['position_sizing']['lot_size']
        
        # Results tracking
        self.trades = []
        self.daily_pnl = {}
        self.equity_curve = []
        
    def load_data(self, csv_path):
        """Load historical Nifty data"""
        df = pd.read_csv(csv_path, parse_dates=['datetime'])
        df = df.set_index('datetime')
        
        # Filter for market hours only
        df = df.between_time('09:15:00', '15:30:00')
        
        return df
    
    def calculate_orb(self, day_data):
        """Calculate Opening Range Breakout levels"""
        # First candle (09:15-09:16)
        first_candle = day_data.iloc[0]
        
        orb_high = first_candle['high']
        orb_low = first_candle['low']
        orb_range = orb_high - orb_low
        
        return {
            'orb_high': orb_high,
            'orb_low': orb_low,
            'orb_range': orb_range,
            'orb_open': first_candle['open'],
            'orb_close': first_candle['close']
        }
    
    def simulate_option_premium(self, spot, strike, option_type, time_to_expiry_days):
        """Simplified option premium calculation"""
        # This is a simplified model - use Black-Scholes for accuracy
        
        moneyness = abs(spot - strike) / strike * 100
        time_value = 10 * (time_to_expiry_days / 30)  # Rough estimate
        
        if option_type == 'CE':
            intrinsic = max(0, spot - strike)
        else:  # PE
            intrinsic = max(0, strike - spot)
        
        premium = intrinsic + time_value - (moneyness * 0.5)
        return max(premium, 5)  # Minimum premium
    
    def backtest(self, data_path, start_date=None, end_date=None):
        """Run backtest on historical data"""
        print("=" * 70)
        print("STARTING BACKTEST")
        print("=" * 70)
        
        # Load data
        df = self.load_data(data_path)
        
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        # Group by date
        dates = df.index.date
        unique_dates = sorted(set(dates))
        
        print(f"Backtesting {len(unique_dates)} trading days")
        print(f"From: {unique_dates[0]} To: {unique_dates[-1]}")
        print("=" * 70)
        
        for date in unique_dates:
            day_data = df[df.index.date == date]
            
            if len(day_data) < 2:
                continue  # Not enough data
            
            self.simulate_day(day_data, date)
        
        # Generate results
        self.generate_results()
    
    def simulate_day(self, day_data, date):
        """Simulate trading for one day"""
        # Calculate ORB
        orb = self.calculate_orb(day_data)
        
        # Check if we can trade today (risk limits)
        daily_loss = self.daily_pnl.get(date, 0)
        max_daily_loss = self.capital * (self.max_daily_loss_pct / 100)
        
        if abs(daily_loss) >= max_daily_loss:
            return  # Daily loss limit hit
        
        trades_today = sum(1 for t in self.trades if t['entry_date'] == date)
        if trades_today >= self.max_trades_per_day:
            return  # Max trades hit
        
        # Simulate rest of day (starting from 2nd candle)
        for i in range(1, len(day_data)):
            current_candle = day_data.iloc[i]
            current_price = current_candle['close']
            
            # Check for breakout
            call_trigger = orb['orb_high'] + self.breakout_buffer
            put_trigger = orb['orb_low'] - self.breakout_buffer
            
            direction = None
            if current_price >= call_trigger:
                direction = 'CALL'
            elif current_price <= put_trigger:
                direction = 'PUT'
            
            if direction:
                # Simulate trade
                trade_result = self.simulate_trade(
                    day_data.iloc[i:],
                    direction,
                    orb,
                    date,
                    current_candle.name
                )
                
                if trade_result:
                    self.trades.append(trade_result)
                    self.daily_pnl[date] = self.daily_pnl.get(date, 0) + trade_result['pnl']
                    
                    # Update capital
                    self.capital += trade_result['pnl']
                    self.equity_curve.append({
                        'date': date,
                        'capital': self.capital
                    })
                    
                    # Check if we hit trade limit
                    trades_today += 1
                    if trades_today >= self.max_trades_per_day:
                        break
    
    def simulate_trade(self, remaining_data, direction, orb, date, entry_time):
        """Simulate a single trade with multi-stage exits"""
        
        # ATM strike
        entry_price = remaining_data.iloc[0]['close']
        atm_strike = round(entry_price / 50) * 50
        
        # Estimate option premium at entry
        option_type = 'CE' if direction == 'CALL' else 'PE'
        option_entry = self.simulate_option_premium(entry_price, atm_strike, option_type, 5)
        
        # Stop loss
        if direction == 'CALL':
            sl_level = orb['orb_low']
            tp1_level = entry_price + (entry_price - sl_level) * self.tp1_mult
            tp2_level = entry_price + (entry_price - sl_level) * self.tp2_mult
        else:  # PUT
            sl_level = orb['orb_high']
            tp1_level = entry_price - (sl_level - entry_price) * self.tp1_mult
            tp2_level = entry_price - (sl_level - entry_price) * self.tp2_mult
        
        # Trade state
        remaining_lots = self.position_lots
        pnl = 0
        tp1_hit = False
        tp2_hit = False
        breakeven_active = False
        trailing_sl = sl_level
        highest_price = entry_price
        lowest_price = entry_price
        
        exit_reason = None
        exit_time = None
        
        # Simulate rest of day
        for i in range(1, len(remaining_data)):
            candle = remaining_data.iloc[i]
            current_price = candle['close']
            high = candle['high']
            low = candle['low']
            
            # Check TP1
            if not tp1_hit:
                if (direction == 'CALL' and high >= tp1_level) or \
                   (direction == 'PUT' and low <= tp1_level):
                    # Estimate option premium at TP1
                    option_exit = self.simulate_option_premium(current_price, atm_strike, option_type, 4)
                    exit_pnl = (option_exit - option_entry) * self.tp1_exit_lots * self.lot_size
                    pnl += exit_pnl
                    remaining_lots -= self.tp1_exit_lots
                    tp1_hit = True
                    breakeven_active = True
                    sl_level = entry_price  # Move to breakeven
            
            # Check TP2
            if tp1_hit and not tp2_hit:
                if (direction == 'CALL' and high >= tp2_level) or \
                   (direction == 'PUT' and low <= tp2_level):
                    option_exit = self.simulate_option_premium(current_price, atm_strike, option_type, 3)
                    exit_pnl = (option_exit - option_entry) * self.tp2_exit_lots * self.lot_size
                    pnl += exit_pnl
                    remaining_lots -= self.tp2_exit_lots
                    tp2_hit = True
                    trailing_sl = current_price - self.trailing_points if direction == 'CALL' else current_price + self.trailing_points
            
            # Update trailing stop
            if tp2_hit:
                if direction == 'CALL':
                    if high > highest_price:
                        highest_price = high
                        new_trailing = highest_price - self.trailing_points
                        if new_trailing > trailing_sl:
                            trailing_sl = new_trailing
                else:  # PUT
                    if low < lowest_price:
                        lowest_price = low
                        new_trailing = lowest_price + self.trailing_points
                        if new_trailing < trailing_sl:
                            trailing_sl = new_trailing
            
            # Check stop loss
            if (direction == 'CALL' and low <= sl_level) or \
               (direction == 'PUT' and high >= sl_level):
                option_exit = self.simulate_option_premium(current_price, atm_strike, option_type, 2)
                exit_pnl = (option_exit - option_entry) * remaining_lots * self.lot_size
                pnl += exit_pnl
                exit_reason = 'STOP_LOSS'
                exit_time = candle.name
                break
            
            # Check trailing stop
            if tp2_hit:
                if (direction == 'CALL' and low <= trailing_sl) or \
                   (direction == 'PUT' and high >= trailing_sl):
                    option_exit = self.simulate_option_premium(current_price, atm_strike, option_type, 1)
                    exit_pnl = (option_exit - option_entry) * remaining_lots * self.lot_size
                    pnl += exit_pnl
                    exit_reason = 'TRAILING_STOP'
                    exit_time = candle.name
                    break
        
        # If no exit triggered, close at EOD
        if exit_reason is None:
            option_exit = self.simulate_option_premium(
                remaining_data.iloc[-1]['close'], 
                atm_strike, 
                option_type, 
                0.5
            )
            exit_pnl = (option_exit - option_entry) * remaining_lots * self.lot_size
            pnl += exit_pnl
            exit_reason = 'EOD'
            exit_time = remaining_data.index[-1]
        
        # Subtract transaction costs (approx)
        transaction_cost = (self.position_lots * self.lot_size * 40)  # ₹40 per lot (brokerage + taxes)
        pnl -= transaction_cost
        
        return {
            'entry_date': date,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'orb_range': orb['orb_range'],
            'orb_high': orb['orb_high'],
            'orb_low': orb['orb_low'],
            'entry_price': entry_price,
            'strike': atm_strike,
            'option_entry': option_entry,
            'sl_level': orb['orb_low'] if direction == 'CALL' else orb['orb_high'],
            'tp1_hit': tp1_hit,
            'tp2_hit': tp2_hit,
            'exit_reason': exit_reason,
            'pnl': pnl,
            'pnl_pct': (pnl / self.capital) * 100
        }
    
    def generate_results(self):
        """Generate backtest results and metrics"""
        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        
        if not self.trades:
            print("No trades executed during backtest period")
            return
        
        df_trades = pd.DataFrame(self.trades)
        
        # Overall metrics
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = len(df_trades[df_trades['pnl'] <= 0])
        win_rate = (winning_trades / total_trades) * 100
        
        total_pnl = df_trades['pnl'].sum()
        avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
        
        largest_win = df_trades['pnl'].max()
        largest_loss = df_trades['pnl'].min()
        
        # Risk metrics
        profit_factor = abs(df_trades[df_trades['pnl'] > 0]['pnl'].sum() / 
                           df_trades[df_trades['pnl'] <= 0]['pnl'].sum()) if losing_trades > 0 else 0
        
        expectancy = df_trades['pnl'].mean()
        
        # Drawdown
        equity = pd.DataFrame(self.equity_curve)
        equity['peak'] = equity['capital'].cummax()
        equity['drawdown'] = equity['capital'] - equity['peak']
        equity['drawdown_pct'] = (equity['drawdown'] / equity['peak']) * 100
        max_drawdown = equity['drawdown_pct'].min()
        
        # Print results
        print(f"\n📊 Overall Performance")
        print(f"{'─' * 70}")
        print(f"Total Trades:        {total_trades}")
        print(f"Winning Trades:      {winning_trades} ({win_rate:.1f}%)")
        print(f"Losing Trades:       {losing_trades} ({100-win_rate:.1f}%)")
        print(f"\nTotal P&L:           ₹{total_pnl:,.2f}")
        print(f"Average Win:         ₹{avg_win:,.2f}")
        print(f"Average Loss:        ₹{avg_loss:,.2f}")
        print(f"Largest Win:         ₹{largest_win:,.2f}")
        print(f"Largest Loss:        ₹{largest_loss:,.2f}")
        print(f"\nProfit Factor:       {profit_factor:.2f}")
        print(f"Expectancy:          ₹{expectancy:,.2f}")
        print(f"Max Drawdown:        {max_drawdown:.2f}%")
        
        # ORB Range Analysis
        print(f"\n📊 ORB Range Analysis")
        print(f"{'─' * 70}")
        small_range = df_trades[df_trades['orb_range'] <= self.orb_threshold]
        large_range = df_trades[df_trades['orb_range'] > self.orb_threshold]
        
        if len(small_range) > 0:
            print(f"\n≤ {self.orb_threshold} Points:")
            print(f"  Trades: {len(small_range)}")
            print(f"  Win Rate: {(len(small_range[small_range['pnl'] > 0]) / len(small_range) * 100):.1f}%")
            print(f"  Avg P&L: ₹{small_range['pnl'].mean():,.2f}")
        
        if len(large_range) > 0:
            print(f"\n> {self.orb_threshold} Points:")
            print(f"  Trades: {len(large_range)}")
            print(f"  Win Rate: {(len(large_range[large_range['pnl'] > 0]) / len(large_range) * 100):.1f}%")
            print(f"  Avg P&L: ₹{large_range['pnl'].mean():,.2f}")
        
        # Direction Analysis
        print(f"\n📊 Direction Analysis")
        print(f"{'─' * 70}")
        call_trades = df_trades[df_trades['direction'] == 'CALL']
        put_trades = df_trades[df_trades['direction'] == 'PUT']
        
        if len(call_trades) > 0:
            print(f"\nCALL Trades:")
            print(f"  Count: {len(call_trades)}")
            print(f"  Win Rate: {(len(call_trades[call_trades['pnl'] > 0]) / len(call_trades) * 100):.1f}%")
            print(f"  Avg P&L: ₹{call_trades['pnl'].mean():,.2f}")
        
        if len(put_trades) > 0:
            print(f"\nPUT Trades:")
            print(f"  Count: {len(put_trades)}")
            print(f"  Win Rate: {(len(put_trades[put_trades['pnl'] > 0]) / len(put_trades) * 100):.1f}%")
            print(f"  Avg P&L: ₹{put_trades['pnl'].mean():,.2f}")
        
        # TP Analysis
        print(f"\n📊 Take Profit Analysis")
        print(f"{'─' * 70}")
        tp1_hit = len(df_trades[df_trades['tp1_hit']])
        tp2_hit = len(df_trades[df_trades['tp2_hit']])
        
        print(f"TP1 Hit Rate: {(tp1_hit / total_trades * 100):.1f}%")
        print(f"TP2 Hit Rate: {(tp2_hit / total_trades * 100):.1f}%")
        
        # Export results
        df_trades.to_csv('backtest_results.csv', index=False)
        equity.to_csv('equity_curve.csv', index=False)
        
        print(f"\n✅ Results exported to:")
        print(f"   - backtest_results.csv")
        print(f"   - equity_curve.csv")
        print("=" * 70)


# Example usage
if __name__ == "__main__":
    backtest = NiftyORBBacktest('nifty_orb_config.json')
    backtest.backtest(
        'nifty_1min_data.csv',
        start_date='2025-01-01',
        end_date='2025-12-31'
    )
```

Save this as: `nifty_orb_backtest.py`

---

### Method 2: Using OpenAlgo Analyzer Mode

Test with live market data but simulated capital:

1. **Enable Analyzer Mode:**
   ```bash
   # In OpenAlgo settings
   Settings → Analyzer Mode → Enable
   ```

2. **Set Virtual Capital:**
   ```
   Starting Capital: ₹1,00,000
   ```

3. **Run Strategy:**
   - Upload your strategy
   - Let it run during market hours
   - Monitor paper trades

4. **Track Results:**
   - View in OpenAlgo dashboard
   - Export trade logs
   - Analyze performance

---

### Method 3: Using Third-Party Tools

#### A. Backtrader
```python
import backtrader as bt

class NiftyORBStrategy(bt.Strategy):
    params = (
        ('breakout_buffer', 3),
        ('tp1_mult', 1.0),
        ('tp2_mult', 2.0),
    )
    
    def __init__(self):
        self.orb_high = None
        self.orb_low = None
        self.first_candle_done = False
    
    def next(self):
        # Your ORB logic here
        pass
```

#### B. QuantConnect
- Cloud-based backtesting
- Free tier available
- Python/C# support

#### C. TradingView Pine Script
- Visual backtesting
- Easy to prototype
- Limited to TradingView data

---

## Creating Data CSV

### Format Required:
```csv
datetime,open,high,low,close,volume
2026-01-02 09:15:00,24500.00,24520.00,24480.00,24515.00,1500000
2026-01-02 09:16:00,24515.00,24530.00,24510.00,24525.00,1200000
```

### Python Script to Download Data:

```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def download_nifty_data(start_date, end_date):
    """Download Nifty 1-minute data"""
    
    # Download (yfinance has limited intraday history)
    ticker = yf.Ticker("^NSEI")
    
    # For longer history, loop through days
    all_data = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        try:
            df = ticker.history(
                interval='1m',
                start=current_date.strftime('%Y-%m-%d'),
                end=next_date.strftime('%Y-%m-%d')
            )
            
            if not df.empty:
                all_data.append(df)
                print(f"Downloaded: {current_date.date()}")
        
        except Exception as e:
            print(f"Error on {current_date.date()}: {e}")
        
        current_date = next_date
    
    # Combine all data
    if all_data:
        full_data = pd.concat(all_data)
        full_data = full_data.reset_index()
        full_data.columns = [c.lower() for c in full_data.columns]
        full_data.to_csv('nifty_1min_data.csv', index=False)
        print(f"\n✅ Saved {len(full_data)} rows to nifty_1min_data.csv")
    else:
        print("No data downloaded")

# Example usage
start = datetime(2025, 1, 1)
end = datetime(2025, 12, 31)
download_nifty_data(start, end)
```

---

## Metrics to Track

### Essential Metrics
```python
metrics = {
    # Win/Loss
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0,
    'win_rate': 0.0,
    
    # P&L
    'total_pnl': 0.0,
    'avg_win': 0.0,
    'avg_loss': 0.0,
    'largest_win': 0.0,
    'largest_loss': 0.0,
    'expectancy': 0.0,
    
    # Risk
    'profit_factor': 0.0,
    'sharpe_ratio': 0.0,
    'sortino_ratio': 0.0,
    'max_drawdown': 0.0,
    'recovery_factor': 0.0,
    
    # Streaks
    'max_consecutive_wins': 0,
    'max_consecutive_losses': 0,
    'avg_trade_duration': 0,
    
    # TP Analysis
    'tp1_hit_rate': 0.0,
    'tp2_hit_rate': 0.0,
    'breakeven_exits': 0,
    'trailing_exits': 0,
    
    # By ORB Range
    'small_range_win_rate': 0.0,  # ≤30 points
    'large_range_win_rate': 0.0,  # >30 points
    
    # By Direction
    'call_win_rate': 0.0,
    'put_win_rate': 0.0,
}
```

---

## Optimization Parameters

### Parameters to Test:

```json
{
  "breakout_buffer": [2, 3, 5, 7, 10],
  "orb_threshold": [25, 30, 35, 40],
  "tp1_multiplier": [0.5, 1.0, 1.5],
  "tp2_multiplier": [1.5, 2.0, 2.5, 3.0],
  "trailing_stop": [10, 15, 20, 25],
  "position_lots": [1, 2, 3, 5],
  "risk_per_trade": [2, 3, 5, 7]
}
```

### Grid Search Example:

```python
from itertools import product

# Parameters to test
buffers = [2, 3, 5]
tp2_mults = [1.5, 2.0, 2.5]

results = []

for buffer, tp2 in product(buffers, tp2_mults):
    # Update config
    config['orb_parameters']['breakout_buffer'] = buffer
    config['tp_trailing']['tp2_multiplier'] = tp2
    
    # Run backtest
    backtest = NiftyORBBacktest(config)
    result = backtest.run()
    
    results.append({
        'buffer': buffer,
        'tp2': tp2,
        'total_pnl': result['total_pnl'],
        'win_rate': result['win_rate'],
        'profit_factor': result['profit_factor']
    })

# Find best combination
best = max(results, key=lambda x: x['total_pnl'])
print(f"Best: Buffer={best['buffer']}, TP2={best['tp2']}")
```

---

## Validation

### Walk-Forward Analysis

```python
# Split data into training and testing periods
train_data = data['2024-01-01':'2024-06-30']
test_data = data['2024-07-01':'2024-12-31']

# Optimize on training data
best_params = optimize(train_data)

# Test on out-of-sample data
results = backtest(test_data, best_params)

# Compare performance
if test_performance > (train_performance * 0.7):
    print("✅ Strategy validated")
else:
    print("❌ Overfitting detected")
```

### Monte Carlo Simulation

```python
import numpy as np

def monte_carlo(trades, n_simulations=1000):
    """Simulate random trade sequences"""
    
    results = []
    
    for _ in range(n_simulations):
        # Randomly shuffle trades
        shuffled = np.random.choice(trades, len(trades), replace=True)
        sim_pnl = shuffled.sum()
        results.append(sim_pnl)
    
    # Confidence intervals
    p5 = np.percentile(results, 5)
    p95 = np.percentile(results, 95)
    
    print(f"95% Confidence Interval: ₹{p5:,.0f} to ₹{p95:,.0f}")
```

---

## Quick Start Checklist

- [ ] Download historical Nifty 1-min data
- [ ] Create `nifty_orb_backtest.py`
- [ ] Update `nifty_orb_config.json` with test parameters
- [ ] Run backtest script
- [ ] Analyze results (CSV files)
- [ ] Test different parameter combinations
- [ ] Validate with walk-forward analysis
- [ ] Paper trade before going live

---

## Next Steps

1. **Start Simple:**
   - Run backtest with default parameters
   - Analyze results
   - Identify patterns

2. **Optimize:**
   - Test parameter variations
   - Find best combinations
   - Avoid overfitting

3. **Validate:**
   - Walk-forward analysis
   - Out-of-sample testing
   - Monte Carlo simulation

4. **Paper Trade:**
   - OpenAlgo Analyzer Mode
   - 2 weeks minimum
   - Compare to backtest

5. **Go Live:**
   - Start with minimum capital
   - Monitor closely
   - Scale gradually

---

## Support

- **Questions?** Read the full strategy guide
- **Need data?** Check broker APIs or data vendors
- **Backtest issues?** Review logs and CSV outputs

**Remember:** Backtesting is essential but not a guarantee of live performance!

---

**Last Updated:** September 2026  
**Version:** 1.0.0
