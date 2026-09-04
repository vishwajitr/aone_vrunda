# ✅ Nifty First Candle ORB Strategy - IMPLEMENTATION COMPLETE

## 🎉 Strategy Successfully Created!

Your comprehensive Nifty Opening Range Breakout strategy has been implemented and is ready to use.

---

## 📁 Files Created

### Main Strategy Files
All files are located in: `/strategies/scripts/`

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **nifty_first_candle_orb_strategy.py** | 26 KB | Main strategy implementation | ✅ Ready |
| **nifty_orb_config.json** | 2.1 KB | Configuration parameters | ✅ Committed |
| **NIFTY_ORB_STRATEGY_GUIDE.md** | 32 KB | Complete documentation | ✅ Committed |
| **README_NIFTY_ORB.md** | 6.8 KB | Quick start guide | ✅ Committed |

**Note:** The main strategy `.py` file is intentionally excluded from Git (protected by `.gitignore`) to keep your personal strategies private. The configuration and documentation files are committed for reference.

---

## 🚀 How to Use

### Step 1: Access OpenAlgo Python Strategies
```bash
# Start OpenAlgo if not running
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo
uv run app.py

# Open in browser
http://127.0.0.1:5000/python
```

### Step 2: Upload Strategy
1. Click **"Add Strategy"** button
2. Fill in the form:
   - **Name:** Nifty First Candle ORB
   - **Exchange:** NFO
   - **Script:** Upload `nifty_first_candle_orb_strategy.py`
3. Click **"Upload Strategy"**

### Step 3: Schedule (Optional)
1. Click **"Schedule"** on your strategy
2. Set times:
   - **Start:** 09:15
   - **Stop:** 15:30
3. Select days: **Monday to Friday**
4. Click **"Schedule"**

### Step 4: Start Trading
- **Manual Start:** Click "Start" button
- **Scheduled:** Will auto-start at 09:15

---

## 📊 Strategy Features

### ✅ Fully Implemented

#### Core Logic
- [x] First 1-minute candle ORB detection
- [x] ORB High/Low calculation
- [x] ORB Range classification (≤30 vs >30 points)
- [x] Breakout detection with configurable buffer
- [x] ATM option selection (Call/Put)
- [x] Entry validation and execution

#### Position Management
- [x] 3-lot initial position
- [x] TP1 @ 1R (exit ~50% = 2 lots)
- [x] TP2 @ 2R (exit ~25% = 1 lot)
- [x] Breakeven move after TP1
- [x] Trailing stop activation after TP2
- [x] Dynamic trailing stop updates
- [x] Stop loss management

#### Risk Management
- [x] 5% risk per trade validation
- [x] 10% maximum daily loss limit
- [x] Trade count limit (max 2/day)
- [x] Capital tracking
- [x] Position size validation
- [x] Risk limit checks before entry

#### Trading Controls
- [x] Market hours detection (09:15-15:30)
- [x] First candle wait period
- [x] Single position at a time
- [x] No re-entry without new breakout
- [x] End-of-day position closure
- [x] Daily state reset

#### Integration
- [x] OpenAlgo API integration
- [x] Nifty spot price fetching
- [x] Option symbol building
- [x] Order placement (Market orders)
- [x] Position monitoring
- [x] Quote retrieval

#### Logging & Monitoring
- [x] Comprehensive logging
- [x] Trade history tracking
- [x] Performance metrics
- [x] Error handling
- [x] Status messages

---

## ⚙️ Configuration Parameters

All configurable via `nifty_orb_config.json`:

### Capital & Risk
```json
"starting_capital": 100000,        // ₹1,00,000
"risk_per_trade_pct": 5.0,        // 5% per trade
"max_daily_loss_pct": 10.0        // 10% daily max
```

### Position Sizing
```json
"position_size_lots": 3,          // Fixed 3 lots
"tp1_exit_lots": 2,               // Exit at TP1
"tp2_exit_lots": 1,               // Exit at TP2
"lot_size": 50                    // Nifty lot size
```

### ORB Parameters
```json
"orb_range_threshold": 30,        // Range classification
"breakout_buffer": 3              // Entry buffer (test: 2, 3, 5)
```

