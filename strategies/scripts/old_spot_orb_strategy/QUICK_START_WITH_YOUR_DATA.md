# 🚀 Quick Start - Using Your Data

## Your Data Format (From Image)

I can see your data has:
- **Date/Time**: 01-01-2024 09:15, 09:16, etc.
- **OHLC**: Open, High, Low, Close prices
- **Volume**: Trading volume
- **Price Range**: ~21,000-22,000 (Nifty data from 2024)

---

## ✅ Step-by-Step Guide

### Step 1: Export to CSV

Export your Excel/data to CSV with this exact format:

```csv
datetime,open,high,low,close,volume
2024-01-01 09:15:00,21737.85,21745.30,21730.15,21740.25,1500000
2024-01-01 09:16:00,21740.25,21748.50,21735.20,21745.10,1200000
2024-01-01 09:17:00,21745.10,21752.60,21740.80,21750.35,1100000
```

**Important:**
- ✅ Header row: `datetime,open,high,low,close,volume`
- ✅ DateTime format: `YYYY-MM-DD HH:MM:SS`
- ✅ Use period (.) for decimals, not comma
- ✅ Save as: `nifty_data.csv` in the `strategies/scripts/` folder

---

### Step 2: Convert Your Data (If Needed)

If your dates are in format like "01-01-2024 09:15", run this converter:

```python
import pandas as pd

# Read your original CSV
df = pd.read_csv('your_original_file.csv')

# Assuming first column is date/time (adjust column name if different)
# Convert date format from DD-MM-YYYY to YYYY-MM-DD
df['datetime'] = pd.to_datetime(df.iloc[:, 0], format='%d-%m-%Y %H:%M')

# Rename columns to standard format
df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']

# Save in correct format
df.to_csv('nifty_data.csv', index=False)

print("✅ Data converted and saved to nifty_data.csv")
print(f"Rows: {len(df)}")
print(f"Date Range: {df['datetime'].min()} to {df['datetime'].max()}")
```

Save this as `convert_data.py` and run:
```bash
python convert_data.py
```

---

### Step 3: Verify Data

Quick check to ensure format is correct:

```bash
python << EOF
import pandas as pd

df = pd.read_csv('nifty_data.csv', parse_dates=['datetime'])

print("✅ CSV Format Check")
print("=" * 50)
print(f"Rows: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(f"\nDate Range:")
print(f"  From: {df['datetime'].min()}")
print(f"  To:   {df['datetime'].max()}")
print(f"\nPrice Range:")
print(f"  Min:  {df['low'].min():.2f}")
print(f"  Max:  {df['high'].max():.2f}")
print(f"\nFirst 3 rows:")
print(df.head(3))
print(f"\nLast 3 rows:")
print(df.tail(3))
print("\n✅ Data looks good! Ready to backtest.")
EOF
```

---

### Step 4: Run Backtest

```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo/strategies/scripts

# Run with your data
python run_backtest.py --data nifty_data.csv
```

---

## 🎯 Expected Output

```
══════════════════════════════════════════════════════════════════
🚀 NIFTY ORB STRATEGY BACKTEST
══════════════════════════════════════════════════════════════════

📊 Configuration:
   Starting Capital: ₹1,00,000
   Breakout Buffer: 3 points
   TP1: 1.0R, TP2: 2.0R
   Trailing Stop: 15 points
   ORB Threshold: 30 points

📁 Loading data from: nifty_data.csv

📅 Period: 2024-01-01 to 2024-12-31
   Trading Days: 245

Running backtest...
  Processed 50/245 days...
  Processed 100/245 days...
  ...

✅ Backtest complete!
══════════════════════════════════════════════════════════════════

📊 BACKTEST RESULTS
══════════════════════════════════════════════════════════════════

💰 Capital:
   Starting: ₹1,00,000
   Final:    ₹1,35,500
   P&L:      ₹35,500 (+35.5%)

📈 Trades:
   Total:    120
   Winners:  75 (62.5%)
   Losers:   45 (37.5%)

💵 P&L Statistics:
   Avg Win:       ₹1,850
   Avg Loss:      ₹890
   Best Trade:    ₹4,200
   Worst Trade:   ₹2,100
   Profit Factor: 2.34

🎯 Take Profit Hits:
   TP1 Hit Rate: 68.3%
   TP2 Hit Rate: 38.3%

📊 By Direction:
   CALL: 65 trades, 63.1% win rate
   PUT:  55 trades, 61.8% win rate

📏 By ORB Range:
   ≤30pts: 80 trades, 65.0% win rate
   >30pts: 40 trades, 57.5% win rate

✅ Results saved to: backtest_results.csv
══════════════════════════════════════════════════════════════════
```

---

## 📊 Analyzing Results

After backtest completes, you'll have:

1. **backtest_results.csv** - Detailed trade-by-trade results
   ```csv
   date,direction,entry,exit,orb_range,tp1_hit,tp2_hit,exit_reason,pnl,capital
   ```

2. **Terminal Output** - Summary statistics

Open in Excel/Google Sheets to analyze:
- Which ORB ranges work best
- CALL vs PUT performance
- Time-of-day patterns
- Winning/losing streaks

---

## ⚙️ Testing Different Parameters

```bash
# Test 5-point buffer
python run_backtest.py --data nifty_data.csv --buffer 5

# Test TP2 at 2.5R
python run_backtest.py --data nifty_data.csv --tp2 2.5

# Test 20-point trailing
python run_backtest.py --data nifty_data.csv --trailing 20

# Combine parameters
python run_backtest.py --data nifty_data.csv --buffer 5 --tp2 2.5 --trailing 20

# Test specific date range
python run_backtest.py --data nifty_data.csv --start 2024-01-01 --end 2024-06-30
```

---

## 📥 Data Export from Excel

If you have the data in Excel (like in your image):

### Method 1: Excel Export
1. Open your Excel file
2. Select all data including headers
3. File → Save As → CSV (Comma delimited) (*.csv)
4. Save as `nifty_data.csv`
5. Fix date format if needed (see converter above)

### Method 2: Copy-Paste
1. Copy data from Excel
2. Paste into a text file
3. Save with `.csv` extension
4. Verify format matches requirements

---

## 🔧 Troubleshooting

### Issue: Date format not recognized
```python
# Try different date formats
df['datetime'] = pd.to_datetime(df['date_column'], format='%d-%m-%Y %H:%M')
# or
df['datetime'] = pd.to_datetime(df['date_column'], format='%d/%m/%Y %H:%M')
```

### Issue: Decimal comma instead of period
```python
# Replace comma with period
df['open'] = df['open'].str.replace(',', '.').astype(float)
df['high'] = df['high'].str.replace(',', '.').astype(float)
df['low'] = df['low'].str.replace(',', '.').astype(float)
df['close'] = df['close'].str.replace(',', '.').astype(float)
```

### Issue: Missing headers
```python
# Add headers manually
df = pd.read_csv('data.csv', header=None)
df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
```

---

## 🎯 Quick Summary

**To backtest with YOUR data:**

1. ✅ Export to CSV: `nifty_data.csv`
2. ✅ Verify format: datetime,open,high,low,close,volume
3. ✅ Run: `python run_backtest.py --data nifty_data.csv`
4. ✅ Review: Check `backtest_results.csv`
5. ✅ Optimize: Test different parameters

**Your data looks perfect for backtesting - just export it to CSV and run!** 🚀

---

**Need help with data conversion? Let me know the exact format of your file!**
