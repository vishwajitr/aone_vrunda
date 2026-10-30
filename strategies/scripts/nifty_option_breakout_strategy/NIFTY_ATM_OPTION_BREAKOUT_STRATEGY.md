# Nifty ATM Option First 1-Minute Candle Breakout Strategy

## 1. Strategy Overview

This strategy trades the breakout of the first 1-minute candle of the ATM Call and ATM Put options after the Nifty market opens.

### Parameters

- **Underlying**: Nifty 50
- **Timeframe**: 1 Minute
- **Options**: ATM Call and ATM Put
- **Position Size**: 1 lot per trade
- **Starting Capital**: ₹1,00,000
- **Target**: +15 option points
- **Stop Loss**: First 1-minute candle Low
- **Maximum initial trades per day**: 2
- **Maximum re-entry**: 1 per side
- **Minimum first-candle premium range**: 10 points
- **Maximum first-candle premium range**: 35 points

---

## 2. ATM Strike Selection

At the exact start of the first 1-minute candle after the Nifty market opens:

1. Check the Nifty spot price.
2. Determine the ATM strike according to the applicable Nifty strike interval.
3. Select:
   - ATM Call (CE)
   - ATM Put (PE)
4. The selected ATM strike remains fixed for the setup.

**Important**: The ATM strike should not change during the first 1-minute candle if Nifty moves during that minute.

---

## 3. First 1-Minute Candle

During the first 1-minute candle, record the following separately.

### ATM Call
- First Candle High
- First Candle Low
- First Candle Range

### ATM Put
- First Candle High
- First Candle Low
- First Candle Range

**The first candle must fully close before breakout entries are allowed.**

---

## 4. First-Candle Premium Range Filter

A trade setup is valid only when the first 1-minute candle range is between **10 and 35 option points**.

### Formula
```
First Candle Range = First Candle High − First Candle Low
```

The filter applies separately to the ATM Call and ATM Put.

### Valid Range
- **Minimum**: 10 points
- **Maximum**: 35 points

Therefore:
```
10 points ≤ First Candle Range ≤ 35 points
```

### If First Candle Range Is Below 10 Points
If the first candle range is less than 10 points, that option is **invalid for trading**.

No trade should be taken on that option for the day.

### If First Candle Range Is More Than 35 Points
If the first candle range is greater than 35 points, that option is **invalid for trading**.

No trade should be taken on that option for the day.

### Boundary Conditions
- Exactly 10 points → ✅ Valid
- Exactly 35 points → ✅ Valid
- Below 10 points → ❌ Invalid
- Above 35 points → ❌ Invalid

**The filter is calculated independently for CE and PE.**

---

## 5. CALL Trade Rules

After the first 1-minute Call candle closes and the Call passes the premium-range filter:

### Entry
Buy the ATM Call when:
```
ATM Call First 1-Minute High is broken
```

### Stop Loss
```
SL = ATM Call First 1-Minute Low
```

### Target
```
TP = Entry Price + 15 option points
```

### Example
Suppose:
- CE first candle High = ₹180
- CE first candle Low = ₹165
- First candle range = 15 points

The range is between 10 and 35 points, so the setup is **valid**.

If CE breaks ₹180:
- Buy CE
- SL = ₹165
- TP = Entry + ₹15

If entry is ₹181:
- SL = ₹165
- TP = ₹196

---

## 6. PUT Trade Rules

After the first 1-minute Put candle closes and the Put passes the premium-range filter:

### Entry
Buy the ATM Put when:
```
ATM Put First 1-Minute High is broken
```

### Stop Loss
```
SL = ATM Put First 1-Minute Low
```

### Target
```
TP = Entry Price + 15 option points
```

### Example
Suppose:
- PE first candle High = ₹170
- PE first candle Low = ₹155
- First candle range = 15 points

The range is between 10 and 35 points, so the setup is **valid**.

If PE breaks ₹170:
- Buy PE
- SL = ₹155
- TP = Entry + ₹15

If entry is ₹171:
- SL = ₹155
- TP = ₹186

---

## 7. Re-Entry Rules

A maximum of **1 re-entry** is allowed separately for the Call side and Put side.

This means:
- CE gets 1 initial entry + 1 re-entry maximum
- PE gets 1 initial entry + 1 re-entry maximum

**The re-entry is available only after the previous trade on that same side has been stopped out.**