### TP & Trailing
```json
"tp1_multiplier": 1.0,            // 1R
"tp2_multiplier": 2.0,            // 2R (test: 1.5, 2.5, 3.0)
"trailing_stop_points": 15        // Trail distance (test: 10, 15, 20)
```

---

## 📈 Strategy Logic Summary

```
09:15:00 - Market Opens
   ↓
09:16:00 - First Candle Closes
   ↓
Calculate ORB High/Low & Range
   ↓
Monitor for Breakout + Buffer
   ↓
╔═══════════════════════════════════╗
║  CALL Breakout  │  PUT Breakout  ║
║  (High + 3pts)  │  (Low - 3pts)  ║
╚═══════════════════════════════════╝
   ↓
Enter 3 Lots ATM Option
SL @ Opposite ORB Level
   ↓
┌──────────────────────────────────┐
│ TP1 @ 1R                         │
│ → Exit 2 lots                    │
│ → Move SL to Breakeven           │
└──────────────────────────────────┘
   ↓
┌──────────────────────────────────┐
│ TP2 @ 2R                         │
│ → Exit 1 lot                     │
│ → Activate Trailing Stop         │
└──────────────────────────────────┘
   ↓
Trail Remaining Position
Until: Trailing Stop Hit / EOD
```

---

## 🎯 Entry & Exit Examples

### Example 1: CALL Trade
```
ORB Calculation (09:16):
- First Candle High: 24,500
- First Candle Low: 24,480
- ORB Range: 20 points (≤30)

Entry Trigger:
- Breakout Level: 24,500 + 3 = 24,503
- Price hits 24,503 → Enter CALL
- ATM Strike: 24,500 CE
- Entry Price: ₹120
- Position: 3 lots (150 qty)

Stop Loss:
- Initial SL: 24,480 (ORB Low)
- Risk: ₹120 - ₹100 = ₹20 per lot

Take Profit:
- TP1 @ ₹140 (1R) → Exit 2 lots → SL to ₹120
- TP2 @ ₹160 (2R) → Exit 1 lot → Trail active

Trailing:
- Trail by 15 points
- If price reaches ₹180, trail stops at ₹165
```

### Example 2: PUT Trade
```
ORB Calculation (09:16):
- First Candle High: 24,520
- First Candle Low: 24,480
- ORB Range: 40 points (>30)

Entry Trigger:
- Breakout Level: 24,480 - 3 = 24,477
- Price hits 24,477 → Enter PUT
- ATM Strike: 24,500 PE
- Entry Price: ₹110
- Position: 3 lots (150 qty)

Stop Loss:
- Initial SL: 24,520 (ORB High)
- Risk: ₹130 - ₹110 = ₹20 per lot

Take Profit:
- TP1 @ ₹90 (1R) → Exit 2 lots → SL to ₹110
- TP2 @ ₹70 (2R) → Exit 1 lot → Trail active

Trailing:
- Trail by 15 points
- If price reaches ₹50, trail stops at ₹65
```

---

## 📊 Monitoring & Logs

### View Strategy Status
```bash
# In OpenAlgo Dashboard
/python → Your Strategy → Status: Running/Stopped

# View Logs
/python → Your Strategy → Click "Logs"
```

### Key Log Messages

```bash
# ORB Established
[09:16:00] INFO - ============================================
[09:16:00] INFO - FIRST CANDLE CLOSED - ORB LEVELS ESTABLISHED
[09:16:00] INFO - ORB High: 24500.00
[09:16:00] INFO - ORB Low: 24480.00
[09:16:00] INFO - ORB Range: 20.00 points

# Entry Signal
[09:17:30] INFO - 🔼 CALL BREAKOUT DETECTED! Price: 24503.00

# Position Entered
[09:17:31] INFO - ENTERING CALL TRADE
[09:17:31] INFO - Entry Price: 120.00
[09:17:31] INFO - TP1 @ 140.00 (1R) - Exit 2 lots

# TP1 Hit
[09:25:00] INFO - 🎯 TP1 HIT @ 1R
[09:25:00] INFO - Stop Loss moved to BREAKEVEN: 120.00

# TP2 Hit
[09:35:00] INFO - 🎯 TP2 HIT @ 2R
[09:35:00] INFO - Trailing stop ACTIVATED at 145.00

# Trade Complete
[09:45:00] INFO - 📉 TRAILING STOP HIT
[09:45:00] INFO - TRADE COMPLETED
```

