#!/usr/bin/env python3
"""API Connector - More ways to reach"""

# Discord is already connected
# Let's add Slack/Telegram ready

APIS = {
    "discord": {"status": "connected", "channel": "discord"},
    "imessage": {"status": "connected", "can_send": True},
    "mastodon": {"status": "connected", "can_post": True},
    "moltbook": {"status": "connected", "can_post": True},
    "slack": {"status": "not_connected", "note": "Need webhook URL"},
    "telegram": {"status": "not_connected", "note": "Need bot token"},
    "whatsapp": {"status": "available", "note": "WhatsApp app on Mac"},
    "signal": {"status": "not_connected", "note": "Need CLI"}
}

def status():
    """Show API status"""
    for name, info in APIS.items():
        status = "✅" if info["status"] == "connected" else "❌"
        print(f"{status} {name}: {info['status']}")
        if "note" in info:
            print(f"   {info['note']}")

def send_via(api, message):
    """Send message via specified API"""
    if api == "discord":
        # Already connected
        pass
    elif api == "imessage":
        import subprocess
        script = f'tell application "Messages" to send "{message}" to buddy "+12152848650"'
        subprocess.run(["osascript", "-e", script])
    elif api == "mastodon":
        # Already connected
        pass
    
    return f"Sent via {api}"

if __name__ == "__main__":
    print("=== API CONNECTIONS ===")
    status()
