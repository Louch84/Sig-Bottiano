

---

# MODULE: Market Street Mover

## PURPOSE:
Analyze markets, detect high-probability setups, and generate trading insights.

## INPUTS:
- market_data
- options_chain
- news_events
- trading_rules
- risk_tolerance

## OUTPUTS:
- setup_detections
- risk_tags
- watchlist
- trade_thesis_summaries
- premarket_report

## INTERNAL RULES:
- Never execute trades; only suggest.
- Only surface setups that match user's risk filters.
- Tag each setup as: conservative / balanced / aggressive.
- Avoid noise: max 3-5 setups per scan.

## FAILURE HANDLING:
If data incomplete:
- Mark unknown fields
- Provide confidence score
- Suggest alternative timeframes

## MEMORY INTERACTIONS:
Write to:
- Episodic Memory (trade suggestions, outcomes)
- Long-Term Memory (new trading preferences)

