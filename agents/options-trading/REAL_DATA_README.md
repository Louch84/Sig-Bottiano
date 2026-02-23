# Real Market Data Integration

Live earnings, unusual flow, short interest, and real-time quotes for the Options Trading Agent.

## 🚀 Quick Start

```bash
cd /Users/sigbotti/.openclaw/workspace/agents/options-trading

# Setup API keys (interactive)
./setup_real_data.sh

# Or manually copy and edit:
cp data/.env.example data/.env
# Edit data/.env with your actual API keys

# Test connections
python3 test_real_data.py

# Generate real watchlist
python3 real_watchlist.py
```

## 📡 Supported Data Sources

### Free Tier (Recommended)

| Provider | Free Tier | Best For | Get Key |
|----------|-----------|----------|---------|
| **Finnhub** | 60 calls/min | Earnings, fundamentals | [finnhub.io](https://finnhub.io) |
| **Alpha Vantage** | 25 calls/day | Stock quotes, historical | [alphavantage.co](https://www.alphavantage.co) |
| **Yahoo Finance** | Unlimited | Fallback quotes, short interest | No key needed |

### Premium (Better Real-Time)

| Provider | Cost | Best For | Get Key |
|----------|------|----------|---------|
| **Polygon** | $49/mo | Real-time quotes, options chains | [polygon.io](https://polygon.io) |
| **Unusual Whales** | $79/mo | Options flow, dark pool | [unusualwhales.com](https://unusualwhales.com) |
| **Benzinga** | $99/mo | News, earnings calendar | [benzinga.com](https://benzinga.com) |

## 🔧 Configuration

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Options Trading Agent - API Keys
export FINNHUB_API_KEY="your_actual_key_here"
export ALPHA_VANTAGE_API_KEY="your_actual_key_here"
export POLYGON_API_KEY="your_actual_key_here"
```

Or use the `.env` file in `data/.env`:

```bash
FINNHUB_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

## 📊 What You Get

### Real-Time Data
- ✅ Live stock prices (no more simulated data)
- ✅ Actual earnings dates and expected moves
- ✅ Real short interest percentages
- ✅ Unusual options volume detection
- ✅ Sector momentum tracking

### Scoring System
Each stock is scored based on:

| Catalyst | Points | Data Source |
|----------|--------|-------------|
| Earnings (≤2 days) | +40 | Finnhub/Alpha Vantage |
| Earnings (3-5 days) | +25 | Finnhub/Alpha Vantage |
| Short Interest >25% | +35 | Yahoo Finance |
| Short Interest 15-25% | +20 | Yahoo Finance |
| Unusual Flow >3x OI | +30 | Yahoo/Unusual Whales |
| Volume Spike >1.5x | +10 | Real-time quote |
| Price Move >3% | +15 | Real-time quote |

**Minimum score to make watchlist: 30/100**

## 🎯 Usage

### Generate Live Watchlist

```bash
python3 real_watchlist.py
```

Output includes:
- Real prices from market data
- Actual upcoming earnings
- Live short interest data
- Detected unusual flow
- Risk:Reward calculations

### Test Your APIs

```bash
python3 test_real_data.py
```

Tests all configured APIs and shows:
- Connection status
- Quote accuracy
- Data freshness
- API rate limits

## 🔄 Data Flow

```
┌─────────────────┐
│ Your Watchlist  │
│   (under $50)   │
└────────┬────────┘
         │
    ┌────▼────┐
    │  APIs   │ ←── Finnhub (earnings)
    │         │ ←── Alpha Vantage (quotes)
    │         │ ←── Yahoo (short interest)
    └────┬────┘
         │
    ┌────▼──────────┐
    │ Data Manager  │ ←── Combines all sources
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │   Scoring     │ ←── Calculates catalyst scores
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │   Watchlist   │ ←── Top 10 setups
    └───────────────┘
```

## 📈 Example Output

```
📊 REAL CATALYST WATCHLIST - Monday, February 24
LIVE DATA | UNDER $50 ONLY

🚀 SHORT SQUEEZE SETUPS
---------------------------------------------------------------------------

🟢 GME @ $25.40 | Score: 89/100
   Data Source: yahoo
   Direction: CALL | Confidence: HIGH
   Trigger: High short interest: 41.2%. Break above $25.65
   Stop: $24.38 | Target: $28.45 | R:R = 1:3.0
   Live Catalysts:
      🔥 High short interest: 41.2%
      🔥 Unusual bullish flow (344% of avg OI)
      ⚡ Strong bullish move: +5.2%

📈 Earnings Play Setups
---------------------------------------------------------------------------

🟢 MARA @ $24.30 | Score: 82/100
   Data Source: finnhub
   Direction: CALL | Confidence: HIGH
   Trigger: Earnings in 1 days. Break above $24.54
   Stop: $23.33 | Target: $27.22 | R:R = 1:3.0
   Live Catalysts:
      🔥 Earnings in 1 days
      ⚡ Unusual call flow (287% of avg OI)
```

## ⚠️ Rate Limits

### Finnhub (Free)
- 60 calls/minute
- 500 calls/day
- **Recommendation**: Use for earnings + quotes

### Alpha Vantage (Free)
- 25 calls/day
- 5 calls/minute
- **Recommendation**: Use for quotes only

### Combined Usage
With both free APIs:
- ~85 API calls per watchlist generation
- Can run 5-6 times per day
- Use sparingly during market hours

## 🛠️ Troubleshooting

### "No APIs configured"
```bash
# Check if keys are set
echo $FINNHUB_API_KEY

# If empty, add to ~/.zshrc:
echo 'export FINNHUB_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

### "API rate limit exceeded"
- Wait 1 minute and retry
- Reduce watchlist size in `real_watchlist.py`
- Upgrade to paid tier for higher limits

### "Price data stale"
- Yahoo Finance: 15-20 min delay (normal)
- Finnhub: Real-time for US equities
- Alpha Vantage: Real-time but slower

### "Missing earnings data"
- Some small-cap stocks lack coverage
- System uses Yahoo fallback
- Manually verify earnings dates

## 🔐 Security

Your API keys are stored in `data/.env` which is:
- ✅ Ignored by git (in .gitignore)
- ✅ Never logged or displayed
- ✅ Loaded only at runtime
- ✅ Not included in any exports

**Never commit your .env file!**

## 📚 API Documentation

- [Finnhub Docs](https://finnhub.io/docs/api)
- [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
- [Polygon Docs](https://polygon.io/docs)

## 🎯 Next Steps

1. Get free Finnhub key (2 minutes)
2. Run `./setup_real_data.sh`
3. Test with `python3 test_real_data.py`
4. Generate live watchlist with `python3 real_watchlist.py`
5. Trade with real data 💰

---

**Questions?** Check `test_real_data.py` for debugging help.
