#!/bin/bash

# OpenAlgo Broker Configuration Helper
# This script helps you configure your broker credentials

echo "=============================================="
echo "  OpenAlgo Broker Configuration Helper"
echo "=============================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run this script from the openalgo directory."
    exit 1
fi

echo "Supported brokers:"
echo "  fivepaisa, fivepaisaxts, aliceblue, angel, arrow,"
echo "  compositedge, definedge, deltaexchange, dhan, dhan_sandbox,"
echo "  firstock, flattrade, fyers, groww, hdfcsecurities,"
echo "  hdfcsky, ibulls, iifl, iiflcapital, indmoney,"
echo "  jainamxts, kotak, motilal, mstock, nubra, paytm,"
echo "  pocketful, rmoney, samco, shoonya, tradejini,"
echo "  tradesmart, upstox, wisdom, zebu, zerodha"
echo ""

# Ask for broker name
read -p "Enter your broker name (e.g., zerodha, angel, fyers): " BROKER_NAME

if [ -z "$BROKER_NAME" ]; then
    echo "❌ Error: Broker name cannot be empty!"
    exit 1
fi

# Convert to lowercase
BROKER_NAME=$(echo "$BROKER_NAME" | tr '[:upper:]' '[:lower:]')

echo ""
echo "Configuring for broker: $BROKER_NAME"
echo ""

# Update REDIRECT_URL in .env
REDIRECT_URL="http://127.0.0.1:5000/${BROKER_NAME}/callback"

# Use sed to update the REDIRECT_URL
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|^REDIRECT_URL = .*|REDIRECT_URL = '${REDIRECT_URL}'|" .env
else
    # Linux
    sed -i "s|^REDIRECT_URL = .*|REDIRECT_URL = '${REDIRECT_URL}'|" .env
fi

echo "✅ Updated REDIRECT_URL to: $REDIRECT_URL"
echo ""

# Ask for API credentials
read -p "Enter your broker API Key: " BROKER_API_KEY
read -p "Enter your broker API Secret (press Enter if not required): " BROKER_API_SECRET

if [ -z "$BROKER_API_KEY" ]; then
    echo "⚠️  Warning: API Key is empty!"
else
    # Update BROKER_API_KEY
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^BROKER_API_KEY = .*|BROKER_API_KEY = '${BROKER_API_KEY}'|" .env
    else
        sed -i "s|^BROKER_API_KEY = .*|BROKER_API_KEY = '${BROKER_API_KEY}'|" .env
    fi
    echo "✅ Updated BROKER_API_KEY"
fi

if [ ! -z "$BROKER_API_SECRET" ]; then
    # Update BROKER_API_SECRET
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^BROKER_API_SECRET = .*|BROKER_API_SECRET = '${BROKER_API_SECRET}'|" .env
    else
        sed -i "s|^BROKER_API_SECRET = .*|BROKER_API_SECRET = '${BROKER_API_SECRET}'|" .env
    fi
    echo "✅ Updated BROKER_API_SECRET"
fi

echo ""
echo "=============================================="
echo "  Configuration Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Start OpenAlgo: uv run app.py"
echo "2. Open browser: http://127.0.0.1:5000"
echo "3. Create admin account and login"
echo ""
echo "For more details, see: SETUP_COMPLETE.md"
echo ""
