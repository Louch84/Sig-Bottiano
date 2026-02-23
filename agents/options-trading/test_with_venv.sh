#!/bin/bash
# Test Real Data with Virtual Environment

cd /Users/sigbotti/.openclaw/workspace/agents/options-trading

# Activate virtual environment
source venv/bin/activate

# Run test
python3 test_real_data.py
