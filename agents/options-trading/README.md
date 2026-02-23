# Options Trading Multi-Agent System

Comprehensive options trading agent with hierarchical multi-agent architecture, real-time analytics, and educational modules. Built for under-$50 stocks.

## 🏗️ Architecture

### Four Specialized Teams

1. **Analyst Teams** (`analyst/agents.py`)
   - Fundamental Analyst: P/E, P/B, cash flow, DCF valuation
   - Technical Analyst: Smart Money Concepts (Order Blocks, FVG, MSB)
   - Sentiment Analyst: Unusual volume, sweep detection, flow analysis
   - News Analyst: Earnings events, macro surprises, NLP processing

2. **Research Teams** (`research/agents.py`)
   - Research Team Lead: Coordinates structured bull/bear debate
   - Bullish/Bearish Researchers: Develop opposing theses
   - Output: Confidence-weighted recommendations with conviction scores

3. **Trader Agents** (`trader/agents.py`)
   - Trader Lead: Strategy selection, position sizing, regime detection
   - Execution Agent: Order routing and fills
   - Strategies: Covered calls, PMCC, Iron Condors, Calendar spreads, Debit spreads

4. **Risk Management** (`risk/agents.py`)
   - Risk Manager: Greek limits, stress tests, correlation monitoring
   - Tail Risk Monitor: VaR, CVaR, scenario analysis
   - Real-time trade validation with pro-forma exposure calculation

### Quantitative Models (`models/pricing.py`)

- **Black-Scholes-Merton**: Option pricing with full Greek calculations
- **GARCH(1,1)**: Volatility forecasting with under-$50 adjustments
- **EGARCH**: Asymmetric volatility with leverage effects
- **Heston SV**: Stochastic volatility for smile fitting
- **VIX Replication**: Custom volatility index calculation

### Data Infrastructure (`data/stream.py`)

- Real-time OPRA data handling (1.4M contracts, 3TB daily)
- Greeks aggregation and portfolio monitoring
- Order flow classification (Lee-Ready, Bulk Volume, Quote-based)
- Sweep detection and unusual volume alerts

### Educational Module (`utils/education.py`)

Multi-level explanations from same analytical foundation:
- **Beginner**: Analogies (renting houses, casino odds)
- **Intermediate**: Plain English with key metrics
- **Advanced**: Greek analysis and probability
- **Expert**: Full quant framework with second-order Greeks

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /Users/sigbotti/.openclaw/workspace/agents/options-trading
pip install numpy scipy
```

### 2. Run the System

```bash
python3 main.py
```

### 3. Install Watchdog (Auto-Restart)

```bash
# Copy LaunchAgent to system location
cp ai.openclaw.options-trading.watchdog.plist ~/Library/LaunchAgents/

# Load and start
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.options-trading.watchdog.plist

# Verify it's running
launchctl list | grep options-trading
```

The watchdog checks every 2 minutes and restarts components if they crash.

## 📊 System Components

### Message Flow

```
Analyst Teams → Research Debate → Trader Signals → Risk Check → Execution
      ↑                                                      ↓
      └────────────── Orchestrator Coordination ←────────────┘
```

### Data Priorities

| Priority | Data Type | Latency |
|----------|-----------|---------|
| Critical | Options quotes, Underlying OHLCV | <100ms |
| High | Options trades, Greeks updates | <500ms |
| Medium | Order book depth | <1s |
| Low | News, sentiment | <5s |

### Risk Limits (Configurable)

```python
limits = {
    "portfolio_delta_pct": 0.50,      # ±50% of portfolio
    "portfolio_gamma": 1000,          # Max gamma exposure
    "portfolio_vega_pct": 0.02,       # 2% per 1% vol move
    "max_position_pct": 0.20,         # 20% single position
    "max_drawdown_pct": 0.10          # 10% max drawdown
}
```

## 🎓 Educational Examples

### Covered Call Explanation

**Beginner:**
> Like renting out a house you own. You get monthly rent (the premium). The tenant has the option to buy your house at a set price. If they don't exercise it, you keep the rent and the house.

**Intermediate:**
> Position: Long 100 shares, Short 1 call option at $52.50 strike (10% OTM). Premium collected: $1.50 (3.3% of stock price). Max profit: $5.00 if assigned. Breakeven: $43.50.

**Advanced:**
> Delta: 0.35 (hedged but still bullish). Theta: -$0.12/day working for you. Annualized return: 18.5%. Assignment risk if stock closes above strike at expiration.

**Expert:**
> Black-Scholes theoretical: $1.47, Market price: $1.50 (edge: 3bps). Charm: 0.0023, Vanna: -0.015. Scenario +10% move: +$245 P&L, -10% move: -$180 P&L.

## 🔧 Configuration

### Environment Variables

```bash
export ANTHROPIC_API_KEY="your-key"
export OPTIONS_DATA_API="provider-key"  # Optional
export DISCORD_WEBHOOK="webhook-url"     # For alerts
```

### Strategy Parameters

Edit in `trader/agents.py`:

```python
# Covered call settings
COVERED_CALL_DTE = (20, 45)      # Days to expiration range
COVERED_CALL_DELTA = (0.30, 0.40) # Target delta range
COVERED_CALL_OTM = (0.05, 0.10)   # OTM percentage

