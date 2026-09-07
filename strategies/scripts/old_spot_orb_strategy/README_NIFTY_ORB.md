# 🎯 Nifty First Candle ORB Strategy

Professional Opening Range Breakout strategy for Nifty ATM Options.

## ⚡ Quick Start

```bash
# 1. Navigate to OpenAlgo Python Strategies
http://localhost:5000/python

# 2. Upload Strategy
- File: nifty_first_candle_orb_strategy.py
- Exchange: NFO
- Schedule: 09:15-15:30, Mon-Fri

# 3. Start Strategy
Click "Start" or wait for scheduled start
```

## 📊 Strategy Summary

| Parameter | Value |
|-----------|-------|
| **Instrument** | Nifty ATM Options (CE/PE) |
| **Timeframe** | 1 Minute |
| **Position Size** | 3 Lots |
| **Risk/Trade** | 5% of capital |
| **Max Daily Loss** | 10% of capital |
| **Entry** | ORB High/Low + 3 point buffer |
| **Stop Loss** | Opposite ORB level |
| **TP1** | 1R (Exit 2 lots) |
| **TP2** | 2R (Exit 1 lot) |
| **Trailing** | 15 points |
| **Max Trades** | 2 per day |

## 📁 Files Included

```
strategies/scripts/
├── nifty_first_candle_orb_strategy.py  ← Main strategy (upload this)
├── nifty_orb_config.json               ← Configuration parameters
├── NIFTY_ORB_STRATEGY_GUIDE.md         ← Complete documentation
└── README_NIFTY_ORB.md                 ← This file
```

## 🔐 Required Setup

### 1. Environment Variables
```bash
OPENALGO_API_KEY=<your_key>          # From OpenAlgo dashboard
HOST_SERVER=http://127.0.0.1:5000   # Default
WEBSOCKET_URL=ws://127.0.0.1:8765   # Default
```

### 2. Broker Requirements
- ✅ NFO (Options) segment enabled
- ✅ Minimum capital: ₹1,00,000
- ✅ Options trading approved
- ✅ Sufficient margin for 3 lots

### 3. OpenAlgo Configuration
- ✅ Broker connected
- ✅ API key generated
- ✅ Market data enabled

## 🎯 How It Works

```
09:15:00 → Market Opens
09:16:00 → First Candle Closes
         ↓
    Record ORB High/Low
         ↓
    Wait for Breakout
         ↓
┌────────┴────────┐
↓                 ↓
CALL @ High+3     PUT @ Low-3
↓                 ↓
3 Lots Entry
↓
SL @ Opposite Level
↓
TP1 @ 1R → Exit 2 lots → Move SL to Breakeven
↓
TP2 @ 2R → Exit 1 lot → Activate Trailing
↓
Trail Remaining Position
```

## ⚙️ Configuration

Edit `nifty_orb_config.json` for custom parameters:

```json
{
  "breakout_buffer": 3,           // Test: 2, 3, 5
  "tp1_multiplier": 1.0,          // Fixed at 1R
  "tp2_multiplier": 2.0,          // Test: 1.5, 2.0, 2.5, 3.0
  "trailing_stop_points": 15,     // Test: 10, 15, 20
  "risk_per_trade_pct": 5.0,      // 5% per trade
  "max_daily_loss_pct": 10.0      // 10% daily max
}
```

## 📈 Risk Management

### Capital Requirements
| Your Capital | Max Risk/Trade | Max Daily Loss |
|--------------|----------------|----------------|
| ₹1,00,000 | ₹5,000 | ₹10,000 |
| ₹1,50,000 | ₹7,500 | ₹15,000 |
| ₹2,00,000 | ₹10,000 | ₹20,000 |

### Trading Limits
- Maximum **2 trades per day**
- Stop trading if daily loss hits **10%**
- Position sizing validation before entry
- Never exceed risk limits

## 🚨 Risk Warnings

### ⚠️ HIGH RISK STRATEGY
- **Options decay:** Time value loss throughout the day
- **Leverage:** High gains/losses possible
- **5% risk:** Aggressive for options trading
- **No guarantees:** Past performance ≠ future results

### Before Live Trading:
1. ✅ **Backtest** minimum 3 months
2. ✅ **Paper trade** minimum 2 weeks
3. ✅ **Verify** all parameters
4. ✅ **Test** with small capital first

