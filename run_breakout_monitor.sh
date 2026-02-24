#!/bin/bash
# Breakout Alert Monitor with Desktop Notifications
# Runs continuously and alerts when breakouts are confirmed

cd /Users/sigbotti/.openclaw/workspace
source agents/options-trading/venv/bin/activate

echo "=========================================="
echo "🚀 BREAKOUT ENTRY ALERT SYSTEM"
echo "=========================================="
echo ""
echo "This will check every 5 minutes for confirmed breakouts"
echo "You'll get desktop notifications when it's time to buy"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Function to send desktop notification
send_notification() {
    local title="$1"
    local message="$2"
    osascript -e "display notification \"$message\" with title \"$title\" sound name \"Glass\""
}

# Run the monitor with notification support
python3 -c "
import sys
sys.path.insert(0, '.')
from breakout_alerts import BreakoutEntryAlerts
import os

class AlertWithNotification(BreakoutEntryAlerts):
    def _alert(self, signal):
        super()._alert(signal)
        # Send desktop notification
        title = f'BREAKOUT: {signal.symbol}'
        message = f'{signal.symbol} at \${signal.entry_price:.2f} - Volume {signal.rvol:.1f}x - BUY NOW!'
        os.system(f\"osascript -e 'display notification \\\"{message}\\\" with title \\\"{title}\\\" sound name \\\"Glass\\\"'\")

symbols = ['F', 'KMI', 'NOK', 'T', 'BAC', 'SOFI', 'PLTR', 'AMC', 'GME',
           'RIVN', 'LCID', 'UBER', 'AAL', 'CCL', 'XOM', 'OXY', 'MPC', 'VLO']

monitor = AlertWithNotification()
monitor.run_continuous_monitoring(symbols, interval_seconds=300)
"