# Iron condor settings
CONDOR_WING_WIDTH = (0.10, 0.20)  # 10-20% width
CONDOR_PROFIT_TARGET = 0.50       # 50% of max profit
```

## 📈 Monitoring

### Watchdog Logs

```bash
# Real-time logstail -f /tmp/openclaw/watchdog.log

# Metrics
cat /tmp/openclaw/metrics.json
```

### Health Checks

The watchdog monitors:
- ✅ Gateway connectivity
- ✅ Trading agent process
- ✅ Disk space (>80% warning, >90% critical)
- ✅ Memory usage
- ✅ Channel health (Discord, etc.)

### Manual Health Check

```bash
./watchdog.sh
```

## 🧪 Testing

### Run Single Trading Cycle

```python
import asyncio
from main import initialize_system, run_trading_cycle

async def test():
    bus, orchestrator = await initialize_system()
    await run_trading_cycle(orchestrator)

asyncio.run(test())
```

### Test Educational Module

```python
from utils.education import OptionsEducator

educator = OptionsEducator()
metrics = {
    "stock_price": 45.0,
    "strike": 50.0,
    "premium": 1.5,
    "delta": 0.35,
    "theta": -0.12,
    "max_profit": 5.0
}

# Get beginner explanation
print(educator.format_for_user("covered_call", metrics, SkillLevel.BEGINNER))
```

## 🚨 Troubleshooting

### Gateway Won't Start

```bash
openclaw gateway stop
sleep 3
openclaw gateway start
# Or manual:
nohup openclaw gateway > /tmp/openclaw-gateway.log 2>&1 &
```

### Trading Agent Crashes

Check logs:
```bash
tail -50 /tmp/options-trading-agent.log
```

Common issues:
- Missing dependencies: `pip install numpy scipy`
- Port conflicts: Check port 18789
- Permission issues: Ensure scripts are executable

### Watchdog Not Running

```bash
# Check status
launchctl list | grep options-trading

# Restart
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.options-trading.watchdog.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.options-trading.watchdog.plist
```

## 📝 Roadmap

### Phase 1 (Current)
- ✅ Multi-agent architecture
- ✅ Core quantitative models
- ✅ Strategy library
- ✅ Educational module
- ✅ Watchdog/monitoring

### Phase 2 (Next)
- ⬜ Broker API integration (TDAmeritrade, IBKR)
- ⬜ Backtesting framework
- ⬜ Web dashboard
- ⬜ Paper trading mode

### Phase 3 (Future)
- ⬜ Machine learning models
- ⬜ Alternative data integration
- ⬜ Social sentiment analysis
- ⬜ Mobile app

## 📚 Resources

- Black-Scholes: `models/pricing.py` - `BlackScholesModel`
- Greeks: `models/pricing.py` - `Greeks` dataclass
- ReAct Pattern: `core.py` - `Agent.think()` and `Agent.act()`
- Strategy Examples: `trader/agents.py` - `TraderLead._build_*`

## ⚠️ Disclaimer

This system is for educational and research purposes. Always:
- Start with paper trading
- Understand the risks of options trading
- Never risk more than you can afford to lose
- Consult with financial advisors

Options involve substantial risk and are not suitable for all investors.

---

Built by Sig Botti for Louch. Philly-built, no cap.
