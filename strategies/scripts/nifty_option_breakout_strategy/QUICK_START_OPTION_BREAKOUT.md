# Quick Start Guide - Nifty ATM Option Breakout Strategy

## 📋 Overview

This strategy trades **option premium breakouts** (not Nifty spot) based on the first 1-minute candle of ATM CE and PE options.

---

## ⚙️ Strategy Configuration

### Key Parameters:
- **Starting Capital**: ₹1,00,000
- **Position Size**: 1 lot (fixed)
- **Target**: +15 option points (fixed)
- **Stop Loss**: First candle low
- **Range Filter**: 10-35 points
- **Max Trades**: 2 initial + 1 re-entry per side
- **Risk Management**: 5% per trade, 10% daily loss

---

## 🚀 Running the Strategy

### 1. Set Environment Variables

```bash
export OPENALGO_API_KEY="your_api_key_here"
export OPENALGO_HOST="http://127.0.0.1:5000"
```

### 2. Run the Strategy

```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo/strategies/scripts
python3 nifty_atm_option_breakout_strategy.py
```

---

## 📊 How It Works

### Step 1: Market Open (9:15 AM)
```
1. Identify ATM strike based on Nifty spot
2. Select ATM CE and ATM PE
3. Wait for first 1-minute candle to close (9:16 AM)
```

### Step 2: First Candle Capture (9:16 AM)
```
For CE:
├─ Record High, Low, Range
└─ Valid if Range is 10-35 points

For PE:
├─ Record High, Low, Range
└─ Valid if Range is 10-35 points
```

### Step 3: Monitor for Breakout
```
CE Breakout:
├─ When CE premium > First Candle High
├─ BUY 1 lot
├─ Target = Entry + 15 points
└─ SL = First Candle Low

PE Breakout:
├─ When PE premium > First Candle High
├─ BUY 1 lot
├─ Target = Entry + 15 points
└─ SL = First Candle Low
```

### Step 4: Re-Entry Logic
```
If SL Hit:
├─ Can take 1 re-entry if High breaks again
├─ Same SL (First Candle Low)
└─ New Target = New Entry + 15 points

If Target Hit:
└─ No re-entry allowed
```

---

## 📈 Trade Examples

### Example 1: CE Trade
```
9:15-9:16 AM - First Candle:
├─ High: ₹180
├─ Low: ₹165
└─ Range: 15 points ✅ (Valid: 10-35)

9:22 AM - Breakout:
├─ CE premium breaks ₹180
├─ Entry: ₹181
├─ Target: ₹196 (+15 points)
├─ Stop Loss: ₹165
└─ Position: 1 lot (50 qty)

Outcome 1 (Target Hit):
├─ CE reaches ₹196
├─ Exit: ₹196
├─ P&L: (196 - 181) × 150 = ₹2,250 profit ✅
└─ No re-entry allowed

Outcome 2 (SL Hit):
├─ CE drops to ₹165
├─ Exit: ₹165
├─ P&L: (165 - 181) × 150 = ₹-2,400 loss ❌
└─ Can re-enter if CE breaks ₹180 again
```

### Example 2: PE Trade with Re-Entry
```
9:15-9:16 AM - First Candle:
├─ High: ₹170
├─ Low: ₹155
└─ Range: 15 points ✅ (Valid)

9:25 AM - First Entry:
├─ PE breaks ₹170
├─ Entry: ₹171
├─ Target: ₹186
├─ SL: ₹155
└─ Position: 1 lot

9:32 AM - SL Hit:
├─ PE drops to ₹155
├─ Loss: (155 - 171) × 150 = ₹-2,400 ❌
└─ Watching for re-entry...

9:45 AM - Re-Entry:
├─ PE breaks ₹170 again
├─ Re-entry: ₹172
├─ Target: ₹187 (+15 from re-entry)
├─ SL: ₹155 (same as original)
└─ Position: 1 lot

10:05 AM - Target Hit:
├─ PE reaches ₹187
├─ Profit: (187 - 172) × 150 = ₹2,250 ✅
└─ Net: ₹-2,400 + ₹2,250 = ₹-150 (small loss but recovered)
```

---

## ⚠️ Important Notes

### Range Filter is Critical
```
First Candle Range < 10 points → ❌ Skip (too tight)
First Candle Range > 35 points → ❌ Skip (too volatile)
First Candle Range 10-35 points → ✅ Trade valid
```

### Independent Sides
- CE and PE are completely independent
- Each can have 1 initial entry + 1 re-entry
- One side's re-entry doesn't affect the other

### Risk Limits
- **Per Trade**: 5% of current capital
- **Daily Loss**: 10% of current capital
- **Max Positions**: Only 1 at a time

---

## 📝 Trading Checklist

### Before Trading:
- [ ] OPENALGO_API_KEY is set
- [ ] Strategy is connected to broker
- [ ] Market is open (9:15 AM onwards)

### After First Candle:
- [ ] CE range checked (10-35 points?)
- [ ] PE range checked (10-35 points?)
- [ ] Valid sides marked for trading

### Before Entry:
- [ ] Premium broke above first candle high?
- [ ] No other position open?
- [ ] Within risk limits (5%)?
- [ ] Within daily loss limit (10%)?

### During Trade:
- [ ] Monitor for target hit (+15 points)
- [ ] Monitor for SL hit (first candle low)
- [ ] If SL hit, watch for re-entry

---

## 🎯 Expected Performance

### Realistic Expectations:
- **Win Rate**: 40-60% (typical for breakout strategies)
- **Risk:Reward**: Varies based on first candle range
- **Best Conditions**: Moderate volatility (15-25 point range)
- **Worst Conditions**: Very low (<10) or high (>35) volatility

---

## 🔧 Customization

Edit `nifty_atm_option_breakout_strategy.py` to modify:

```python
@dataclass
class StrategyConfig:
    STARTING_CAPITAL: float = 100000  # Change capital
    MIN_RANGE: float = 10.0           # Adjust min range
    MAX_RANGE: float = 35.0           # Adjust max range
    TARGET_POINTS: float = 15.0       # Change target
    POSITION_SIZE_LOTS: int = 1       # Change lot size
```

---

## 📞 Support

For issues or questions:
1. Check logs in terminal output
2. Verify API connection
3. Review trade history
4. Test with paper trading first

---

**⚠️ Risk Disclaimer**: This strategy involves significant risk. Always test thoroughly before live trading.
