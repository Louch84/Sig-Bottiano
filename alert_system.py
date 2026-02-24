#!/usr/bin/env python3
"""
Alert System - Multi-Channel Notifications
Sends trading alerts via Discord, Telegram, or Desktop
"""

import os
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class AlertChannel(Enum):
    DISCORD = "discord"
    TELEGRAM = "telegram"
    DESKTOP = "desktop"
    ALL = "all"

@dataclass
class TradingAlert:
    """A trading signal alert"""
    timestamp: str
    ticker: str
    signal_type: str  # CALL, PUT, WATCH
    strategy: str     # Squeeze, Low Conviction, Flow, etc.
    strike: float
    expiration: str
    entry_price: float
    conviction: int   # 0-100
    thesis: str
    stop_loss: Optional[float] = None
    targets: Optional[List[float]] = None
    risk_level: str = "medium"  # low, medium, high

class AlertManager:
    """
    Multi-channel alert system for trading signals
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.alert_history: List[Dict] = []
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load config from file or environment"""
        config = {
            'discord': {
                'enabled': False,
                'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', ''),
                'bot_token': os.getenv('DISCORD_BOT_TOKEN', ''),
                'channel_id': os.getenv('DISCORD_CHANNEL_ID', '')
            },
            'telegram': {
                'enabled': False,
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
            },
            'desktop': {
                'enabled': True  # Always try desktop as fallback
            }
        }
        
        # Try to load from file
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        
        # Check if env vars are set
        if config['discord']['webhook_url']:
            config['discord']['enabled'] = True
        if config['telegram']['bot_token'] and config['telegram']['chat_id']:
            config['telegram']['enabled'] = True
            
        return config
    
    def send_alert(self, alert: TradingAlert, channels: List[AlertChannel] = None) -> Dict:
        """
        Send alert via specified channels
        Returns status of each channel
        """
        if channels is None:
            channels = [AlertChannel.ALL]
        
        if AlertChannel.ALL in channels:
            channels = [AlertChannel.DISCORD, AlertChannel.TELEGRAM, AlertChannel.DESKTOP]
        
        results = {}
        
        for channel in channels:
            try:
                if channel == AlertChannel.DISCORD:
                    results['discord'] = self._send_discord(alert)
                elif channel == AlertChannel.TELEGRAM:
                    results['telegram'] = self._send_telegram(alert)
                elif channel == AlertChannel.DESKTOP:
                    results['desktop'] = self._send_desktop(alert)
            except Exception as e:
                results[channel.value] = {'success': False, 'error': str(e)}
        
        # Log to history
        self.alert_history.append({
            'alert': asdict(alert),
            'results': results,
            'sent_at': datetime.now().isoformat()
        })
        
        return results
    
    def _send_discord(self, alert: TradingAlert) -> Dict:
        """Send alert via Discord webhook"""
        webhook_url = self.config['discord']['webhook_url']
        
        if not webhook_url:
            return {'success': False, 'error': 'Discord webhook not configured'}
        
        # Format message
        emoji = "🟢" if alert.signal_type == "CALL" else "🔴" if alert.signal_type == "PUT" else "⚪"
        
        embed = {
            "title": f"{emoji} {alert.ticker} {alert.signal_type} ALERT",
            "description": alert.thesis[:500],
            "color": 0x00ff00 if alert.signal_type == "CALL" else 0xff0000 if alert.signal_type == "PUT" else 0x808080,
            "fields": [
                {"name": "📊 Strategy", "value": alert.strategy, "inline": True},
                {"name": "🎯 Strike", "value": f"${alert.strike}", "inline": True},
                {"name": "📅 Expiration", "value": alert.expiration, "inline": True},
                {"name": "💰 Entry", "value": f"${alert.entry_price}", "inline": True},
                {"name": "📈 Conviction", "value": f"{alert.conviction}%", "inline": True},
                {"name": "⚠️ Risk", "value": alert.risk_level.upper(), "inline": True},
            ],
            "footer": {"text": f"Sig Mind Alert System • {alert.timestamp}"}
        }
        
        if alert.stop_loss:
            embed["fields"].append({"name": "🛑 Stop Loss", "value": f"${alert.stop_loss}", "inline": True})
        
        if alert.targets:
            targets_str = ", ".join([f"${t}" for t in alert.targets[:3]])
            embed["fields"].append({"name": "🎯 Targets", "value": targets_str, "inline": False})
        
        payload = {
            "embeds": [embed],
            "content": f"@here New {alert.signal_type} signal on {alert.ticker}"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            return {'success': True, 'message_id': 'webhook_sent'}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
    
    def _send_telegram(self, alert: TradingAlert) -> Dict:
        """Send alert via Telegram bot"""
        bot_token = self.config['telegram']['bot_token']
        chat_id = self.config['telegram']['chat_id']
        
        if not bot_token or not chat_id:
            return {'success': False, 'error': 'Telegram not configured'}
        
        emoji = "🟢" if alert.signal_type == "CALL" else "🔴" if alert.signal_type == "PUT" else "⚪"
        
        message = f"""
{emoji} <b>{alert.ticker} {alert.signal_type} ALERT</b>

📊 <b>Strategy:</b> {alert.strategy}
🎯 <b>Strike:</b> ${alert.strike}
📅 <b>Expiration:</b> {alert.expiration}
💰 <b>Entry:</b> ${alert.entry_price}
📈 <b>Conviction:</b> {alert.conviction}%
⚠️ <b>Risk:</b> {alert.risk_level.upper()}

<b>Thesis:</b>
{alert.thesis[:300]}...

🛑 <b>Stop Loss:</b> ${alert.stop_loss if alert.stop_loss else 'TBD'}
        """.strip()
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return {'success': True, 'message_id': response.json().get('result', {}).get('message_id')}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
    
    def _send_desktop(self, alert: TradingAlert) -> Dict:
        """Send desktop notification (macOS)"""
        try:
            import subprocess
            
            title = f"{alert.ticker} {alert.signal_type} Alert"
            message = f"{alert.strategy} | Strike: ${alert.strike} | Conviction: {alert.conviction}%"
            
            # macOS notification
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(['osascript', '-e', script], check=True)
            
            return {'success': True, 'message': 'Desktop notification sent'}
        except Exception as e:
            return {'success': False, 'error': f'Desktop notification failed: {str(e)}'}
    
    def test_all_channels(self) -> Dict:
        """Test all configured channels"""
        test_alert = TradingAlert(
            timestamp=datetime.now().isoformat(),
            ticker="TEST",
            signal_type="CALL",
            strategy="Test Alert",
            strike=100.0,
            expiration="2025-03-01",
            entry_price=1.50,
            conviction=75,
            thesis="This is a test alert to verify the notification system is working.",
            risk_level="low"
        )
        
        return self.send_alert(test_alert, [AlertChannel.ALL])
    
    def get_alert_history(self, limit: int = 10) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def save_config(self, path: str = "alert_config.json"):
        """Save current config to file"""
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)


