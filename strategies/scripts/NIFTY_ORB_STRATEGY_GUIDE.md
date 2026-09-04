# Nifty First 1-Minute Candle ORB Strategy - Implementation Guide

## 📋 Strategy Overview

This is a professional implementation of the Opening Range Breakout (ORB) strategy that trades Nifty ATM options based on the first 1-minute candle after market open.

### Key Features
- ✅ First candle ORB breakout detection
- ✅ Multi-stage profit taking (TP1 @ 1R, TP2 @ 2R)
- ✅ Trailing stop for final position
- ✅ Breakeven move after TP1
- ✅ Configurable breakout buffer (2, 3, 5 points)
- ✅ Risk management (5% per trade, 10% daily max loss)
- ✅ ATM option selection
- ✅ 3-lot position with partial exits
- ✅ Maximum 2 trades per day
- ✅ 30-point range classification for analysis

---

## 🚀 Quick Start

### 1. Prerequisites
- OpenAlgo installed and configured
- Broker account connected (supports NFO options)
- Sufficient capital (recommended: ₹1,00,000+)
- API key generated in OpenAlgo

### 2. Upload Strategy
1. Go to OpenAlgo dashboard: `http://localhost:5000/python`
2. Click "Add Strategy"
3. Upload: `nifty_first_candle_orb_strategy.py`
4. Set Exchange: **NFO**
5. Set parameters (or use defaults)

### 3. Configure Schedule
- **Start Time:** 09:15 (market open)
- **Stop Time:** 15:30 (market close)
- **Days:** Monday to Friday
- **Exchange:** NFO

### 4. Required Environment Variables
```bash
OPENALGO_API_KEY=<your_api_key>
HOST_SERVER=http://127.0.0.1:5000
WEBSOCKET_URL=ws://127.0.0.1:8765
```

---

## ⚙️ Configuration

Edit `nifty_orb_config.json` to customize parameters:

### Capital & Risk
```json
{
  "starting_capital": 100000,
  "risk_per_trade_pct": 5.0,
  "max_daily_loss_pct": 10.0
}
```

### ORB Parameters
```json
{
  "orb_range_threshold": 30,
  "breakout_buffer": 3
}
```

### TP & Trailing
```json
{
  "tp1_multiplier": 1.0,
  "tp2_multiplier": 2.0,
  "trailing_stop_points": 15
}
```

---

## 📊 Strategy Logic Flow

```
Market Open (09:15)
         ↓
Wait for First 1-Min Candle to Close
         ↓
Record ORB High/Low & Calculate Range
         ↓
Wait for Breakout + Buffer
         ↓
    ┌────────┴────────┐
    ↓                 ↓
CALL Entry        PUT Entry
(ORB High+Buffer) (ORB Low-Buffer)
    ↓                 ↓
3 Lots ATM CE     3 Lots ATM PE
    ↓                 ↓
SL @ ORB Low      SL @ ORB High
    └────────┬────────┘
             ↓
     Position Management
             ↓
     ┌───────┴───────┐
     ↓               ↓
   TP1 @ 1R      TP2 @ 2R
 (Exit 2 lots)  (Exit 1 lot)
     ↓               ↓
  Move SL to    Trail Remaining
  Breakeven      Position
```

---

## 💰 Position Sizing & Exits

### Entry
- **Initial Position:** 3 lots (150 quantity @ 50 lot size)
- **Option Type:** ATM Call or Put
- **Entry Trigger:** ORB level + breakout buffer

### Exit Stages
| Stage | Trigger | Action | Remaining |
|-------|---------|--------|-----------|
| **Entry** | - | Buy 3 lots | 3 lots |
| **TP1** | 1R profit | Exit 2 lots (~50%) | 1 lot |
| **Breakeven** | After TP1 | Move SL to entry | 1 lot |
| **TP2** | 2R profit | Exit 0.5 lots (~25%)* | 0.5 lot |
| **Trail** | Activated | Trail remaining | Variable |

*Note: Since we can't trade 0.5 lots, exit 1 lot at TP2, leaving 0 lots. Adjust lot allocation based on your preference.

**Alternative Allocation:**
- **TP1:** Exit 1 lot (leaving 2 lots)
- **TP2:** Exit 1 lot (leaving 1 lot for trailing)

---

## 📈 Risk Management

### Per Trade Risk
```
Max Risk = Current Capital × 5%
Example: ₹1,00,000 × 5% = ₹5,000
```

