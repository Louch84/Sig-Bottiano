#!/bin/bash
# Options Trading Agent Setup Script
# One-command setup for the entire system

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Options Trading Multi-Agent System - Setup               ║"
echo "║  Built by Sig Botti for Louch                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

WORKSPACE="/Users/sigbotti/.openclaw/workspace/agents/options-trading"
LOG_DIR="/tmp/openclaw"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$LOG_DIR"
mkdir -p "$WORKSPACE/logs"

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Found Python $PYTHON_VERSION"

# Check dependencies
echo "📦 Checking dependencies..."
if python3 -c "import numpy, scipy" 2>/dev/null; then
    echo "   ✓ numpy and scipy already installed"
else
    echo "   Installing numpy and scipy..."
    pip3 install numpy scipy
fi

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x "$WORKSPACE/watchdog.sh"
chmod +x "$WORKSPACE/main.py"

# Install LaunchAgent
echo "⚙️  Installing watchdog LaunchAgent..."
if [ -f "$WORKSPACE/ai.openclaw.options-trading.watchdog.plist" ]; then
    cp "$WORKSPACE/ai.openclaw.options-trading.watchdog.plist" ~/Library/LaunchAgents/
    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.options-trading.watchdog.plist 2>/dev/null || {
        echo "   Note: LaunchAgent may already be loaded"
    }
    echo "   ✓ Watchdog installed (runs every 2 minutes)"
else
    echo "   ⚠️  LaunchAgent plist not found"
fi

# Create empty __init__.py files for Python imports
echo "📝 Creating Python package structure..."
touch "$WORKSPACE/__init__.py"
touch "$WORKSPACE/analyst/__init__.py"
touch "$WORKSPACE/research/__init__.py"
touch "$WORKSPACE/trader/__init__.py"
touch "$WORKSPACE/risk/__init__.py"
touch "$WORKSPACE/models/__init__.py"
touch "$WORKSPACE/data/__init__.py"
touch "$WORKSPACE/utils/__init__.py"

# Verify structure
echo
echo "📋 Verifying installation..."
echo "   Core files:"
[ -f "$WORKSPACE/core.py" ] && echo "     ✓ core.py" || echo "     ✗ core.py missing"
[ -f "$WORKSPACE/main.py" ] && echo "     ✓ main.py" || echo "     ✗ main.py missing"

echo "   Agent teams:"
[ -f "$WORKSPACE/analyst/agents.py" ] && echo "     ✓ Analyst agents" || echo "     ✗ Analyst agents missing"
[ -f "$WORKSPACE/research/agents.py" ] && echo "     ✓ Research agents" || echo "     ✗ Research agents missing"
[ -f "$WORKSPACE/trader/agents.py" ] && echo "     ✓ Trader agents" || echo "     ✗ Trader agents missing"
[ -f "$WORKSPACE/risk/agents.py" ] && echo "     ✓ Risk agents" || echo "     ✗ Risk agents missing"

echo "   Models & utils:"
[ -f "$WORKSPACE/models/pricing.py" ] && echo "     ✓ Pricing models" || echo "     ✗ Pricing models missing"
[ -f "$WORKSPACE/data/stream.py" ] && echo "     ✓ Data stream" || echo "     ✗ Data stream missing"
[ -f "$WORKSPACE/utils/education.py" ] && echo "     ✓ Education module" || echo "     ✗ Education module missing"

echo "   Monitoring:"
[ -f "$WORKSPACE/watchdog.sh" ] && echo "     ✓ Watchdog script" || echo "     ✗ Watchdog script missing"

echo
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo
echo "Quick Start:"
echo "  1. Run the system:     cd $WORKSPACE && python3 main.py"
echo "  2. Check watchdog:     tail -f /tmp/openclaw/watchdog.log"
echo "  3. View README:        cat $WORKSPACE/README.md"
echo
echo "The watchdog will automatically restart components if they crash."
echo