# Convenience functions
alert_manager = None

def get_alert_manager() -> AlertManager:
    """Get or create alert manager singleton"""
    global alert_manager
    if alert_manager is None:
        alert_manager = AlertManager()
    return alert_manager

def send_trade_alert(ticker: str, signal_type: str, strike: float, 
                     expiration: str, entry: float, conviction: int,
                     thesis: str, **kwargs) -> Dict:
    """Quick function to send a trade alert"""
    manager = get_alert_manager()
    
    alert = TradingAlert(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ticker=ticker,
        signal_type=signal_type,
        strategy=kwargs.get('strategy', 'Scanner'),
        strike=strike,
        expiration=expiration,
        entry_price=entry,
        conviction=conviction,
        thesis=thesis,
        stop_loss=kwargs.get('stop_loss'),
        targets=kwargs.get('targets'),
        risk_level=kwargs.get('risk_level', 'medium')
    )
    
    return manager.send_alert(alert)

def test_alerts():
    """Test all alert channels"""
    manager = get_alert_manager()
    return manager.test_all_channels()


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🚨 ALERT SYSTEM TEST")
    print("="*70)
    print()
    
    # Test configuration
    manager = get_alert_manager()
    print("Configuration Status:")
    print(f"  Discord: {'✅ Enabled' if manager.config['discord']['enabled'] else '❌ Not configured'}")
    print(f"  Telegram: {'✅ Enabled' if manager.config['telegram']['enabled'] else '❌ Not configured'}")
    print(f"  Desktop: {'✅ Enabled' if manager.config['desktop']['enabled'] else '❌ Disabled'}")
    print()
    
    # Send test alert
    print("Sending test alert...")
    results = test_alerts()
    
    print("\nResults:")
    for channel, result in results.items():
        status = "✅" if result.get('success') else "❌"
        print(f"  {status} {channel}: {result.get('message', result.get('error', 'Unknown'))}")
    
    print()
    print("="*70)
    print("To configure alerts, set these environment variables:")
    print("  DISCORD_WEBHOOK_URL - Discord webhook URL")
    print("  TELEGRAM_BOT_TOKEN - Telegram bot token")
    print("  TELEGRAM_CHAT_ID - Telegram chat ID")
    print("="*70)