### Daily Risk
```
Max Daily Loss = Current Capital × 10%
Example: ₹1,00,000 × 10% = ₹10,000
```

### Risk Calculation
```
1R = |Entry Price - Stop Loss|

For CALL: 1R = Entry - ORB Low
For PUT: 1R = ORB High - Entry

Maximum Loss = 1R × Position Size
```

### Capital Updates
| Capital | Max Risk/Trade (5%) | Max Daily Loss (10%) |
|---------|---------------------|----------------------|
| ₹1,00,000 | ₹5,000 | ₹10,000 |
| ₹1,20,000 | ₹6,000 | ₹12,000 |
| ₹1,50,000 | ₹7,500 | ₹15,000 |
| ₹2,00,000 | ₹10,000 | ₹20,000 |

---

## 🎯 Entry Rules

### CALL Trade
- **Condition:** Nifty breaks above ORB High + buffer
- **Entry:** Buy ATM Call (3 lots)
- **Stop Loss:** ORB Low
- **Example:**
  - ORB High: 24,500
  - Buffer: 3 points
  - Entry Trigger: 24,503
  - Stop Loss: 24,480 (ORB Low)

### PUT Trade
- **Condition:** Nifty breaks below ORB Low - buffer
- **Entry:** Buy ATM Put (3 lots)
- **Stop Loss:** ORB High
- **Example:**
  - ORB Low: 24,480
  - Buffer: 3 points
  - Entry Trigger: 24,477
  - Stop Loss: 24,500 (ORB High)

---

## 📉 Stop Loss & Take Profit

### Stop Loss Rules
1. **Initial SL:** Opposite side of ORB
2. **After TP1:** Move SL to breakeven (entry price)
3. **After TP2:** Activate trailing stop
4. **Trailing:** Only moves in profitable direction

### Take Profit Targets
```
TP1 = Entry ± (1R)
TP2 = Entry ± (2R)

Where R = |Entry - Stop Loss|
```

**Example for CALL:**
- Entry: ₹120
- SL: ₹100
- R = 120 - 100 = ₹20
- TP1 = 120 + 20 = ₹140
- TP2 = 120 + 40 = ₹160

---

## 🔧 Backtesting Parameters

### Variables to Test

#### 1. Breakout Buffer
- **Test:** 2, 3, 5 points
- **Default:** 3 points
- **Impact:** Entry timing and frequency

#### 2. ORB Range Threshold
- **Test:** 25, 30, 35, 40 points
- **Default:** 30 points
- **Impact:** Range classification for analysis

#### 3. TP Multipliers
- **TP1:** 1.0R (fixed)
- **TP2:** Test 1.5R, 2.0R, 2.5R, 3.0R
- **Default:** 2.0R
- **Impact:** Profit capture vs trend following

#### 4. Trailing Stop
- **Test:** 10, 15, 20 points
- **Default:** 15 points
- **Impact:** Final exit timing

---

## 📊 Performance Metrics to Track

### Trade Metrics
- Win Rate
- Average Winner
- Average Loser
- Risk:Reward Ratio
- Profit Factor
- Expectancy

### Position Metrics
- TP1 Hit Rate
- TP2 Hit Rate
- Breakeven Exits
- Trailing Stop Exits
- Stop Loss Hits

### Strategy Metrics
- Trades per Day
- Daily P&L
- Maximum Drawdown
- Consecutive Losses
- Recovery Factor

### Classification Metrics
Track separately:
- ORB Range ≤ 30 points
- ORB Range > 30 points
- CALL vs PUT trades
- First vs Second trade of day

---

## ⚠️ Important Notes

### Before Live Trading

1. **✅ Backtest Thoroughly**
   - Minimum 3 months historical data
   - Include transaction costs
   - Use realistic slippage
   - Test multiple market conditions

2. **✅ Paper Trade**
   - Run in Analyzer Mode first
   - Verify order execution
   - Test position management
   - Confirm risk limits work

3. **✅ Verify Broker Support**
   - Options trading enabled
   - NFO segment active
   - Sufficient margin
   - API limits understood

4. **✅ Check Lot Size**
   - Current Nifty lot size: 50
   - Verify before each expiry
   - Lot size changes affect position sizing

### During Live Trading

1. **Monitor Execution**
   - Watch first candle formation
   - Verify ORB levels calculated
   - Confirm breakout detection
   - Check order fills

2. **Risk Controls**
   - Never override risk limits
   - Stop trading at daily loss limit
   - Maximum 2 trades per day
   - Close all positions by 15:25

