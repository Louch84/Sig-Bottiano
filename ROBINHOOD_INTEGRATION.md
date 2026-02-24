# 📈 Robinhood Integration Guide

## What I Can Do

**✅ I CAN:**
- Track your trades manually (you tell me, I record)
- Analyze your performance
- Compare your results to scanner signals
- Alert you when to enter/exit based on your rules
- Calculate P&L and win rates

**❌ I CANNOT:**
- Execute trades directly on Robinhood
- Access your Robinhood account automatically
- See your live positions

## Why No Direct Access?

Robinhood's API for personal accounts is limited and requires:
- OAuth tokens that expire frequently
- MFA codes
- Complex authentication flows
- Risk of account locks

**Better approach:** You execute trades, I track and analyze.

## Recommended Workflow

### Option 1: Quick Signal → Trade → Log (Recommended)

```python
# 1. I scan and alert you
python3 scheduled_scanner.py --time quick
# → Desktop notification: "NOK CALL $8 strike @ $0.11, 85% confidence"

# 2. You trade on Robinhood (manually)
# Buy 2 contracts of NOK Mar 7 $8 CALL @ $0.11

# 3. You tell me (or I track automatically)
from trade_tracker import enter_trade
trade = enter_trade(
    ticker='NOK',
    direction='CALL',
    strategy='low_conviction',
    strike=8.0,
    expiration='2025-03-07',
    contracts=2,
    entry_price=0.11,
    signal_confidence=85
)

# 4. Later, when you sell
from trade_tracker import exit_trade
exit_trade(trade.trade_id, exit_price=0.25, exit_reason='target_hit')

# 5. Check performance
from trade_tracker import portfolio
portfolio()
```

### Option 2: Auto-Log from Scanner

When scanner finds a signal, auto-create a "paper" trade record:

```python
from scanner_alert_integration import scan_and_alert
from trade_tracker import get_tracker

signals = scan_and_alert(['NOK', 'T'])

# Log high-conviction signals as "planned trades"
tracker = get_tracker()
for signal in signals:
    if signal.confidence >= 80:
        tracker.record_entry(
            ticker=signal.symbol,
            direction=signal.direction,
            strategy=signal.strategy,
            strike=signal.suggested_strike,
            expiration=signal.expiration,
            contracts=2,  # Default size
            entry_price=signal.option_cost,
            signal_confidence=signal.confidence,
            notes="Auto-logged from scanner"
        )
```

### Option 3: End-of-Day Batch Entry

Trade during the day, log everything at night:

```python
# At end of day, log all trades
from trade_tracker import enter_trade

# Trade 1
trade1 = enter_trade('NOK', 'CALL', 'low_conviction', 8.0, '2025-03-07', 2, 0.11)

# Trade 2  
trade2 = enter_trade('T', 'PUT', 'flow', 28.0, '2025-03-07', 1, 0.36)

# etc...

# When you exit days later
from trade_tracker import exit_trade
exit_trade(trade1.trade_id, 0.25, 'target_hit')
exit_trade(trade2.trade_id, 0.15, 'stop_loss')
```

## Integration Tools

### trade_tracker.py
- Records all your trades
- Calculates P&L
- Tracks performance by strategy
- Exports to CSV

### robinhood_connector.py (Future)
If you want, I can build a tool that:
- Uses your exported Robinhood statements
- Imports trade history automatically
- Analyzes your past performance

To export from Robinhood:
1. Robinhood app → Account → Statements & History
2. Download CSV of trades
3. I can import and analyze

## What You Get

1. **Performance Tracking**
   - Win rate by strategy
   - P&L per trade
   - Best/worst performers

2. **Signal Validation**
   - Compare my scanner signals to your actual results
   - See which patterns work for YOU

3. **Learning Loop**
   - What time of day works best?
   - Which symbols are your edge?
   - Which strategies to drop?

## Quick Start

```bash
# 1. Start tracking
cd /Users/sigbotti/.openclaw/workspace
source agents/options-trading/venv/bin/activate

# 2. Log your next trade
python3 -c "
from trade_tracker import enter_trade
trade = enter_trade('NOK', 'CALL', 'low_conviction', 8.0, '2025-03-07', 2, 0.11)
print(f'Recorded: {trade.trade_id}')
"

# 3. Check portfolio anytime
python3 -c "from trade_tracker import portfolio; portfolio()"
```

## Files

- `trade_tracker.py` - Main tracking system
- `trade_history.json` - Your trade database
- `trade_history.csv` - Export for Excel/analysis

## Next: Automated Tracking?

If you want less manual work, options:
1. **Screenshots** - Take screenshot of Robinhood, I parse with OCR
2. **Manual log** - Text me "Bought NOK 8c 2@0.11" and I auto-log
3. **Daily import** - Export Robinhood CSV daily, I auto-import

What works best for you?
