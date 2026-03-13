# modules/alerts.py

class RumorAlertSystem:
    def __init__(self):
        self.alert_channels = ['console', 'webhook', 'email']  # Configure as needed
    
    def send_rumor_alert(self, signal: Dict):
        """
        Send formatted alert for new rumor detection
        """
        message = f"""
🚨 RUMOR ALERT - {signal['urgency_level'].upper()} 🚨

Ticker: ${signal['ticker']}
Type: {signal['rumor_type']}
Source: @{signal['source']}
Confidence: {signal['confidence_score']:.1%}

Signal Details:
• Options Flow Confirmed: {'✅' if signal['options_flow_confirmed'] else '❌'}
• Sentiment Score: {signal['sentiment_score']:+.2f}
• Keywords: {', '.join(signal['keywords_matched'])}

Extract: "{signal['raw_text'][:200]}..."

Action Required: {'IMMEDIATE' if signal['urgency_level'] == 'critical' else 'Review Trade Plan'}

Timestamp: {signal['timestamp']}
        """
        
        self._dispatch_alert(message, signal['urgency_level'])
    
    def send_trade_alert(self, trade_type: str, plan: Dict):
        """
        Alert for trade execution
        """
        if trade_type == 'entry':
            message = f"""
📈 POSITION ENTERED

Ticker: ${plan['ticker']}
Entry: ${plan['entry_price']:.2f}
Target: ${plan['target_price']:.2f} (+{((plan['target_price']/plan['entry_price'])-1)*100:.1f}%)
Stop: ${plan['stop_loss']:.2f} (-{((1-plan['stop_loss']/plan['entry_price']))*100:.1f}%)
Size: {plan['position_size']} shares
Exit Strategy: {plan['exit_trigger']}

Time Stop: {plan['planned_exit_time']}
            """
        else:  # exit
            message = f"""
📉 POSITION EXITED

Ticker: ${plan['ticker']}
Exit Reason: {plan['exit_reason']}
P&L: {plan['pnl']:.2f} ({plan['pnl_pct']:+.2f}%)
Duration: {plan['duration']}
            """
        
        self._dispatch_alert(message, 'trade')
    
    def _dispatch_alert(self, message: str, priority: str):
        # Implement your alert dispatch logic
        # Console, webhook to your UI, email, SMS, etc.
        pass