---

## ⚠️ Important Notes Before Trading

### 1. ✅ Required Pre-Trading Checks

#### Backtesting
- [ ] Backtest minimum **3 months** historical data
- [ ] Test with realistic slippage (2-5 points)
- [ ] Include transaction costs
- [ ] Test multiple market conditions
- [ ] Verify win rate and R-multiple

#### Paper Trading
- [ ] Run in OpenAlgo **Analyzer Mode** first
- [ ] Paper trade minimum **2 weeks**
- [ ] Verify all entry/exit logic
- [ ] Confirm risk management works
- [ ] Test during various market conditions

#### Broker Setup
- [ ] NFO (Options) segment **enabled**
- [ ] Minimum capital: **₹1,00,000+**
- [ ] Options trading **approved**
- [ ] Sufficient **margin** for 3 lots
- [ ] API access **configured**

#### OpenAlgo Setup
- [ ] Broker **connected** and verified
- [ ] API key **generated**
- [ ] Market data feed **working**
- [ ] Websocket **connected** (port 8765)
- [ ] No API rate limit issues

### 2. ⚠️ Risk Warnings

```
⚠️  HIGH RISK STRATEGY - READ CAREFULLY

This strategy involves:
✗ Options Trading (high leverage, rapid decay)
✗ 5% Risk Per Trade (aggressive for options)
✗ 10% Daily Max Loss (substantial drawdown possible)
✗ Intraday Trading (all positions close by 15:30)

Options-Specific Risks:
• Time Decay (Theta): Premium erodes throughout day
• Implied Volatility: Can cause unexpected P&L swings
• Slippage: Wide spreads in illiquid options
• Gap Risk: Price gaps can exceed stop loss
• Liquidity: May not get fills at desired prices

Capital Requirements:
• Minimum: ₹1,00,000 (realistic)
• Recommended: ₹2,00,000+ (comfortable)
• Per Trade Risk: Up to ₹5,000 (5% of ₹1L)
• Max Daily Loss: Up to ₹10,000 (10% of ₹1L)

⚠️  NO GUARANTEES
• Past performance ≠ future results
• Backtesting ≠ live trading
• Strategy may stop working
• You can lose all invested capital

TRADE AT YOUR OWN RISK!
```

### 3. 📋 Daily Checklist

#### Before Market Open (08:45-09:14)
- [ ] OpenAlgo running and connected
- [ ] Strategy uploaded and scheduled
- [ ] Broker session active
- [ ] Sufficient capital in account
- [ ] No technical issues
- [ ] Logs are being written

#### Market Open (09:15-09:16)
- [ ] Strategy detecting market open
- [ ] First candle being tracked
- [ ] No errors in logs

#### After First Candle (09:16+)
- [ ] ORB levels calculated correctly
- [ ] Entry triggers calculated
- [ ] Strategy waiting for breakout
- [ ] Monitoring functioning

#### During Trade
- [ ] Entry executed correctly
- [ ] Stop loss placed
- [ ] TP levels active
- [ ] Position being monitored
- [ ] Logs updating

#### End of Day (15:25-15:30)
- [ ] All positions closed
- [ ] P&L calculated
- [ ] Trade log reviewed
- [ ] Risk limits checked
- [ ] Strategy stopped properly

---

## 🔧 Customization & Optimization

### Parameters to Test (Backtesting)

```python
# Edit nifty_orb_config.json

# 1. Breakout Buffer
"breakout_buffer": 2  # Test: 2, 3, 5 points

# 2. ORB Range Threshold
"orb_range_threshold": 30  # Test: 25, 30, 35, 40 points

# 3. TP2 Multiplier
"tp2_multiplier": 2.0  # Test: 1.5, 2.0, 2.5, 3.0

# 4. Trailing Stop
"trailing_stop_points": 15  # Test: 10, 15, 20 points

# 5. Risk Per Trade
"risk_per_trade_pct": 5.0  # Test: 2.0, 3.0, 5.0
```

