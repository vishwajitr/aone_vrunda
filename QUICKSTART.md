# OpenAlgo Quick Start Guide

## 🚀 Setup Status: COMPLETE ✅

Your OpenAlgo installation is configured and ready to use!

---

## 📋 What's Been Done

✅ **Python Dependencies** - All packages installed  
✅ **Security Keys** - Generated and configured  
✅ **Databases** - Initialized and migrated  
✅ **Application** - Ready to start  

---

## 🔧 Before You Start: Configure Your Broker

You **MUST** configure your broker before starting OpenAlgo.

### Option 1: Use the Configuration Helper Script (Recommended)

```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo
./configure_broker.sh
```

The script will:
1. Ask for your broker name (e.g., zerodha, angel, fyers)
2. Request your API credentials
3. Update your `.env` file automatically

### Option 2: Manual Configuration

Open `.env` file and update these lines:

```ini
# Change <broker> to your broker name (lowercase)
REDIRECT_URL = 'http://127.0.0.1:5000/<broker>/callback'

# Add your broker credentials
BROKER_API_KEY = 'your_api_key_here'
BROKER_API_SECRET = 'your_api_secret_here'
```

**Example for Zerodha:**
```ini
REDIRECT_URL = 'http://127.0.0.1:5000/zerodha/callback'
BROKER_API_KEY = 'xyz123abc456'
BROKER_API_SECRET = 'def789ghi012'
```

---

## 🎯 Starting OpenAlgo

Once broker is configured:

```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo
uv run app.py
```

You should see:
```
Starting OpenAlgo...
* Running on http://127.0.0.1:5000
```

---

## 🌐 First-Time Access

1. **Open your browser** and go to: http://127.0.0.1:5000

2. **Create Admin Account** (first time only):
   - Username: your_username
   - Email: your_email@example.com
   - Password: Strong@Password123

3. **Login to Broker**:
   - Click "Connect Broker"
   - You'll be redirected to your broker's login page
   - Authorize OpenAlgo
   - You'll be redirected back to OpenAlgo dashboard

4. **Generate API Key** (for webhooks):
   - Go to API Key section
   - Click "Generate New Key"
   - Copy and save this key securely

---

## 📖 Supported Brokers

OpenAlgo supports 40+ brokers including:

| Popular Brokers | API Portal |
|----------------|-----------|
| **Zerodha** | https://kite.trade |
| **Angel One** | https://smartapi.angelbroking.com |
| **Fyers** | https://myapi.fyers.in |
| **Upstox** | https://api.upstox.com |
| **Dhan** | https://api.dhan.co |
| **Flattrade** | Contact your broker |
| **Shoonya** | https://shoonya.finvasia.com |
| **ICICI Direct** | Contact your broker |

For XTS-based brokers (fivepaisaxts, compositedge, ibulls, etc.), you'll also need:
```ini
BROKER_API_KEY_MARKET = 'your_market_api_key'
BROKER_API_SECRET_MARKET = 'your_market_api_secret'
```

---

## 🛠️ Common Commands

### Start OpenAlgo
```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo
uv run app.py
```

### Stop OpenAlgo
Press `Ctrl + C` in the terminal

### View Logs (in another terminal)
```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo
tail -f log/*.log
```

### Reset Admin Password (if forgotten)
```bash
cd /Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo
uv run python upgrade/reset_admin_password.py
```

---

## 📁 Important Directories

```
openalgo/
├── .env                    # Configuration (KEEP SECRET!)
├── db/                     # Databases
├── workspace/              # Your strategies
│   ├── indicators/         # Custom indicators
│   ├── backtests/          # Backtest results
│   └── research/           # Research notes
├── log/                    # Application logs
└── docs/                   # Documentation
```

---

## 🔐 Security Checklist

- [ ] Never share your `.env` file
- [ ] Use strong admin password
- [ ] Enable Two-Factor Authentication (Settings → Security)
- [ ] Keep broker API credentials secure
- [ ] Regularly backup your `db/` directory
- [ ] Use HTTPS in production (not http://127.0.0.1)

---

## 📚 Next Steps

### Learn OpenAlgo
1. **Dashboard Overview**: `docs/userguide/07-dashboard-overview/README.md`
2. **Understanding Interface**: `docs/userguide/08-understanding-interface/README.md`
3. **Placing Orders**: `docs/userguide/10-placing-first-order/README.md`

### Test Before Real Trading
- **Analyzer Mode**: Test strategies with virtual money
  - Go to Settings → Enable Analyzer Mode
  - Place test orders without real money

### Integrate with Trading Platforms
- **TradingView**: `docs/userguide/16-tradingview-integration/README.md`
- **Amibroker**: `docs/userguide/17-amibroker-integration/README.md`
- **ChartInk**: `docs/userguide/18-chartink-integration/README.md`

### Build Strategies
- **Python Strategies**: `docs/userguide/20-python-strategies/README.md`
- **Flow Builder**: `docs/userguide/21-flow-visual-builder/README.md`

---

## ❓ Troubleshooting

### "Default REDIRECT_URL detected" Error
**Solution**: Configure your broker using `./configure_broker.sh` or manually edit `.env`

### "Invalid API credentials" Error
**Solution**: 
1. Verify credentials in your broker's developer portal
2. Check for typos in `.env` file
3. Ensure no extra spaces in credentials

### Application won't start
**Solution**:
```bash
# Check logs
cat log/*.log

# Verify environment
uv run python -c "from utils.env_check import load_and_check_env_variables; load_and_check_env_variables()"
```

### Broker login fails
**Solution**:
1. Ensure broker API is activated in broker portal
2. Check if REDIRECT_URL matches broker settings
3. Try logging into broker's website directly first

---

## 🆘 Get Help

- **Documentation**: `docs/userguide/README.md`
- **Troubleshooting**: `docs/userguide/29-troubleshooting/README.md`
- **FAQs**: `docs/userguide/30-faqs/README.md`
- **Discord**: https://www.openalgo.in/discord
- **GitHub Issues**: https://github.com/marketcalls/openalgo/issues

---

## 🎉 You're Ready!

Configure your broker and start OpenAlgo to begin trading!

```bash
./configure_broker.sh
uv run app.py
```

Then open: **http://127.0.0.1:5000**

---

**Setup completed**: September 4, 2026  
**Installation path**: `/Applications/MAMP/htdocs/htdocs/VishwajitWeb/opencodenew/openalgo`
