# Nifty ATM Option Breakout Strategy

Complete implementation of the Option Breakout Strategy with backtesting support.

---

## 📁 Files in This Folder

```
nifty_option_breakout_strategy/
├── nifty_atm_option_breakout_strategy.py     # Live trading strategy
├── backtest_option_breakout.py               # Backtesting engine
├── NIFTY_ATM_OPTION_BREAKOUT_STRATEGY.md     # Complete documentation (22 sections)
├── QUICK_START_OPTION_BREAKOUT.md            # Quick start guide
├── option_breakout_results.csv               # Latest backtest results
└── README.md                                  # This file
```

---

## 🚀 Quick Start

### 1. **Live Trading**

```bash
cd nifty_option_breakout_strategy

# Set API key
export OPENALGO_API_KEY="your_api_key"

# Run strategy
python3 nifty_atm_option_breakout_strategy.py
```

### 2. **Backtesting**

```bash
cd nifty_option_breakout_strategy

# Backtest with 1-month data
python3 backtest_option_breakout.py --data ../nifty_ohlcv.csv

# Backtest with 1-day data
python3 backtest_option_breakout.py --data ../nifty_1min_ohlcv.csv
```

---

## 📊 Strategy Overview

### Entry Rules
- Trades ATM CE and PE **option premium** breakouts
- Waits for first 1-minute candle (9:15-9:16 AM)
- **Range filter**: 10-35 points (critical!)
- Entry: When premium breaks first candle high

### Exit Rules
- **Target**: Entry + 15 points (fixed)
- **Stop Loss**: First candle low
- **Re-entry**: 1 per side (only after SL hit)

### Risk Management
- **Capital**: ₹1,00,000
- **Risk per trade**: 5%
- **Daily loss limit**: 10%
- **Position size**: 1 lot (fixed)

---

## 📈 Latest Backtest Results

**Period**: Aug 4 - Sep 4, 2026 (23 trading days)

```
✅ Total Trades:       17
✅ Win Rate:           70.59%
✅ Net P&L:            ₹13,921
✅ Return:             +13.92%
✅ Profit Factor:      2.06
✅ Target Hit Rate:    70.59%

Trade Breakdown:
├─ CE Trades: 6  | P&L: ₹621
└─ PE Trades: 11 | P&L: ₹13,300
```

---

## 📚 Documentation

### Main Documentation
Read `NIFTY_ATM_OPTION_BREAKOUT_STRATEGY.md` for:
- Complete strategy rules (22 sections)
- Entry/exit logic
- Re-entry rules
- Risk management
- Trading checklists
- Examples

### Quick Start
Read `QUICK_START_OPTION_BREAKOUT.md` for:
- Setup instructions
- Trade examples
- Common issues
- Tips

---

## 🎯 Key Features

### 1. **Range Filter (10-35 points)**
- Skips tight ranges (< 10 points)
- Avoids excessive volatility (> 35 points)
- **Critical for success!**

### 2. **Independent CE & PE Tracking**
- Each side trades independently
- Separate entry/exit/re-entry
- Can trade both simultaneously

### 3. **Re-Entry System**
- 1 re-entry allowed per side
- Only after stop loss is hit
- Same first candle high/low used
- New target from re-entry price

### 4. **Simple Exit Logic**
- Fixed +15 point target
- First candle low as SL
- No complex trailing stops

---

## ⚠️ Important Notes

### About Backtesting
- Backtest uses **simulated** option premiums
- Based on Nifty spot price movements
- Real option data will be more accurate
- Good for strategy validation

### Before Live Trading
- ✅ Read complete documentation
- ✅ Paper trade for 1-2 weeks
- ✅ Verify API connection
- ✅ Test with small capital first
- ✅ Monitor slippage and execution

---

## 🔧 Customization

### Edit Strategy Parameters

In `nifty_atm_option_breakout_strategy.py`:

```python
@dataclass
class StrategyConfig:
    STARTING_CAPITAL: float = 100000     # Change capital
    POSITION_SIZE_LOTS: int = 1          # Change lot size
    MIN_RANGE: float = 10.0              # Min first candle range
    MAX_RANGE: float = 35.0              # Max first candle range
    TARGET_POINTS: float = 15.0          # Target in points
    RISK_PER_TRADE_PCT: float = 5.0      # Risk percentage
    MAX_DAILY_LOSS_PCT: float = 10.0     # Daily loss limit
```

### Edit Backtest Parameters

In `backtest_option_breakout.py`:

```python
class OptionBreakoutBacktest:
    def __init__(self):
        self.min_range = 10.0         # Adjust range filter
        self.max_range = 35.0         # Adjust range filter
        self.target_points = 15.0     # Change target
        self.position_size_lots = 1   # Change position size
```

---

## 📊 Running Custom Backtests

### Test Different Ranges
```python
# Edit backtest_option_breakout.py
self.min_range = 15.0  # Tighter filter
self.max_range = 30.0  # Tighter filter
```

### Test Different Targets
```python
# Edit backtest_option_breakout.py
self.target_points = 12.0  # Smaller target
# or
self.target_points = 20.0  # Larger target
```

### Compare Results
```bash
# Run multiple backtests with different parameters
python3 backtest_option_breakout.py --data ../nifty_ohlcv.csv --output results_10_35.csv
# (edit parameters)
python3 backtest_option_breakout.py --data ../nifty_ohlcv.csv --output results_15_30.csv
# Compare CSV files
```

---

## 📞 Troubleshooting

### Strategy Won't Start
```bash
# Check API key
echo $OPENALGO_API_KEY

# Verify OpenAlgo is running
curl http://127.0.0.1:5000/api/v1/funds
```

### No Trades Executing
- Check first candle range (must be 10-35 points)
- Verify market hours (9:15 AM - 3:30 PM IST)
- Confirm risk limits not exceeded
- Check daily loss limit

### Backtest Errors
```bash
# Check data file exists
ls -lh ../nifty_ohlcv.csv

# Verify Python installation
python3 --version

# Check pandas/numpy installed
python3 -c "import pandas; import numpy"
```

---

## 📈 Performance Tips

### To Improve Win Rate:
1. Use tighter range filter (e.g., 15-30)
2. Avoid first 30 minutes after market open
3. Add trend filter (only trade with trend)
4. Skip high-volatility days (VIX > 20)

### To Improve Risk:Reward:
1. Adjust target (test 12, 15, 18 points)
2. Use tighter stop loss
3. Implement partial exits
4. Add time-based exit rules

---

## 📝 Version History

- **v2.0.0** (Sep 6, 2026) - Option breakout strategy
- Backtest results: 70.59% win rate, +13.92% return

---

## 🎯 Next Steps

1. ✅ Read `NIFTY_ATM_OPTION_BREAKOUT_STRATEGY.md`
2. ✅ Review `QUICK_START_OPTION_BREAKOUT.md`
3. ✅ Run backtest on your data
4. ✅ Paper trade for validation
5. ✅ Start live with small capital

---

**Created**: September 6, 2026  
**Status**: Active  
**Backtest Validated**: ✅ Yes (13.92% return, 70.59% win rate)