### Call Re-Entry
1. CE first-candle High is broken.
2. Buy CE.
3. The trade does not reach the +15 point target.
4. CE hits the first-candle Low stop loss.
5. After the SL, continue monitoring the same CE first-candle High.
6. If the CE High breaks again, take one re-entry.
7. The re-entry uses:
   - Entry = second breakout price
   - SL = original first-candle Low
   - TP = re-entry price + 15 points

**After this re-entry is used, no further CE entries are allowed that day.**

### Put Re-Entry
1. PE first-candle High is broken.
2. Buy PE.
3. The trade does not reach the +15 point target.
4. PE hits the first-candle Low stop loss.
5. Continue monitoring the same PE first-candle High.
6. If the PE High breaks again, take one re-entry.
7. The re-entry uses:
   - Entry = second breakout price
   - SL = original first-candle Low
   - TP = re-entry price + 15 points

**After this re-entry is used, no further PE entries are allowed that day.**

---

## 8. Re-Entry Does Not Reset the First-Candle Levels

For both CE and PE:
- The original first-candle High remains the breakout level.
- The original first-candle Low remains the stop-loss level.
- The +15 point target is calculated from the new re-entry price.

**The first-candle High/Low are not recalculated after the first trade.**

---

## 9. Re-Entry Trigger Example

### CE Example

First candle:
- High = ₹180
- Low = ₹165
- Range = 15 points

First breakout:
- CE breaks ₹180
- Entry = ₹181
- SL = ₹165
- TP = ₹196

Suppose CE falls and hits ₹165.

The initial CE trade is stopped out.

The strategy continues watching ₹180.

Later:
- CE breaks ₹180 again
- Re-entry = ₹181
- SL = ₹165
- TP = ₹196

This is the one allowed CE re-entry.

**If the second CE trade also hits SL, no further CE trade is allowed.**

---

## 10. Important Re-Entry Condition

A re-entry is allowed only when the previous trade on that same side was **stopped out**.

### If Target Is Hit

If the first CE trade reaches its target:
- ✅ CE re-entry is **not allowed**.

If the first PE trade reaches its target:
- ✅ PE re-entry is **not allowed**.

The re-entry is specifically intended for a failed breakout where the original first-candle Low SL is hit and the original High breaks again.

---

## 11. Call and Put Side Independence

CE and PE setups are tracked **independently**.

### Example:

**Scenario 1**
- CE breaks High → CE trade
- CE hits SL
- CE High breaks again → CE re-entry

CE has now used its re-entry.

**Scenario 2**

Later, PE gives a valid breakout.

If the daily trade/risk limits permit it:
- PE trade can be taken.
- PE still has its own separate re-entry available.

Therefore: **CE re-entry count and PE re-entry count are independent.**

---

## 12. Maximum Trade Rules

The strategy allows a maximum of **2 initial/regular trade entries per day**, subject to the risk and daily-loss limits.

Re-entries are treated as additional entries and must also comply with the overall daily trade/risk controls.

The implementation should track:
- CE initial entry count
- CE re-entry count
- PE initial entry count
- PE re-entry count
- Total entries for the day
- Open position status
- Daily realized P&L

**No new position may be opened while another position is already open.**

---

## 13. Position Size

Each trade uses: **1 lot**

The actual quantity should use the applicable Nifty option lot size for the relevant historical date.

For example, if the applicable lot size is 50:
```
1 lot = 50 option units
```

Historical backtests should use the correct lot size applicable on each date rather than assuming one permanent lot size.

---

## 14. Capital and Risk Management

**Starting capital**: ₹1,00,000

### Maximum Risk Per Trade
```
Maximum risk = 5% of current trading capital
```

### Maximum Daily Loss
```
Maximum daily loss = 10% of current trading capital
```

The limits must be recalculated using the current capital.

| Current Capital | Max Risk / Trade (5%) | Max Daily Loss (10%) |
|-----------------|----------------------|---------------------|
| ₹1,00,000 | ₹5,000 | ₹10,000 |
| ₹1,20,000 | ₹6,000 | ₹12,000 |
| ₹1,50,000 | ₹7,500 | ₹15,000 |
| ₹2,00,000 | ₹10,000 | ₹20,000 |

---

## 15. Position/Risk Calculation

Before every entry, including a re-entry:

```
Risk per unit = Entry Price − Stop Loss Price
Total Trade Risk = Risk per unit × Quantity
```

The trade may only be taken if the calculated risk is within the allowed 5% of current capital.

The same risk rule applies to:
- Initial CE entry
- CE re-entry
- Initial PE entry
- PE re-entry

