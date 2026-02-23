"""
Options Trading Multi-Agent System
Core orchestrator and message bus for coordinating specialized trading agents.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    ANALYST = "analyst"
    RESEARCH = "research"
    TRADER = "trader"
    RISK = "risk"
    ORCHESTRATOR = "orchestrator"

class MessageType(Enum):
    ANALYSIS = "analysis"
    RESEARCH_REPORT = "research_report"
    TRADE_SIGNAL = "trade_signal"
    RISK_ALERT = "risk_alert"
    MARKET_DATA = "market_data"
    COMMAND = "command"
    RESPONSE = "response"

@dataclass
class Message:
    msg_id: str
    sender: str
    recipient: str
    msg_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5  # 1 = highest, 10 = lowest
    
    def to_dict(self) -> Dict:
        return {
            "msg_id": self.msg_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "msg_type": self.msg_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority
        }

class Agent:
    """Base agent class with ReAct pattern implementation"""
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.message_bus: Optional['MessageBus'] = None
        self.memory: List[Dict] = []
        self.reasoning_chain: List[str] = []
        
    def connect_bus(self, bus: 'MessageBus'):
        self.message_bus = bus
        bus.register_agent(self)
        
    async def think(self, observation: str) -> str:
        """ReAct: Reasoning step"""
        self.reasoning_chain.append(f"Observation: {observation}")
        reasoning = await self._reason(observation)
        self.reasoning_chain.append(f"Reasoning: {reasoning}")
        return reasoning
    
    async def act(self, reasoning: str) -> Optional[Message]:
        """ReAct: Action step"""
        action = await self._decide_action(reasoning)
        self.reasoning_chain.append(f"Action: {action}")
        return action
    
    async def _reason(self, observation: str) -> str:
        """Override in subclasses"""
        raise NotImplementedError
    
    async def _decide_action(self, reasoning: str) -> Optional[Message]:
        """Override in subclasses"""
        raise NotImplementedError
    
    async def receive_message(self, msg: Message):
        """Process incoming messages"""
        logger.info(f"[{self.agent_id}] Received {msg.msg_type.value} from {msg.sender}")
        self.memory.append(msg.to_dict())
        
    def send_message(self, recipient: str, msg_type: MessageType, payload: Dict, priority: int = 5):
        """Send message via bus"""
        if self.message_bus:
            msg = Message(
                msg_id=f"{self.agent_id}_{datetime.now().timestamp()}",
                sender=self.agent_id,
                recipient=recipient,
                msg_type=msg_type,
                payload=payload,
                priority=priority
            )
            self.message_bus.send(msg)
            
    def broadcast_analysis(self, analysis_type: str, data: Dict, confidence: float):
        """Broadcast analysis to all interested agents"""
        self.send_message(
            recipient="all",
            msg_type=MessageType.ANALYSIS,
            payload={
                "analysis_type": analysis_type,
                "data": data,
                "confidence": confidence,
                "agent_role": self.role.value
            }
        )

class MessageBus:
    """Central message coordination system"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.message_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.subscribers: Dict[MessageType, List[str]] = {
            msg_type: [] for msg_type in MessageType
        }
        self.running = False
        
    def register_agent(self, agent: Agent):
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} ({agent.role.value})")
        
    def subscribe(self, agent_id: str, msg_type: MessageType):
        if agent_id in self.agents:
            self.subscribers[msg_type].append(agent_id)
            
    def send(self, msg: Message):
        """Queue message for delivery"""
        self.message_queue.put_nowait((msg.priority, msg))
        logger.debug(f"Queued message {msg.msg_id} ({msg.msg_type.value})")
        
    async def run(self):
        """Main message processing loop"""
        self.running = True
        logger.info("Message bus started")
        
        while self.running:
            try:
                priority, msg = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                await self._route_message(msg)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Message routing error: {e}")
                
    async def _route_message(self, msg: Message):
        """Route message to recipient(s)"""
        if msg.recipient == "all":
            # Broadcast to subscribers of this message type
            recipients = self.subscribers.get(msg.msg_type, [])
            for agent_id in recipients:
                if agent_id in self.agents and agent_id != msg.sender:
                    await self.agents[agent_id].receive_message(msg)
        else:
            # Direct message
            if msg.recipient in self.agents:
                await self.agents[msg.recipient].receive_message(msg)
                
    def stop(self):
        self.running = False
        logger.info("Message bus stopped")

class TradingOrchestrator(Agent):
    """
    Executive agent coordinating all specialized teams.
    Implements hierarchical governance with ReAct pattern.
    """
    
    def __init__(self):
        super().__init__("orchestrator", AgentRole.ORCHESTRATOR)
        self.trading_state = {
            "positions": {},
            "pending_signals": [],
            "risk_limits": {},
            "market_regime": None
        }
        
    async def _reason(self, observation: str) -> str:
        """Synthesize inputs from all teams"""
        recent_analyses = [m for m in self.memory if m.get("msg_type") == "analysis"][-10:]
        
        reasoning = f"""
        Based on {len(recent_analyses)} recent analyses:
        - Market regime: {self.trading_state['market_regime']}
        - Open positions: {len(self.trading_state['positions'])}
        - Pending signals: {len(self.trading_state['pending_signals'])}
        
        Observation: {observation}
        
        Must coordinate: analyst valuations → research debate → trader execution with risk oversight
        """
        return reasoning
    
    async def _decide_action(self, reasoning: str) -> Optional[Message]:
        """Coordinate final trading decisions"""
        # Extract confidence scores from recent analyses
        analyses = [m for m in self.memory if m.get("msg_type") == "analysis"]
        avg_confidence = sum(a.get("payload", {}).get("confidence", 0) for a in analyses) / max(len(analyses), 1)
        
        if avg_confidence > 0.7:
            # High confidence - proceed with trade coordination
            return Message(
                msg_id=f"orch_{datetime.now().timestamp()}",
                sender=self.agent_id,
                recipient="trader_lead",
                msg_type=MessageType.COMMAND,
                payload={
                    "command": "EVALUATE_SIGNALS",
                    "confidence": avg_confidence,
                    "context": reasoning
                },
                priority=2
            )
        return None
    
    async def coordinate_trade_cycle(self):
        """Main coordination loop"""
        # 1. Request fresh analysis
        self.send_message(
            "analyst_fundamental",
            MessageType.COMMAND,
            {"command": "ANALYZE_UNIVERSE", "focus": "under_50"}
        )
        
        self.send_message(
            "analyst_technical",
            MessageType.COMMAND,
            {"command": "GENERATE_SIGNALS"}
        )
        
        # 2. Trigger research debate
        await asyncio.sleep(2)  # Allow analysis to complete
        
        self.send_message(
            "research_lead",
            MessageType.COMMAND,
            {"command": "DEBATE_CANDIDATES"}
        )
        
        # 3. Risk check before execution
        await asyncio.sleep(2)
        
        self.send_message(
            "risk_manager",
            MessageType.COMMAND,
            {"command": "VALIDATE_PORTFOLIO"}
        )

# Usage example
async def main():
    bus = MessageBus()
    
    # Initialize agents
    orchestrator = TradingOrchestrator()
    
    # Connect all to bus
    orchestrator.connect_bus(bus)
    
    # Start message bus
    await bus.run()

if __name__ == "__main__":
    asyncio.run(main())
