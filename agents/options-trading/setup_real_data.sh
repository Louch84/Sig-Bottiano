#!/bin/bash
# Real Data Setup Script
# Configures API keys for live market data

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  REAL DATA API SETUP                                       ║"
echo "║  Options Trading Agent - Live Market Data                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

WORKSPACE="/Users/sigbotti/.openclaw/workspace/agents/options-trading"
cd "$WORKSPACE"

# Check if .env already exists
if [ -f "$WORKSPACE/data/.env" ]; then
    echo "✅ .env file already exists"
    echo "   Current configuration:"
    grep -E "API_KEY" "$WORKSPACE/data/.env" | while read line; do
        if [[ "$line" == *"="* ]]; then
            key=$(echo "$line" | cut -d'=' -f1)
            value=$(echo "$line" | cut -d'=' -f2)
            if [ -n "$value" ] && [ "$value" != "your_"*"_here" ]; then
                echo "     ✅ $key: Set"
            else
                echo "     ❌ $key: Not set"
            fi
        fi
    done
    echo
    read -p "Reconfigure? (y/n): " reconfig
    if [[ ! $reconfig =~ ^[Yy]$ ]]; then
        echo "Keeping existing configuration."
        echo
        echo "Test your setup:"
        echo "  python3 test_real_data.py"
        exit 0
    fi
fi

echo "📝 Setting up API keys..."
echo
echo "I'll help you configure real-time market data."
echo "You can get free API keys from these providers:"
echo
echo "1. Finnhub (RECOMMENDED - Free, 60 calls/min)"
echo "   https://finnhub.io"
echo

read -p "Do you have a Finnhub API key? (y/n): " has_finnhub

if [[ $has_finnhub =~ ^[Yy]$ ]]; then
    read -p "Enter your Finnhub API key: " finnhub_key
else
    echo
    echo "To get a free Finnhub key:"
    echo "  1. Go to https://finnhub.io"
    echo "  2. Click 'Get free api key'"
    echo "  3. Sign up with email"
    echo "  4. Copy your API key from the dashboard"
    echo
    read -p "Press Enter when you have your key (or skip): " finnhub_key
    if [ -z "$finnhub_key" ]; then
        finnhub_key="your_finnhub_key_here"
    fi
fi

echo
echo "2. Alpha Vantage (Free, 25 calls/day)"
echo "   https://www.alphavantage.co"
echo

read -p "Do you have an Alpha Vantage API key? (y/n): " has_alpha

if [[ $has_alpha =~ ^[Yy]$ ]]; then
    read -p "Enter your Alpha Vantage API key: " alpha_key
else
    alpha_key="your_alpha_vantage_key_here"
fi

echo
echo "3. Polygon (Premium - $49/month for real-time)"
echo "   https://polygon.io"
echo

read -p "Do you have a Polygon API key? (y/n): " has_polygon

if [[ $has_polygon =~ ^[Yy]$ ]]; then
    read -p "Enter your Polygon API key: " polygon_key
else
    polygon_key="your_polygon_key_here"
fi

# Create .env file
cat > "$WORKSPACE/data/.env" << EOF
# Data API Configuration
# Generated on $(date)

# 🥇 RECOMMENDED - Finnhub (Free tier: 60 calls/min)
FINNHUB_API_KEY=$finnhub_key

# Alpha Vantage (Free tier: 25 calls/day)
ALPHA_VANTAGE_API_KEY=$alpha_key

# Polygon (Real-time data - Premium)
POLYGON_API_KEY=$polygon_key

# Unusual Whales (Options flow - Premium)
UNUSUAL_WHALES_API_KEY=your_unusual_whales_key_here

# Benzinga (News & earnings - Premium)
BENZINGA_API_KEY=your_benzinga_api_key_here
EOF

echo
echo "✅ Configuration saved to $WORKSPACE/data/.env"
echo

# Export for current session
export FINNHUB_API_KEY="$finnhub_key"
export ALPHA_VANTAGE_API_KEY="$alpha_key"
export POLYGON_API_KEY="$polygon_key"

echo "🧪 Testing connections..."
echo

python3 "$WORKSPACE/test_real_data.py"

echo
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  SETUP COMPLETE                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo
echo "To use real data in your watchlist:"
echo "  python3 real_watchlist.py"
echo
echo "The system will automatically:"
echo "  ✅ Use Finnhub/Alpha Vantage for real-time quotes"
echo "  ✅ Fetch actual earnings dates"
echo "  ✅ Get real short interest data"
echo "  ✅ Detect unusual options volume"
echo "  ✅ Fallback to Yahoo Finance if APIs unavailable"
echo
echo "Your API keys are stored in: $WORKSPACE/data/.env"
echo "(This file is ignored by git for security)"
echo
