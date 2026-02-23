"""
Options Trading Multi-Agent System - Main Runner

This is the entry point for the comprehensive options trading agent.
Initializes all specialized agents and starts the message bus.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import MessageBus, TradingOrchestrator
from analyst.agents import FundamentalAnalyst, TechnicalAnalyst, SentimentAnalyst, NewsAnalyst
from research.agents import ResearchTeamLead, BullishResearcher, BearishResearcher
from trader.agents import TraderLead, ExecutionAgent
from risk.agents import RiskManager, CorrelationMonitor, TailRiskMonitor
from data.stream import OptionsDataStream, GreeksAggregator

async def initialize_system():
    """Initialize all agents and subsystems"""
    
    print("=" * 60)
    print("OPTIONS TRADING MULTI-AGENT SYSTEM")
    print("Initializing...")
    print("=" * 60)
    
    # Create message bus
    bus = MessageBus()
    
    # Initialize Analyst Teams
    print("\n[1/4] Initializing Analyst Teams...")
    
    fundamental_analyst = FundamentalAnalyst()
    fundamental_analyst.connect_bus(bus)
    bus.subscribe(fundamental_analyst.agent_id, MessageType.COMMAND)
    print(f"  ✓ {fundamental_analyst.agent_id}")
    
    technical_analyst = TechnicalAnalyst()
    technical_analyst.connect_bus(bus)
    bus.subscribe(technical_analyst.agent_id, MessageType.COMMAND)
    print(f"  ✓ {technical_analyst.agent_id}")
    
    sentiment_analyst = SentimentAnalyst()
    sentiment_analyst.connect_bus(bus)
    bus.subscribe(sentiment_analyst.agent_id, MessageType.COMMAND)
    print(f"  ✓ {sentiment_analyst.agent_id}")
    
    news_analyst = NewsAnalyst()
    news_analyst.connect_bus(bus)
    bus.subscribe(news_analyst.agent_id, MessageType.COMMAND)
    print(f"  ✓ {news_analyst.agent_id}")
    
    # Initialize Research Teams
    print("\n[2/4] Initializing Research Teams...")
    
    research_lead = ResearchTeamLead()
    research_lead.connect_bus(bus)
    bus.subscribe(research_lead.agent_id, MessageType.ANALYSIS)
    print(f"  ✓ {research_lead.agent_id}")
    
    bullish_researcher = BullishResearcher()
    bullish_researcher.connect_bus(bus)
    print(f"  ✓ {bullish_researcher.agent_id}")
    
    bearish_researcher = BearishResearcher()
    bearish_researcher.connect_bus(bus)
    print(f"  ✓ {bearish_researcher.agent_id}")
    
    # Initialize Trader Agents
    print("\n[3/4] Initializing Trader Agents...")
    
    trader_lead = TraderLead()
    trader_lead.connect_bus(bus)
    bus.subscribe(trader_lead.agent_id, MessageType.RESEARCH_REPORT)
    print(f"  ✓ {trader_lead.agent_id}")
    
    execution_agent = ExecutionAgent()
    execution_agent.connect_bus(bus)
    print(f"  ✓ {execution_agent.agent_id}")
    
    # Initialize Risk Management
    print("\n[4/4] Initializing Risk Management...")
    
    risk_manager = RiskManager()
    risk_manager.connect_bus(bus)
    bus.subscribe(risk_manager.agent_id, MessageType.TRADE_SIGNAL)
    print(f"  ✓ {risk_manager.agent_id}")
    
    correlation_monitor = CorrelationMonitor()
    correlation_monitor.connect_bus(bus)
    print(f"  ✓ {correlation_monitor.agent_id}")
    
    tail_risk_monitor = TailRiskMonitor()
    tail_risk_monitor.connect_bus(bus)
    print(f"  ✓ {tail_risk_monitor.agent_id}")
    
    # Initialize Orchestrator
    orchestrator = TradingOrchestrator()
    orchestrator.connect_bus(bus)
    bus.subscribe(orchestrator.agent_id, MessageType.ANALYSIS)
    bus.subscribe(orchestrator.agent_id, MessageType.RISK_ALERT)
    print(f"\n  ✓ {orchestrator.agent_id} (Executive)")
    
    print("\n" + "=" * 60)
    print("SYSTEM INITIALIZED")
    print(f"Total agents: {len(bus.agents)}")
    print("=" * 60)
    
    return bus, orchestrator

async def run_trading_cycle(orchestrator: TradingOrchestrator):
    """Execute one full trading cycle"""
    
    print("\n" + "=" * 60)
    print("EXECUTING TRADING CYCLE")
    print("=" * 60)
    
    # Step 1: Coordinate trade cycle
    await orchestrator.coordinate_trade_cycle()
    
    # Wait for analysis to propagate
    print("\nWaiting for agent analysis...")
    await asyncio.sleep(5)
    
    # Step 2: Orchestrator synthesis
    print("\nOrchestrator synthesizing...")
    reasoning = await orchestrator.think("Synthesize all analyses for trading decision")
    action = await orchestrator.act(reasoning)
    
    if action:
        print(f"Orchestrator action: {action.msg_type.value}")
    
    print("\n" + "=" * 60)
    print("TRADING CYCLE COMPLETE")
    print("=" * 60)

async def start_data_stream(symbols: list):
    """Start real-time data stream"""
    
    stream = OptionsDataStream()
    greeks_agg = GreeksAggregator()
    
    # Register handlers
    async def on_quote(event):
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] Quote: {event.symbol} "
              f"Bid: {event.data['bid']:.2f} Ask: {event.data['ask']:.2f}")
    
    async def on_greeks(event):
        await greeks_agg.update_position(
            event.symbol,
            event.data,
            contracts=1
        )
    
    stream.register_handler("quote", on_quote)
    stream.register_handler("greeks_update", on_greeks)
    
    # Start streaming
    await stream.start_stream(symbols)

async def main():
    """Main entry point"""
    
    # Initialize system
    bus, orchestrator = await initialize_system()
    
    # Start message bus in background
    bus_task = asyncio.create_task(bus.run())
    
    # Give bus time to start
    await asyncio.sleep(1)
    
    try:
        # Run initial trading cycle
        await run_trading_cycle(orchestrator)
        
        # Start continuous operation
        print("\n" + "=" * 60)
        print("ENTERING CONTINUOUS OPERATION")
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        cycle_count = 0
        while True:
            await asyncio.sleep(60)  # Run cycle every minute
            cycle_count += 1
            print(f"\n--- Cycle {cycle_count} ---")
            await run_trading_cycle(orchestrator)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        bus.stop()
        bus_task.cancel()
        try:
            await bus_task
        except asyncio.CancelledError:
            pass
        print("System stopped.")

if __name__ == "__main__":
    # Import here to avoid circular imports
    from core import MessageType
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
