# Nifty ATM Option Breakout Strategy

## 📁 Project Structure

```
strategies/scripts/
├── nifty_option_breakout_strategy/       # ⭐ NEW STRATEGY (Current)
│   ├── nifty_atm_option_breakout_strategy.py
│   ├── backtest_option_breakout.py
│   ├── NIFTY_ATM_OPTION_BREAKOUT_STRATEGY.md
│   ├── QUICK_START_OPTION_BREAKOUT.md
│   ├── option_breakout_results.csv
│   └── README.md
│
├── old_spot_orb_strategy/                # Previous strategy (archived)
│   ├── nifty_first_candle_orb_strategy.py
│   ├── backtest_results_*.csv
│   └── [other old files]
│
├── nifty_ohlcv.csv                       # Historical data (1 month)
├── nifty_1min_ohlcv.csv                  # Historical data (1 day)
├── fetch_nse_options.py                  # Option data fetcher (helper)
├── run_backtest.py                       # Old backtest engine
└── README.md                             # This file
```

---

## 🎯 What Changed?

### OLD Strategy (Archived)
- ❌ Traded **Nifty Spot** breakouts
- ❌ Used ORB range from Nifty spot price
- ❌ Multi-stage TP (1R, 2R) with trailing
- ❌ Complex exit logic

### NEW Strategy (Current)
- ✅ Trades **Option Premium** breakouts
- ✅ Uses first candle of ATM CE/PE options
- ✅ Fixed +15 point target (simple)
- ✅ Re-entry logic (1 per side)
- ✅ Range filter: 10-35 points
- ✅ CE and PE trade independently

---

## 🚀 Quick Start

### 1. Navigate to Strategy Folder
```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo/strategies/scripts/nifty_option_breakout_strategy
```

### 2. Read the Documentation
```bash
# Complete strategy rules
open NIFTY_ATM_OPTION_BREAKOUT_STRATEGY.md

# Quick start guide with examples
open QUICK_START_OPTION_BREAKOUT.md
```

### 3. Set Up Environment
```bash
export OPENALGO_API_KEY="your_api_key_here"
export OPENALGO_HOST="http://127.0.0.1:5000"
```

### 4. Run the Strategy
```bash
# Live trading
python3 nifty_atm_option_breakout_strategy.py

# Or backtest
python3 backtest_option_breakout.py --data ../nifty_ohlcv.csv
```

---

## 📊 Strategy Summary

### Entry Rules
```
For CE (Call):
├─ Wait for first 1-min candle (9:15-9:16 AM)
├─ Check range: 10-35 points? ✅
├─ When CE premium breaks first candle high
└─ BUY 3 lots

For PE (Put):
├─ Wait for first 1-min candle (9:15-9:16 AM)
├─ Check range: 10-35 points? ✅
├─ When PE premium breaks first candle high
└─ BUY 3 lots
```

### Exit Rules
```
Target: Entry + 15 points
Stop Loss: First candle low
Re-Entry: 1 time per side (only if SL hit)
```

### Risk Management
```
Capital: ₹1,00,000
Risk per Trade: 5% (₹5,000)
Daily Loss Limit: 10% (₹10,000)
Position Size: 3 lots (fixed)
```

---

## 🎓 Key Features

### 1. Range Filter
- **Minimum**: 10 points (avoid tight ranges)
- **Maximum**: 35 points (avoid excessive volatility)
- Invalid ranges are automatically skipped

### 2. Independent Sides
- CE and PE trade separately
- Each has own entry/exit/re-entry
- Can trade both simultaneously (if limits allow)

### 3. Re-Entry Logic
- Only after stop loss is hit
- Maximum 1 re-entry per side
- Uses same first candle high/low
- New target calculated from re-entry price

### 4. Risk Controls
- No position if risk exceeds 5%
- Stop trading if daily loss hits 10%
- Maximum 2 initial trades + 2 re-entries per day
- Only 1 position open at a time

---

## 📈 Example Trade Flow

