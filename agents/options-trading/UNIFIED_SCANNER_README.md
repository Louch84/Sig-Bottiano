# 🔴 Unified Options Scanner

**One scanner, four modes.** Replaces 9 scattered scanners with one cohesive system.

---

## Quick Start

```bash
# Quick scan (5 stocks, 5 seconds)
python unified_scanner.py --mode quick

# Standard scan (full analysis)
python unified_scanner.py --mode standard

# Breakout scanner (F-style 400% plays)
python unified_scanner.py --mode breakout

# Optimized scan (Kelly + Correlation + Regime)
python unified_scanner.py --mode optimized --account-value 25000
```

---

## Modes Explained

### ⚡ QUICK Mode
**Use when:** You need signals NOW (5-10 seconds)

- 5 stocks (AMC, GME, MARA, SOFI, TSLA)
- Basic signals only
- Minimal API calls
- Best for: Quick checks, testing

```bash
python unified_scanner.py --mode quick
```

### 📊 STANDARD Mode (Default)
**Use when:** You want comprehensive analysis (30-60 seconds)

- 24 stock watchlist
- SMC analysis (support/resistance)
- Catalyst detection
- Volume + short interest scoring
- Best for: Daily scanning, general use

```bash
python unified_scanner.py --mode standard
python unified_scanner.py --mode standard --watchlist TSLA,NVDA,AAPL
```

### 🎯 BREAKOUT Mode
**Use when:** Hunting F-style 400% breakout plays

- Consolidation pattern detection
- Resistance proximity analysis
- Coiled spring setups
- Quality scoring (EXCELLENT/GOOD/FAIR)
- Best for: High-conviction breakout trades

```bash
python unified_scanner.py --mode breakout
```

### 🔴 OPTIMIZED Mode
**Use when:** You want institutional-grade risk management

- Kelly position sizing
- Correlation filtering
- Market regime detection (VIX-based)
- Full risk calculations
- Best for: Live trading, portfolio management

```bash
python unified_scanner.py --mode optimized --account-value 25000
```

---

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Scanner mode (quick/standard/breakout/optimized) | `standard` |
| `--watchlist` | Comma-separated symbols (e.g., TSLA,NVDA,AAPL) | Built-in list |
| `--account-value` | Account size for Kelly sizing | `10000` |

---

## Output Format

All modes return signals with consistent fields:

```python
{
    'mode': 'standard',
    'symbol': 'TSLA',
    'price': 245.50,
    'direction': 'CALL',
    'score': 75,
    'confidence': 0.75,
    'change_1d': 3.2,
    'change_5d': 8.5,
    'volume_ratio': 2.5,
    'short_pct': 12.0,
    'catalysts': ['Unusual volume', 'High short interest'],
    'entry': 245.50,
    'stop': 238.00,
    'target_1': 255.00,
    'risk_reward': 2.5
}
```

**Optimized mode adds:**
```python
{
    'kelly': {
        'recommended_pct': 2.5,
        'max_contracts': 10,
        'risk_amount': 250.00
    }
}
```

---

## Architecture

### Shared Data Layer
- **Single yfinance call per symbol** - no duplicate API calls
- **5-minute cache** - prevents redundant fetches
- **Unified data structure** - all modes use same format

### Scanner Classes
```
UnifiedScanner (entry point)
├── QuickScanner
├── StandardScanner
├── BreakoutScanner
└── OptimizedScanner
    ├── KellyPositionSizer (from optimizations.py)
    ├── CorrelationFilter (from optimizations.py)
    └── MarketRegimeDetector (from optimizations.py)
```

---

## What Replaced What

| Old Scanner | New Mode | Notes |
|-------------|----------|-------|
| `quick_scanner.py` | `--mode quick` | Direct replacement |
| `full_scanner.py` | `--mode standard` | Merged + improved |
| `live_scanner.py` | `--mode standard` | Functionality merged |
| `breakout_squeeze_scanner.py` | `--mode breakout` | Direct replacement |
| `optimized_scanner.py` | `--mode optimized` | Direct replacement |
| `scheduled_scanner.py` | Cron + any mode | Use system cron |
| `scanner_alert_integration.py` | Future feature | To be integrated |
| `langgraph_scanner.py` | Keep separate | Different architecture |
| `main.py` | Keep separate | Multi-agent system |

---

## Performance

| Mode | Time (24 stocks) | API Calls | Best For |
|------|------------------|-----------|----------|
| Quick | 5-10 sec | 5 | Fast checks |
| Standard | 30-60 sec | 24 | Daily scanning |
| Breakout | 45-90 sec | 19 | Pattern hunting |
| Optimized | 60-120 sec | 24 + optimizations | Live trading |

---

## Examples

### Daily Morning Scan
```bash
# Quick market pulse
python unified_scanner.py --mode quick

# Full analysis for trading decisions
python unified_scanner.py --mode standard
```

### Hunting Breakout Plays
```bash
# Find F-style setups
python unified_scanner.py --mode breakout

# Custom watchlist
python unified_scanner.py --mode breakout --watchlist F,NOK,T,BAC,KMI
```

### Live Trading (Optimized)
```bash
# Full risk management
python unified_scanner.py --mode optimized --account-value 50000

# Custom watchlist with Kelly sizing
python unified_scanner.py --mode optimized --watchlist TSLA,NVDA,AMD --account-value 25000
```

### Cron Job (Scheduled Scanning)
```bash
# Add to crontab - run every 15 minutes during market hours
*/15 9-16 * * 1-5 cd /Users/sigbotti/.openclaw/workspace/agents/options-trading && python unified_scanner.py --mode standard >> /tmp/scanner.log 2>&1
```

---

## Troubleshooting

### "Optimizations module not found"
```bash
# Make sure optimizations.py is in the same directory
ls -la /Users/sigbotti/.openclaw/workspace/agents/options-trading/optimizations.py
```

### "No signals found"
- Market might be closed
- Watchlist stocks might not meet criteria
- Try `--mode quick` for less strict filtering

### Slow performance
- Use `--mode quick` for faster results
- Reduce watchlist size with `--watchlist`
- Check internet connection (yfinance depends on it)

---

## Future Enhancements

- [ ] Real-time data streaming integration
- [ ] Alert system (Discord/Telegram/SMS)
- [ ] Backtesting module
- [ ] Paper trading integration
- [ ] Machine learning signal enhancement
- [ ] Multi-timeframe analysis
- [ ] Options chain integration (strike selection)

---

**Bottom Line:** One scanner, four modes, zero confusion. Pick your mode and scan.
