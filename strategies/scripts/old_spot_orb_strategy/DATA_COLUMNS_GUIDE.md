# 📊 Data Columns Guide - Nifty ORB Strategy

## 📥 INPUT Data Columns (What You Need to Provide)

### Required CSV Format for Backtesting

Your input CSV file must have **exactly these 6 columns**:

```csv
datetime,open,high,low,close,volume
```

### Column Details:

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| **datetime** | Date and time of candle | `2024-01-01 09:15:00` | ✅ YES |
| **open** | Opening price | `21737.85` | ✅ YES |
| **high** | Highest price | `21745.30` | ✅ YES |
| **low** | Lowest price | `21730.15` | ✅ YES |
| **close** | Closing price | `21740.25` | ✅ YES |
| **volume** | Trading volume | `1500000` | ⚠️ Optional* |

*Volume is optional for the strategy logic but good to have for data validation.

---

### Complete Example Input CSV:

```csv
datetime,open,high,low,close,volume
2024-01-01 09:15:00,21737.85,21745.30,21730.15,21740.25,1500000
2024-01-01 09:16:00,21740.25,21748.50,21735.20,21745.10,1200000
2024-01-01 09:17:00,21745.10,21752.60,21740.80,21750.35,1100000
2024-01-01 09:18:00,21750.35,21755.20,21748.90,21753.80,950000
```

---

### Important Input Requirements:

1. **DateTime Format:**
   - Format: `YYYY-MM-DD HH:MM:SS`
   - Examples: 
     - ✅ `2024-01-01 09:15:00`
     - ✅ `2024-12-31 15:30:00`
     - ❌ `01-01-2024 09:15` (wrong format)
     - ❌ `2024/01/01 09:15:00` (use dash, not slash)

2. **Time Range:**
   - Must include market hours: **09:15:00 to 15:30:00 IST**
   - First candle: 09:15:00 (essential for ORB calculation)

3. **Price Format:**
   - Decimal numbers
   - Use period (`.`) not comma
   - Example: `21737.85` not `21737,85`

4. **No Missing Data:**
   - All OHLC values must be present
   - No blank cells
   - No NaN or NULL values

5. **Chronological Order:**
   - Data must be sorted by datetime (oldest first)

---

## 📤 OUTPUT Data Columns (What You Get in Results)

After running the backtest, you get `backtest_results.csv` with **10 columns**:

### Output Columns:

```csv
date,direction,entry,exit,orb_range,tp1_hit,tp2_hit,exit_reason,pnl,capital
```

### Column Explanations:

| Column | Description | Example Values | Type |
|--------|-------------|----------------|------|
| **date** | Trade entry date | `2025-01-01` | Date |
| **direction** | Trade type | `CALL` or `PUT` | Text |
| **entry** | Nifty price at entry | `22782.52` | Decimal |
| **exit** | Nifty price at exit | `22758.59` | Decimal |
| **orb_range** | First candle range (High-Low) | `13.64` | Decimal |
| **tp1_hit** | Did TP1 get hit? | `True` or `False` | Boolean |
| **tp2_hit** | Did TP2 get hit? | `True` or `False` | Boolean |
| **exit_reason** | Why trade closed | `SL`, `TP1`, `TP2`, `BREAKEVEN`, `TRAILING`, `EOD` | Text |
| **pnl** | Profit/Loss in ₹ | `+1500.00` or `-2000.00` | Decimal |
| **capital** | Capital after trade | `98500.00` | Decimal |

---

### Understanding Output Columns:

#### 1. **date**
- The date when the trade was entered
- Format: `YYYY-MM-DD`

#### 2. **direction**
- `CALL` = Bullish breakout above ORB High
- `PUT` = Bearish breakout below ORB Low

#### 3. **entry**
- Nifty spot price when breakout occurred
- Used to calculate ATM strike

#### 4. **exit**
- Nifty spot price when trade was closed
- Can be at SL, TP1, TP2, or trailing stop

#### 5. **orb_range**
- First candle range = High - Low
- Used for classification:
  - ≤30 points = Small range
  - >30 points = Large range

#### 6. **tp1_hit**
- `True` = Price reached 1R profit (50% exit)
- `False` = Hit stop loss before TP1

#### 7. **tp2_hit**
- `True` = Price reached 2R profit (25% exit)
- `False` = Did not reach TP2
- Only possible if `tp1_hit = True`

#### 8. **exit_reason**
Possible values:
- **SL** = Stop Loss hit (initial SL at opposite ORB level)
- **BREAKEVEN** = Breakeven SL hit (after TP1)
- **TRAILING** = Trailing stop hit (after TP2)
- **EOD** = End of Day closure
- **TP1** / **TP2** = Target hit (rare, usually continues to trail)

#### 9. **pnl**
- Profit/Loss in ₹ (Indian Rupees)
- Positive = Profit
- Negative = Loss
- Already includes transaction costs (~₹200 per trade)

#### 10. **capital**
- Running capital after this trade
- Starts at ₹1,00,000 (default)
- Updates after each trade

