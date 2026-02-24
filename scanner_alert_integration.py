#!/usr/bin/env python3
"""
Scanner Alert Integration
Connects the options scanner to the alert system
Auto-sends notifications when high-conviction signals trigger
"""

import sys
import os
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace')
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/agents/options-trading')

from alert_system import send_trade_alert, AlertManager, TradingAlert, AlertChannel
from advanced_options_scanner import AdvancedOptionsScanner, OptionsSignal
from datetime import datetime
from typing import List

class ScannerAlertBridge:
    """
    Bridge between options scanner and alert system
    """
    
    def __init__(self):
        self.scanner = AdvancedOptionsScanner()
        self.alert_manager = AlertManager()
        self.min_conviction_for_alert = 75  # Only alert on high conviction
        self.alert_cooldown = {}  # Prevent spam
        
    def signal_to_alert(self, signal: OptionsSignal) -> TradingAlert:
        """Convert OptionsSignal to TradingAlert"""
        
        # Build thesis
        thesis_parts = []
        thesis_parts.append(f"{signal.strategy} strategy detected")
        
        if signal.catalyst:
            thesis_parts.append(f"Catalyst: {signal.catalyst}")
        
        if signal.phase3_drug:
            thesis_parts.append(f"Phase 3: {signal.phase3_drug}")
        
        if signal.squeeze_potential:
            thesis_parts.append(f"Squeeze: {signal.squeeze_potential}")
        
        if signal.analyst_rating:
            thesis_parts.append(f"Analyst: {signal.analyst_rating} (Target: ${signal.analyst_target})")
        
        if signal.news_sentiment != 'neutral':
            thesis_parts.append(f"News sentiment: {signal.news_sentiment}")
        
        thesis = " | ".join(thesis_parts)
        
        # Determine risk level
        risk_level = "medium"
        if signal.risk_reward < 1.5:
            risk_level = "high"
        elif signal.risk_reward > 3.0:
            risk_level = "low"
        
        # Build targets
        targets = []
        if signal.target_price:
            targets.append(signal.target_price)
        if signal.analyst_target and signal.analyst_target > signal.current_price * 1.1:
            targets.append(signal.analyst_target)
        
        return TradingAlert(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ticker=signal.symbol,
            signal_type=signal.direction,
            strategy=signal.strategy,
            strike=signal.suggested_strike,
            expiration=signal.expiration,
            entry_price=signal.option_cost,
            conviction=int(signal.confidence),
            thesis=thesis,
            stop_loss=signal.stop_loss,
            targets=targets if targets else None,
            risk_level=risk_level
        )
    
    def should_alert(self, signal: OptionsSignal) -> bool:
        """Check if this signal should trigger an alert"""
        # Check conviction threshold
        if signal.confidence < self.min_conviction_for_alert:
            return False
        
        # Check cooldown (don't alert same symbol+direction within 4 hours)
        key = f"{signal.symbol}_{signal.direction}"
        now = datetime.now()
        
        if key in self.alert_cooldown:
            last_alert = self.alert_cooldown[key]
            hours_since = (now - last_alert).total_seconds() / 3600
            if hours_since < 4:
                return False
        
        # Check for valid option price ($5 or less)
        if signal.option_cost > 5.0:
            return False
        
        return True
    
    def scan_and_alert(self, watchlist: List[str] = None) -> List[OptionsSignal]:
        """
        Run scanner and send alerts for high-quality signals
        """
        if watchlist is None:
            # Default watchlist - under $50 stocks with weekly options
            watchlist = [
                'AMC', 'GME', 'BB', 'RIVN', 'LCID', 'SOFI', 'PLTR', 'NOK', 'F', 'BAC',
                'T', 'ABBV', 'PFE', 'AAL', 'CCL', 'NCLH', 'UBER', 'KMI', 'XOM', 'OXY'
            ]
        
        print(f"🔍 Scanning {len(watchlist)} stocks for signals...")
        print(f"📱 Will alert on signals with {self.min_conviction_for_alert}%+ conviction")
        print()
        
        signals = []
        alerts_sent = 0
        
        for symbol in watchlist:
            try:
                # Run scanner for this symbol
                signal = self.scanner.scan_stock(symbol)
                
                if signal and signal.confidence > 60:  # Lower threshold for display
                    signals.append(signal)
                    
                    # Check if we should alert
                    if self.should_alert(signal):
                        alert = self.signal_to_alert(signal)
                        
                        print(f"🚨 HIGH CONVICTION SIGNAL: {signal.symbol} {signal.direction}")
                        print(f"   Confidence: {signal.confidence}% | Strategy: {signal.strategy}")
                        print(f"   Strike: ${signal.suggested_strike} @ ${signal.option_cost}")
                        
                        # Send alert
                        results = self.alert_manager.send_alert(alert, [AlertChannel.ALL])
                        
                        # Track
                        key = f"{signal.symbol}_{signal.direction}"
                        self.alert_cooldown[key] = datetime.now()
                        alerts_sent += 1
                        
                        # Print results
                        for channel, result in results.items():
                            status = "✅" if result.get('success') else "❌"
                            print(f"   {status} {channel}")
                        
                        print()
                        
            except Exception as e:
                print(f"   ⚠️  {symbol}: {str(e)[:60]}")
                continue
        
        print(f"\n{'='*70}")
        print(f"Scan complete: {len(signals)} signals found, {alerts_sent} alerts sent")
        print(f"{'='*70}")
        
        return signals
    
    def alert_on_scan_results(self, signals: List[OptionsSignal], top_n: int = 5):
        """
        Send alerts for top N signals from existing scan
        """
        # Sort by confidence
        sorted_signals = sorted(signals, key=lambda x: x.confidence, reverse=True)
        
        alerts_sent = 0
        for signal in sorted_signals[:top_n]:
            if self.should_alert(signal):
                alert = self.signal_to_alert(signal)
                self.alert_manager.send_alert(alert)
                alerts_sent += 1
                
                # Update cooldown
                key = f"{signal.symbol}_{signal.direction}"
                self.alert_cooldown[key] = datetime.now()
        
        print(f"Sent {alerts_sent} alerts for top {top_n} signals")
        return alerts_sent


# Convenience function
def scan_and_alert(watchlist: List[str] = None):
    """Quick function to run scanner with alerts"""
    bridge = ScannerAlertBridge()
    return bridge.scan_and_alert(watchlist)

def send_test_trade_alert():
    """Send a test alert to verify everything works"""
    return send_trade_alert(
        ticker="NOK",
        signal_type="CALL",
        strike=8.0,
        expiration="2025-03-07",
        entry=0.11,
        conviction=85,
        thesis="Low conviction pattern detected with high flow conviction. Price near highs with extremely low RVOL suggesting stealth accumulation.",
        strategy="Flow + Low Conviction",
        stop_loss=7.80,
        targets=[8.50, 9.00],
        risk_level="medium"
    )


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🔔 SCANNER ALERT INTEGRATION")
    print("="*70)
    print()
    
    # Test alert first
    print("Sending test alert...")
    test_result = send_test_trade_alert()
    print(f"Test result: {test_result}")
    print()
    
    # Ask if user wants to run full scan
    print("To run live scan with alerts:")
    print("  from scanner_alert_integration import scan_and_alert")
    print("  signals = scan_and_alert()")
    print()
    print("Or for quick test on specific stocks:")
    print("  signals = scan_and_alert(['NOK', 'KMI', 'T'])")
    print()
    print("="*70)
