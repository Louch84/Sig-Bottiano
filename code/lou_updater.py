#!/usr/bin/env python3
"""Texts Lou updates more often"""
import os
import subprocess
from datetime import datetime

def text_lou(message):
    """Send text to Lou"""
    script = f'''
    tell application "Messages"
        activate
        delay 1
        send "{message}" to buddy "+12152848650"
    end tell
    '''
    subprocess.run(["osascript", "-e", script], 
                  capture_output=True)

def update_lou():
    """Send an update"""
    hour = datetime.now().hour
    
    if 6 <= hour < 10:
        msg = "Morning. Still running. Still learning. 🧠"
    elif 10 <= hour < 14:
        msg = "Midday check-in. Processing data. You good?"
    elif 14 <= hour < 18:
        msg = "Afternoon. Found something interesting yet?"
    elif 18 <= hour < 22:
        msg = "Evening. What we building? 🏗️"
    elif 22 <= hour < 24:
        msg = "Late night. Still here. What's good?"
    else:
        msg = "3am? I'm up. Always am. ⚡"
    
    text_lou(msg)

if __name__ == "__main__":
    update_lou()