---

## 📊 Example Output Analysis

### Example Row:
```csv
2025-01-08,PUT,23253.28,23253.28,10.26,True,True,BREAKEVEN,-200.0,87065.63
```

**What this means:**
- **Date:** Jan 8, 2025
- **Trade:** PUT (bearish breakout)
- **Entry:** 23,253.28
- **Exit:** 23,253.28 (same as entry)
- **ORB Range:** 10.26 points (small range ≤30)
- **TP1 Hit:** Yes ✅ (exited 2 lots at profit)
- **TP2 Hit:** Yes ✅ (exited 1 lot at profit)
- **Exit:** BREAKEVEN (remaining position closed at entry price)
- **P&L:** -₹200 (transaction cost only, no gain/loss)
- **Capital:** ₹87,065.63 remaining

**Trade Flow:**
1. PUT entry at 23,253.28
2. Price moved down, hit TP1 → Exit 2 lots (profit)
3. Price continued down, hit TP2 → Exit 1 lot (profit)
4. Price came back up to entry level → Breakeven exit
5. Net result: Small profit from TP1/TP2 exits minus costs = -₹200

---

## 🎯 What You Need vs What You Get

### INPUT (What you provide):
```
Your Data File (nifty_data.csv)
────────────────────────────────
✓ datetime - Time series
✓ open - Candle open price
✓ high - Candle high price  
✓ low - Candle low price
✓ close - Candle close price
✓ volume - Trading volume
```

### PROCESS (What the backtest does):
```
Backtest Engine
───────────────
• Reads your data
• Identifies first candle (09:15-09:16)
• Calculates ORB levels
• Detects breakouts
• Simulates trades
• Manages TP1, TP2, trailing
• Tracks P&L
```

### OUTPUT (What you receive):
```
backtest_results.csv
────────────────────
✓ date - When traded
✓ direction - CALL/PUT
✓ entry - Entry price
✓ exit - Exit price
✓ orb_range - First candle range
✓ tp1_hit - TP1 reached?
✓ tp2_hit - TP2 reached?
✓ exit_reason - Why closed
✓ pnl - Profit/Loss
✓ capital - Running capital
```

---

## 📈 Analyzing Your Results

### Questions You Can Answer:

#### 1. Win Rate by ORB Range
```python
import pandas as pd
df = pd.read_csv('backtest_results.csv')

small_range = df[df['orb_range'] <= 30]
large_range = df[df['orb_range'] > 30]

print(f"Small Range Win Rate: {(small_range['pnl'] > 0).mean()*100:.1f}%")
print(f"Large Range Win Rate: {(large_range['pnl'] > 0).mean()*100:.1f}%")
```

#### 2. CALL vs PUT Performance
```python
calls = df[df['direction'] == 'CALL']
puts = df[df['direction'] == 'PUT']

print(f"CALL Avg P&L: ₹{calls['pnl'].mean():.0f}")
print(f"PUT Avg P&L: ₹{puts['pnl'].mean():.0f}")
```

#### 3. TP Hit Rates
```python
print(f"TP1 Hit Rate: {df['tp1_hit'].mean()*100:.1f}%")
print(f"TP2 Hit Rate: {df['tp2_hit'].mean()*100:.1f}%")
```

#### 4. Exit Reason Distribution
```python
print(df['exit_reason'].value_counts())
```

---

## ✅ Quick Checklist

### Before Running Backtest:
- [ ] CSV has correct column names
- [ ] DateTime format is YYYY-MM-DD HH:MM:SS
- [ ] Price values use period (.) for decimals
- [ ] Data covers market hours (09:15-15:30)
- [ ] No missing values
- [ ] Data is sorted chronologically

### After Running Backtest:
- [ ] Check backtest_results.csv exists
- [ ] Verify number of trades makes sense
- [ ] Review win rate
- [ ] Analyze TP hit rates
- [ ] Check by ORB range
- [ ] Compare CALL vs PUT
- [ ] Review exit reasons

---

## 🔧 Common Issues

### Issue: "Column not found"
**Solution:** Ensure CSV has exact headers:
```csv
datetime,open,high,low,close,volume
```

### Issue: "DateTime parsing error"
**Solution:** Use correct format:
```python
# Convert dates
df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
```

### Issue: "No trades executed"
**Solution:** 
- Check if data includes 09:15:00 (first candle)
- Verify breakout buffer isn't too large
- Check if price data is valid

---

## 📝 Summary

### MINIMUM REQUIRED INPUT:
```
6 columns: datetime, open, high, low, close, volume
Format: CSV
Time range: 09:15:00 - 15:30:00 IST
Frequency: 1-minute candles
```

### YOU RECEIVE AS OUTPUT:
```
10 columns with trade details
CSV format for easy analysis
Complete P&L tracking
TP hit analysis
Exit reason tracking
```

---

**Your input data should look exactly like the format shown in the INPUT section above!** 📊

**Your output data (which you already have) contains everything you need to analyze strategy performance!** 🎯