```
9:15 AM - Market Opens
├─ Nifty Spot: 24,500
├─ ATM Strike: 24,500
├─ Select: 24500 CE and 24500 PE
└─ Wait for first candle...

9:16 AM - First Candle Closes
├─ CE: High ₹180, Low ₹165, Range 15 ✅
├─ PE: High ₹170, Low ₹155, Range 15 ✅
└─ Both valid! Monitoring breakouts...

9:22 AM - CE Breakout
├─ CE premium hits ₹181 (breaks ₹180)
├─ BUY 3 lots CE
├─ Entry: ₹181
├─ Target: ₹196 (+15)
└─ SL: ₹165

9:35 AM - CE Target Hit
├─ CE reaches ₹196
├─ Exit 3 lots
├─ P&L: (196-181) × 150 = ₹2,250 profit ✅
└─ No CE re-entry allowed (target hit)

10:15 AM - PE Breakout
├─ PE premium hits ₹171 (breaks ₹170)
├─ BUY 3 lots PE
├─ Entry: ₹171
├─ Target: ₹186 (+15)
└─ SL: ₹155

10:25 AM - PE SL Hit
├─ PE drops to ₹155
├─ Exit 3 lots
├─ P&L: (155-171) × 150 = ₹-2,400 loss ❌
└─ PE re-entry available!

10:40 AM - PE Re-Entry
├─ PE breaks ₹170 again at ₹172
├─ BUY 3 lots PE (re-entry)
├─ Entry: ₹172
├─ Target: ₹187 (+15)
└─ SL: ₹155

11:00 AM - PE Target Hit
├─ PE reaches ₹187
├─ Exit 3 lots
├─ P&L: (187-172) × 150 = ₹2,250 profit ✅
└─ No more PE trades allowed today

Day Result:
├─ CE Trade: +₹2,250
├─ PE Trade 1: -₹2,400
├─ PE Trade 2: +₹2,250
├─ Net P&L: +₹2,100 ✅
└─ Total Trades: 3 (1 CE + 2 PE)
```

---

## ⚠️ Important Notes

### Data Requirements
This strategy **CANNOT** be backtested using Nifty spot data!

You need:
- ✅ Historical ATM CE 1-minute OHLC data
- ✅ Historical ATM PE 1-minute OHLC data
- ✅ First candle high/low for each option

### Backtest Limitations
- `run_backtest.py` was built for the OLD spot-based strategy
- New backtester needed for option premium data
- Use `fetch_nse_options.py` to collect real option data

### Live Trading
- Always paper trade first!
- Verify option symbols are correct
- Check lot size for your broker
- Monitor slippage and execution

---

## 📞 Next Steps

1. **Read Documentation**
   - Open `NIFTY_ATM_OPTION_BREAKOUT_STRATEGY.md`
   - Review all 22 sections thoroughly

2. **Test Environment**
   - Set up API keys
   - Test connection to OpenAlgo
   - Verify broker integration

3. **Paper Trade**
   - Run strategy in paper trading mode
   - Monitor for 1-2 weeks
   - Validate all entry/exit logic

4. **Collect Data**
   - Use `fetch_nse_options.py` for historical data
   - Build proper backtest with actual option data
   - Optimize parameters if needed

5. **Go Live**
   - Start with small capital
   - Monitor closely for first few days
   - Keep detailed trade logs

---

## 🔧 Support & Troubleshooting

### Common Issues

**Strategy doesn't start:**
```bash
# Check API key
echo $OPENALGO_API_KEY

# Verify OpenAlgo is running
curl http://127.0.0.1:5000/api/v1/funds
```

**No trades executed:**
- Check first candle range (must be 10-35 points)
- Verify market hours (9:15 AM - 3:30 PM)
- Confirm risk limits not exceeded

**Can't find option symbols:**
- ATM strike may be wrong
- Expiry date calculation issue
- Use `fetch_nse_options.py` to test

---

## 📝 Version History

- **v2.0.0** (Sep 6, 2026) - NEW: Option premium breakout strategy
- **v1.0.0** (Sep 4, 2026) - OLD: Nifty spot ORB strategy (archived)

---

**Created by**: OpenAlgo Strategy Builder  
**Last Updated**: September 6, 2026  
**Status**: Active Development
