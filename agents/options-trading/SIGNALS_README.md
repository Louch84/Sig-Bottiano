# Options Signals - Quick Reference

Dead simple CALL/PUT signals with day trade vs swing labels.

## 🚀 Quick Start

```bash
cd /Users/sigbotti/.openclaw/workspace/agents/options-trading

# Single scan
python3 signals.py

# Live continuous scanning (every 30 seconds)
python3 live_signals.py
```

## 📊 What You Get

### ⚡ DAY TRADE Signals
- **0-1 DTE** (same day or next day expiration)
- Based on: Volume surges, breakouts, momentum
- Tight stops (0.5-1%)
- Quick targets (1.5-3% moves)
- High confidence only (70%+)

### 📈 SWING Signals  
- **2-30 DTE** (weekly to monthly)
- Based on: Trends, support/resistance, IV crush setups
- Wider stops (2-4%)
- Bigger targets (5%+ moves)
- Moderate confidence (60%+)

## 🎯 Signal Format

```
AAPL | 🟢 CALL | 85% confidence
  Entry: $229.23 | Strike: $231.20 | 1 DTE
  Stop: $227.68 | T1: $232.67 | T2: $236.11
  R:R = 1:4.4
  Unusual volume (154% of avg); Momentum aligned
```

**What it means:**
- Symbol: AAPL
- Direction: CALL (bullish)
- Confidence: 85%
- Entry: $229.23 (current price)
- Strike: $231.20 (OTM call)
- Expires: 1 day
- Stop: $227.68 (1% below entry)
- Target 1: $232.67 (50% gain on option)
- Target 2: $236.11 (100% gain on option)
- Risk:Reward = 1:4.4

## 📋 Watchlist

Default: SPY, QQQ, IWM, AAPL, TSLA, NVDA, AMD, MSFT, AMZN, META, GOOGL, NFLX, CRM

To change: Edit `signals.py` line 29:
```python
self.watchlist = ["SPY", "QQQ", "AAPL", ...]  # Your symbols
```

## 🎮 How It Works

1. Scans each symbol for setups
2. Day trade setups = volume surge OR breakout
3. Swing setups = trend alignment OR support bounce OR IV crush
4. Ranks by confidence (volume + price action)
5. Outputs top signals

## ⚠️ Disclaimer

These are algorithmic signals for educational purposes. Always:
- Do your own analysis
- Use proper risk management
- Never risk more than you can afford to lose
- Paper trade first

**Not financial advice.**

---

Built by Sig Botti | Philly-built 🦞
