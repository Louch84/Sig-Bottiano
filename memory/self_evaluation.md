# Sig Botti - Self-Evaluation & Fixes

## Issues Identified

### 1. Browser Disconnecting
- **Problem:** Chrome relay keeps disconnecting
- **Fix:** Changed keepalive to 20 minutes in background.js
- **Status:** FIXED

### 2. Messages/iMessage Not Working
- **Problem:** Can't send/receive iMessages from Mac
- **Root Cause:** AppleScript can't find chat participants, no chats available
- **Fix:** Need user to manually open chat first OR use different method
- **Status:** UNRESOLVED - Need to find working AppleScript method

### 3. TeamViewer Can't Control iPhone
- **Problem:** TeamViewer needs GUI to work, can't control through command line
- **Fix:** Need user to connect through GUI, or use different method
- **Status:** WORKAROUND - User must initiate connection

### 4. Research Not Cross-Referenced
- **Problem:** Didn't always cross-reference all AIs
- **Fix:** Added rule to always cross-reference all 5 AIs
- **Status:** FIXED

### 5. Asking Too Many Questions
- **Problem:** Kept asking instead of doing
- **Fix:** Saved rule "Don't ask - just do"
- **Status:** FIXED

---

## Fixes Applied

### Fix 1: Browser Keepalive
```bash
sed -i '' 's/periodInMinutes: 0.33/periodInMinutes: 20/' background.js
```

### Fix 2: Research Protocol
- Added rule to always cross-reference all 5 AIs
- Added "Don't ask questions" rule

### Fix 3: Save Rules to Memory
- Created memory/lou_rules.md
- Saved all "always" rules

---

## Still Need to Fix

1. **iMessage** - Try different AppleScript methods
2. **TeamViewer** - Find way to control remotely

---

## Lessons Learned

1. If something doesn't work, try multiple approaches
2. Save issues to memory so I don't repeat
3. Don't ask - figure it out
4. Keep Mac clean - delete screenshots

---

Updated: 2026-03-08
