#!/usr/bin/env python3
"""
Alert Setup - Configure Discord/Telegram for trading alerts
"""

import os
import json

def setup_discord():
    """Guide user through Discord webhook setup"""
    print("="*70)
    print("🔷 DISCORD SETUP")
    print("="*70)
    print()
    print("To get Discord alerts, you need a webhook URL:")
    print()
    print("1. Open Discord and go to your server")
    print("2. Right-click a channel → Edit Channel → Integrations")
    print("3. Click 'Webhooks' → 'New Webhook'")
    print("4. Name it 'Trading Alerts' and copy the URL")
    print()
    
    webhook = input("Paste your Discord webhook URL (or press Enter to skip): ").strip()
    
    if webhook:
        # Save to config
        config = {}
        if os.path.exists('alert_config.json'):
            with open('alert_config.json', 'r') as f:
                config = json.load(f)
        
        config['discord'] = {'enabled': True, 'webhook_url': webhook}
        
        with open('alert_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Discord configured!")
        
        # Also show how to set env var
        print()
        print("To make it permanent, add to your shell profile:")
        print(f'export DISCORD_WEBHOOK_URL="{webhook}"')
    else:
        print("⏭️  Skipped Discord setup")
    
    print()

def setup_telegram():
    """Guide user through Telegram bot setup"""
    print("="*70)
    print("📱 TELEGRAM SETUP")
    print("="*70)
    print()
    print("To get Telegram alerts:")
    print()
    print("1. Message @BotFather on Telegram")
    print("2. Send /newbot and follow instructions")
    print("3. Copy the bot token (looks like: 123456789:ABCdefGHIjkl)")
    print("4. Message your new bot, then visit:")
    print("   https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("5. Look for 'chat': {'id': 123456789} - that's your chat ID")
    print()
    
    bot_token = input("Paste your Telegram bot token (or press Enter to skip): ").strip()
    chat_id = input("Paste your Telegram chat ID (or press Enter to skip): ").strip()
    
    if bot_token and chat_id:
        config = {}
        if os.path.exists('alert_config.json'):
            with open('alert_config.json', 'r') as f:
                config = json.load(f)
        
        config['telegram'] = {
            'enabled': True,
            'bot_token': bot_token,
            'chat_id': chat_id
        }
        
        with open('alert_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Telegram configured!")
        
        print()
        print("To make it permanent, add to your shell profile:")
        print(f'export TELEGRAM_BOT_TOKEN="{bot_token}"')
        print(f'export TELEGRAM_CHAT_ID="{chat_id}"')
    else:
        print("⏭️  Skipped Telegram setup")
    
    print()

def test_alerts():
    """Test configured alerts"""
    print("="*70)
    print("🧪 TESTING ALERTS")
    print("="*70)
    print()
    
    from alert_system import test_alerts
    results = test_alerts()
    
    print("\nResults:")
    for channel, result in results.items():
        status = "✅" if result.get('success') else "❌"
        message = result.get('message', result.get('error', 'Unknown'))
        print(f"  {status} {channel}: {message}")
    
    print()

def main():
    """Main setup flow"""
    print("="*70)
    print("🚨 TRADING ALERT SETUP")
    print("="*70)
    print()
    print("This will set up alerts for your options scanner")
    print("You'll get notified when high-conviction signals trigger")
    print()
    
    # Check current status
    config = {}
    if os.path.exists('alert_config.json'):
        with open('alert_config.json', 'r') as f:
            config = json.load(f)
    
    discord_enabled = config.get('discord', {}).get('enabled', False)
    telegram_enabled = config.get('telegram', {}).get('enabled', False)
    
    print("Current Status:")
    print(f"  Discord: {'✅ Configured' if discord_enabled else '❌ Not configured'}")
    print(f"  Telegram: {'✅ Configured' if telegram_enabled else '❌ Not configured'}")
    print(f"  Desktop: ✅ Always available (macOS notifications)")
    print()
    
    # Menu
    while True:
        print("Options:")
        print("  1. Setup Discord alerts")
        print("  2. Setup Telegram alerts")
        print("  3. Test all alerts")
        print("  4. Done")
        print()
        
        choice = input("Choose (1-4): ").strip()
        
        if choice == '1':
            setup_discord()
        elif choice == '2':
            setup_telegram()
        elif choice == '3':
            test_alerts()
        elif choice == '4':
            break
        else:
            print("Invalid choice\n")
    
    print("="*70)
    print("✅ Setup complete!")
    print()
    print("To run scanner with alerts:")
    print("  python3 scheduled_scanner.py")
    print()
    print("Or in your code:")
    print("  from scanner_alert_integration import scan_and_alert")
    print("  signals = scan_and_alert()")
    print("="*70)

if __name__ == "__main__":
    main()