**If 1 lot exceeds the permitted risk, the trade should be skipped rather than increasing the risk limit.**

---

## 16. Daily Loss Limit

At the beginning of each trading day:
```
Daily Loss Limit = 10% × Current Capital
```

Once cumulative realized losses reach the daily loss limit:

**Stop taking new trades immediately.**

This includes both normal entries and re-entries.

No additional trade should be opened after the daily loss limit is reached.

---

## 17. Target and Stop Loss

### CE
- Entry = CE first-candle High breakout
- SL = CE first-candle Low
- TP = Entry + 15 points

### PE
- Entry = PE first-candle High breakout
- SL = PE first-candle Low
- TP = Entry + 15 points

**The stop loss remains based on the original first candle for both the initial entry and any permitted re-entry.**

---

## 18. Trading Checklist

### Before Trading
- ☐ Nifty market has opened.
- ☐ ATM strike identified at the start of the first minute.
- ☐ ATM CE and PE selected.
- ☐ First 1-minute candle has closed.
- ☐ CE High/Low recorded.
- ☐ PE High/Low recorded.
- ☐ CE first-candle range checked.
- ☐ PE first-candle range checked.
- ☐ Each valid option has a first-candle range between 10 and 35 points.

### Before Entry
- ☐ Valid CE/PE High breakout confirmed.
- ☐ Correct ATM option selected.
- ☐ Position size = 1 lot.
- ☐ Risk ≤ 5% of current capital.
- ☐ Daily loss < 10% of current capital.
- ☐ Daily trade limit has not been reached.
- ☐ No other position is open.
- ☐ SL placed immediately.
- ☐ TP = +15 option points.

### Before Re-Entry
- ☐ Previous trade on the same side hit SL.
- ☐ Previous trade did not hit target.
- ☐ Re-entry for that side has not already been used.
- ☐ Original first-candle High is broken again.
- ☐ Original first-candle Low remains the SL.
- ☐ Risk ≤ 5% of current capital.
- ☐ Daily loss limit has not been reached.
- ☐ No other position is open.

---

## 19. Strategy Summary

### CALL
```
Valid CE first candle (10–35 points) → CE High Break → BUY CE
```

- **Entry**: CE first-candle High breakout
- **SL**: CE first-candle Low
- **TP**: +15 option points
- **Position**: 1 lot
- **Re-entry**: Maximum 1 after SL
- **Re-entry trigger**: Same original CE High breaks again

### PUT
```
Valid PE first candle (10–35 points) → PE High Break → BUY PE
```

- **Entry**: PE first-candle High breakout
- **SL**: PE first-candle Low
- **TP**: +15 option points
- **Position**: 1 lot
- **Re-entry**: Maximum 1 after SL
- **Re-entry trigger**: Same original PE High breaks again

---

## 20. Backtesting Requirements

A proper backtest should use actual historical Nifty option 1-minute OHLC data and account for:

- Nifty spot price at market open
- ATM strike selection at the start of the first minute
- Historical ATM CE data
- Historical ATM PE data
- First-minute CE High/Low
- First-minute PE High/Low
- First-minute CE range filter
- First-minute PE range filter
- CE breakout timing
- PE breakout timing
- Initial entry
- Stop loss
- 15-point target
- CE re-entry
- PE re-entry
- Maximum one re-entry per side
- 1-lot position size
- Dynamic 5% risk limit
- Dynamic 10% daily loss limit
- Maximum daily entries/trades
- One open position at a time
- Brokerage and applicable charges
- Slippage
- Correct historical option lot size

---

## 21. Important Backtesting Note

Because the strategy uses the **option's own first 1-minute candle**, it cannot be accurately backtested using only the Nifty spot chart.

The backtest needs **historical Nifty option 1-minute OHLC data** for the relevant ATM CE and PE strikes.

This is required to correctly reproduce:
- First-candle option High
- First-candle option Low
- 10–35 point range filter
- Option High breakout
- Option stop loss
- Option target
- Re-entry breakout
- Actual option premium movement

---

## 22. Risk Disclaimer

**This strategy does not guarantee profits.**

Option premiums can move rapidly, and actual execution can differ from theoretical backtest prices because of:

- Slippage
- Bid/ask spread
- Liquidity
- Fast market movement
- Order execution delays
- Brokerage and taxes
- Data quality

**The strategy should be thoroughly tested on reliable historical option data and preferably paper-traded before using real capital.**
