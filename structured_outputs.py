"""
Structured Outputs System
Forces consistent, validated JSON output from agents
Free implementation - no API costs
"""

import json
import re
from typing import Dict, Any, Optional, Type, get_type_hints
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TradingSignal:
    """Structured trading signal format"""
    symbol: str
    direction: str  # CALL or PUT
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: float
    target_price: float
    risk_reward: float
    strategy: str  # DAY_TRADE or SWING
    timeframe: str
    catalysts: list
    max_contracts: int
    timestamp: str
    
    def validate(self) -> tuple[bool, list]:
        """Validate signal completeness"""
        errors = []
        
        if self.confidence < 0 or self.confidence > 1:
            errors.append("Confidence must be 0-1")
        
        if self.direction not in ['CALL', 'PUT']:
            errors.append("Direction must be CALL or PUT")
        
        if self.entry_price <= 0:
            errors.append("Entry price must be positive")
        
        if self.stop_loss <= 0:
            errors.append("Stop loss must be positive")
        
        if self.target_price <= 0:
            errors.append("Target price must be positive")
        
        if self.risk_reward < 0.5:
            errors.append("Risk:Reward seems too low")
        
        return len(errors) == 0, errors
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TradingSignal':
        """Create from dictionary"""
        return cls(**data)


class StructuredOutputParser:
    """
    Parse and validate agent outputs into structured formats
    """
    
    def __init__(self):
        self.schemas = {
            'trading_signal': TradingSignal
        }
    
    def parse_signal_from_text(self, text: str) -> Optional[TradingSignal]:
        """
        Extract structured signal from agent's text output
        Uses regex patterns to find key data
        """
        try:
            # Extract symbol
            symbol_match = re.search(r'(?:Symbol|Stock):?\s*([A-Z]{1,5})', text, re.I)
            symbol = symbol_match.group(1) if symbol_match else "UNKNOWN"
            
            # Extract direction
            direction = "CALL" if re.search(r'\bCALL\b|\bbullish\b', text, re.I) else \
                       "PUT" if re.search(r'\bPUT\b|\bbearish\b', text, re.I) else "UNKNOWN"
            
            # Extract confidence
            conf_match = re.search(r'(?:Confidence|Conviction):?\s*(\d+)%', text, re.I)
            confidence = int(conf_match.group(1)) / 100 if conf_match else 0.5
            
            # Extract prices
            entry_match = re.search(r'(?:Entry|Price):?\s*\$?([\d.]+)', text, re.I)
            entry = float(entry_match.group(1)) if entry_match else 0.0
            
            stop_match = re.search(r'(?:Stop|Stop Loss):?\s*\$?([\d.]+)', text, re.I)
            stop = float(stop_match.group(1)) if stop_match else entry * 0.97
            
            target_match = re.search(r'(?:Target|Target Price):?\s*\$?([\d.]+)', text, re.I)
            target = float(target_match.group(1)) if target_match else entry * 1.03
            
            # Calculate R:R
            risk = abs(entry - stop)
            reward = abs(target - entry)
            rr = reward / risk if risk > 0 else 2.0
            
            # Determine strategy
            strategy = "DAY_TRADE" if re.search(r'\b0DTE\b|\bday trade\b', text, re.I) else "SWING"
            
            # Extract catalysts
            catalysts = []
            if re.search(r'short interest', text, re.I):
                catalysts.append("short_interest")
            if re.search(r'earnings', text, re.I):
                catalysts.append("earnings")
            if re.search(r'volume', text, re.I):
                catalysts.append("volume_surge")
            if re.search(r'breakout', text, re.I):
                catalysts.append("breakout")
            
            if not catalysts:
                catalysts.append("technical_setup")
            
            signal = TradingSignal(
                symbol=symbol,
                direction=direction,
                confidence=confidence,
                entry_price=entry,
                stop_loss=stop,
                target_price=target,
                risk_reward=rr,
                strategy=strategy,
                timeframe="0DTE" if strategy == "DAY_TRADE" else "7D",
                catalysts=catalysts,
                max_contracts=2,
                timestamp=datetime.now().isoformat()
            )
            
            # Validate
            valid, errors = signal.validate()
            if not valid:
                print(f"⚠️  Validation warnings: {errors}")
            
            return signal
            
        except Exception as e:
            print(f"❌ Failed to parse signal: {e}")
            return None
    
    def force_json_output(self, agent_response: str, schema: dict) -> dict:
        """
        Force agent response into valid JSON
        Uses multiple strategies to extract structured data
        """
        # Strategy 1: Look for JSON code block
        json_match = re.search(r'```json\n(.*?)\n```', agent_response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Strategy 2: Look for any JSON object
        json_match = re.search(r'\{[\s\S]*?"symbol"[\s\S]*?\}', agent_response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        # Strategy 3: Parse from text
        signal = self.parse_signal_from_text(agent_response)
        if signal:
            return asdict(signal)
        
        # Fallback: Return error structure
        return {
            "error": "Could not parse structured output",
            "raw_response": agent_response[:200]
        }


class OutputValidator:
    """
    Validates outputs against schemas
    Ensures consistency and completeness
    """
    
    REQUIRED_SIGNAL_FIELDS = [
        'symbol', 'direction', 'entry_price', 'stop_loss', 
        'target_price', 'risk_reward'
    ]
    
    def validate_signal(self, signal: dict) -> tuple[bool, list]:
        """Validate a trading signal has all required fields"""
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_SIGNAL_FIELDS:
            if field not in signal:
                errors.append(f"Missing required field: {field}")
        
        # Check value ranges
        if 'confidence' in signal:
            if not 0 <= signal['confidence'] <= 1:
                errors.append("Confidence must be between 0 and 1")
        
        if 'direction' in signal:
            if signal['direction'] not in ['CALL', 'PUT']:
                errors.append("Direction must be CALL or PUT")
        
        if 'risk_reward' in signal:
            if signal['risk_reward'] < 0.5:
                errors.append("Risk:Reward ratio seems too low (< 0.5)")
        
        return len(errors) == 0, errors
    
    def sanitize_output(self, data: dict) -> dict:
        """Clean and sanitize output data"""
        cleaned = {}
        
        for key, value in data.items():
            # Round floats to reasonable precision
            if isinstance(value, float):
                cleaned[key] = round(value, 4)
            # Ensure strings are clean
            elif isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        
        return cleaned


# Global instances
parser = StructuredOutputParser()
validator = OutputValidator()

# Example usage
if __name__ == "__main__":
    # Test parsing
    sample_text = """
    Symbol: AMC
    Direction: PUT
    Confidence: 65%
    Entry: $1.20
    Stop: $1.22
    Target: $1.13
    Catalyst: High short interest
    """
    
    signal = parser.parse_signal_from_text(sample_text)
    if signal:
        print("✅ Parsed signal:")
        print(signal.to_json())
        
        valid, errors = signal.validate()
        if valid:
            print("\n✅ Signal is valid")
        else:
            print(f"\n⚠️  Validation errors: {errors}")