## 📊 Monitoring

### View Logs
```bash
# In OpenAlgo dashboard
/python → Select Strategy → Click "Logs"

# Or in terminal
tail -f logs/strategies/nifty_first_candle_orb_strategy_*.log
```

### Key Log Messages
```
✅ "ORB LEVELS ESTABLISHED" - First candle closed
🔼 "CALL BREAKOUT DETECTED" - Entry signal
🔽 "PUT BREAKOUT DETECTED" - Entry signal
🎯 "TP1 HIT @ 1R" - First target
🎯 "TP2 HIT @ 2R" - Second target
🛑 "STOP LOSS HIT" - Exit signal
📉 "TRAILING STOP HIT" - Trail exit
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Strategy won't start | Check API key, broker connection |
| ORB not calculating | Wait 60 seconds after 09:15 |
| No trades executing | Verify risk limits, check logs |
| Orders failing | Check option liquidity, margin |
| Wrong option selected | Verify ATM strike calculation |

## 📚 Documentation

### Complete Guide
Read `NIFTY_ORB_STRATEGY_GUIDE.md` for:
- Detailed strategy logic
- Entry/exit rules
- Position management
- Backtesting guide
- Performance metrics
- Daily checklist

### Configuration Reference
See `nifty_orb_config.json` for all parameters

## 🎯 Strategy Features

### ✅ Implemented
- [x] First candle ORB detection
- [x] Breakout with configurable buffer
- [x] ATM option selection
- [x] Multi-stage exits (TP1, TP2, Trail)
- [x] Breakeven move after TP1
- [x] Trailing stop management
- [x] Risk validation (5% per trade, 10% daily)
- [x] Trade limits (max 2/day)
- [x] Position tracking
- [x] Comprehensive logging

### 🔄 Enhancements Possible
- [ ] Integrate actual OHLC data (currently using live price)
- [ ] Add option chain analysis
- [ ] Include IV filtering
- [ ] Add volume confirmation
- [ ] Implement spread monitoring
- [ ] Add recovery strategies
- [ ] Include email/SMS alerts

## 🧪 Backtesting

### Parameters to Test

```json
{
  "breakout_buffer": [2, 3, 5],
  "orb_threshold": [25, 30, 35, 40],
  "tp2_multiplier": [1.5, 2.0, 2.5, 3.0],
  "trailing_stop": [10, 15, 20]
}
```

### Metrics to Track
- Win rate by ORB range (≤30 vs >30)
- CALL vs PUT performance
- TP1/TP2 hit rates
- Average R-multiple
- Maximum drawdown
- Profit factor

## 📞 Support

### Need Help?
- **Full Guide:** `NIFTY_ORB_STRATEGY_GUIDE.md`
- **OpenAlgo Docs:** `/docs/userguide/`
- **Discord:** https://www.openalgo.in/discord
- **GitHub:** https://github.com/marketcalls/openalgo

### Report Issues
Check logs first, then report with:
- Strategy version
- Error message
- Log file excerpt
- Steps to reproduce

## ⚖️ Disclaimer

**EDUCATIONAL USE ONLY**

This strategy involves substantial risk. Options trading is highly leveraged and can result in total loss of invested capital. The developer assumes no responsibility for any losses. 

**ALWAYS:**
- Backtest thoroughly
- Paper trade first
- Start with small size
- Never risk more than you can afford to lose
- Consult a financial advisor

**USE AT YOUR OWN RISK**

---

## 📋 Quick Checklist

Before going live:

- [ ] Backtested minimum 3 months
- [ ] Paper traded minimum 2 weeks
- [ ] Verified broker supports NFO options
- [ ] Confirmed sufficient capital (₹1L+)
- [ ] Tested with small position size
- [ ] Understood all risks
- [ ] Read complete documentation
- [ ] Configured parameters correctly
- [ ] Set up monitoring/alerts
- [ ] Have exit plan ready

---

**Version:** 1.0.0  
**Date:** September 2026  
**Compatibility:** OpenAlgo 2.0+

**🚀 Ready to deploy? Upload `nifty_first_candle_orb_strategy.py` to OpenAlgo!**