3. **Option Selection**
   - Verify ATM strike is correct
   - Check bid-ask spread
   - Ensure sufficient liquidity
   - Confirm expiry date

4. **Position Management**
   - TP1/TP2 orders placed correctly
   - Breakeven SL updated
   - Trailing stop activated
   - Emergency exit ready

---

## 🚨 Risk Warnings

### High-Risk Strategy
This strategy involves:
- **Options Trading:** High leverage, rapid premium decay
- **Aggressive Risk:** 5% per trade is significant
- **Daily Loss:** 10% daily max loss is substantial
- **Intraday:** All positions must close by market close

### Options-Specific Risks
- **Implied Volatility:** Premium affected by IV changes
- **Time Decay:** Theta decay reduces option value
- **Slippage:** Wide spreads in illiquid options
- **Gap Risk:** Overnight gaps (not applicable for intraday)
- **Pin Risk:** Options expiring near strike

### Capital Requirements
- **Minimum:** ₹1,00,000 (realistic)
- **Recommended:** ₹2,00,000+ (comfortable)
- **Margin:** Ensure sufficient for 3 lots + buffer

### No Guarantees
- Past performance ≠ future results
- Backtesting ≠ live trading
- Strategy may stop working
- Markets are unpredictable

**TRADE AT YOUR OWN RISK**

---

## 📝 Daily Checklist

### Pre-Market (08:45 - 09:14)
- [ ] Strategy is scheduled and ready
- [ ] OpenAlgo connected to broker
- [ ] Sufficient capital in account
- [ ] Margin requirements met
- [ ] API limits not reached
- [ ] No technical issues

### Market Open (09:15 - 09:16)
- [ ] First candle forming
- [ ] Strategy monitoring price
- [ ] No errors in logs

### Post First Candle (09:16+)
- [ ] ORB High recorded
- [ ] ORB Low recorded
- [ ] ORB Range calculated
- [ ] Entry triggers calculated
- [ ] Waiting for breakout

### During Trade
- [ ] Position entered correctly
- [ ] Stop loss placed
- [ ] TP1 level active
- [ ] TP2 level active
- [ ] Position monitoring working

### End of Day (15:25 - 15:30)
- [ ] All positions closed
- [ ] P&L calculated
- [ ] Trade log reviewed
- [ ] Risk limits checked
- [ ] Strategy stopped

---

## 🛠️ Troubleshooting

### Common Issues

#### Strategy Not Starting
- Check OPENALGO_API_KEY is set
- Verify broker connection
- Check logs for errors
- Ensure market is open

#### ORB Not Calculated
- Wait for full first candle (60 seconds)
- Check Nifty price feed
- Verify time is after 09:16

#### No Trade Entry
- Confirm breakout + buffer exceeded
- Check risk limits not reached
- Verify 2 trade limit not hit
- Check option symbol is valid

#### Partial Exits Not Working
- Verify lot size configuration
- Check position tracking
- Review TP level calculations
- Confirm order placement

#### Stop Loss Not Triggering
- Check price monitoring frequency
- Verify SL level calculation
- Review position management logic
- Check broker order status

---

## 📞 Support & Resources

### OpenAlgo Resources
- **Documentation:** `/docs/userguide/`
- **Discord:** https://www.openalgo.in/discord
- **GitHub:** https://github.com/marketcalls/openalgo

### Strategy Files
- **Main Script:** `nifty_first_candle_orb_strategy.py`
- **Configuration:** `nifty_orb_config.json`
- **This Guide:** `NIFTY_ORB_STRATEGY_GUIDE.md`

### Logs Location
```
logs/strategies/nifty_first_candle_orb_strategy_YYYYMMDD_HHMMSS.log
```

---

## 📄 Version History

### v1.0.0 (Current)
- Initial implementation
- ORB breakout detection
- Multi-stage TP management
- Trailing stop logic
- Risk management
- ATM option selection
- OpenAlgo integration

---

## ⚖️ Legal Disclaimer

This strategy is provided for educational purposes only. Trading involves substantial risk of loss. The developer assumes no responsibility for trading losses. Always:

- Understand the strategy completely
- Backtest thoroughly
- Paper trade first
- Start with small position sizes
- Never risk more than you can afford to lose
- Consult a financial advisor if needed

**USE AT YOUR OWN RISK**

---

**Last Updated:** September 2026  
**Strategy Version:** 1.0.0  
**Compatibility:** OpenAlgo 2.0+