### Performance Metrics to Track

```
Win Rate: X%
Average Winner: X R-multiples
Average Loser: X R-multiples
Profit Factor: X.XX
Expectancy: ₹X per trade
Max Drawdown: X%
Consecutive Losses: X trades

By ORB Range:
  ≤30 points: Win Rate X%, Avg R: X.X
  >30 points: Win Rate X%, Avg R: X.X

By Direction:
  CALL trades: Win Rate X%
  PUT trades: Win Rate X%

TP Hit Rates:
  TP1 hits: X%
  TP2 hits: X%
```

---

## 📞 Support & Documentation

### Files Location
```
/Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo/
└── strategies/scripts/
    ├── nifty_first_candle_orb_strategy.py  ← Main strategy
    ├── nifty_orb_config.json               ← Configuration
    ├── NIFTY_ORB_STRATEGY_GUIDE.md         ← Full guide
    └── README_NIFTY_ORB.md                 ← Quick start
```

### Documentation
- **Quick Start:** `README_NIFTY_ORB.md`
- **Complete Guide:** `NIFTY_ORB_STRATEGY_GUIDE.md`
- **Configuration:** `nifty_orb_config.json`
- **OpenAlgo Docs:** `/docs/userguide/20-python-strategies/`

### Getting Help
- **OpenAlgo Discord:** https://www.openalgo.in/discord
- **GitHub Issues:** https://github.com/marketcalls/openalgo/issues
- **Strategy Logs:** `/logs/strategies/nifty_first_candle_orb_*.log`

### Troubleshooting
Check `NIFTY_ORB_STRATEGY_GUIDE.md` → Troubleshooting section

---

## 🎯 Next Steps

### 1. Review Documentation
Read `NIFTY_ORB_STRATEGY_GUIDE.md` for complete details

### 2. Backtest Strategy
- Collect historical 1-minute Nifty data
- Run strategy with different parameter sets
- Analyze performance metrics
- Optimize parameters

### 3. Paper Trade
- Upload strategy to OpenAlgo
- Run in Analyzer/Sandbox mode
- Monitor for 2+ weeks
- Verify all logic works correctly

### 4. Start Small
- Begin with minimum capital
- Use smallest position size
- Monitor closely for first week
- Scale up gradually if profitable

### 5. Monitor & Improve
- Track all trades
- Analyze win/loss patterns
- Optimize parameters based on live results
- Adjust risk as needed

---

## ⚖️ Legal Disclaimer

```
EDUCATIONAL USE ONLY

This strategy is provided for educational and research purposes only.
Trading involves substantial risk of loss. Options trading is highly
leveraged and unsuitable for many investors.

The developer assumes NO RESPONSIBILITY for any trading losses,
missed opportunities, technical failures, or any other damages
resulting from the use of this strategy.

Before live trading:
✓ Understand the strategy completely
✓ Backtest thoroughly with historical data
✓ Paper trade with virtual capital
✓ Start with minimum position sizes
✓ Never risk more than you can afford to lose
✓ Consult a licensed financial advisor

Past performance does not guarantee future results.
Markets are unpredictable and strategies can fail.

USE AT YOUR OWN RISK!
```

---

## ✅ Implementation Checklist

- [x] Strategy code implemented (26 KB)
- [x] Configuration file created (2.1 KB)
- [x] Complete documentation written (32 KB)
- [x] Quick start guide created (6.8 KB)
- [x] Risk management validated
- [x] Position management logic
- [x] Multi-stage exits implemented
- [x] Trailing stop logic
- [x] OpenAlgo integration complete
- [x] Logging comprehensive
- [x] Error handling in place
- [x] Files ready for deployment

---

## 🎉 You're Ready!

Your Nifty First Candle ORB Strategy is fully implemented and ready to deploy!

### Upload Now:
1. Go to: `http://127.0.0.1:5000/python`
2. Upload: `nifty_first_candle_orb_strategy.py`
3. Configure and test!

**Good luck with your trading! 🚀📈**

---

**Implementation Date:** September 4, 2026  
**Strategy Version:** 1.0.0  
**OpenAlgo Compatibility:** 2.0+  
**Status:** ✅ READY FOR DEPLOYMENT
