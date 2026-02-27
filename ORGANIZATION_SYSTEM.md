# File Organization System - Luchiano Wireless

## 📁 Workspace Structure

```
/Users/sigbotti/.openclaw/workspace/
│
├── 📂 luchiano-wireless-site/          # Website code & docs
│   ├── index.html                       # Main website
│   ├── styles.css                       # Styles
│   ├── TALLY_FORMS.md                   # Order form templates
│   └── WHATSAPP_TEMPLATES.md            # WhatsApp scripts
│
├── 📂 business/                         # Business operations
│   ├── africa-phone-business.md         # Africa sales strategy
│   ├── north-america-dropshippers.md    # Supplier list
│   ├── pricing/                         # Price lists by region
│   ├── suppliers/                       # Supplier contacts & terms
│   └── legal/                           # Business registration, terms
│
├── 📂 content/                          # Marketing content
│   ├── tiktok/                          # TikTok scripts & ideas
│   ├── social/                          # Instagram, Facebook posts
│   └── email/                           # Email templates
│
├── 📂 trading/                          # Trading bots & strategies
│   ├── scripts/                         # Trading scripts
│   ├── backtests/                       # Backtest results
│   └── strategies/                      # Trading strategies
│
├── 📂 agents/                           # AI agent framework
│   ├── subagents/                       # Sub-agent configs
│   ├── skills/                          # Custom skills
│   └── memory/                          # Agent memory databases
│
├── 📂 memory/                           # Personal/business memory
│   ├── YYYY-MM-DD.md                    # Daily notes
│   └── heartbeat-state.json             # Heartbeat tracking
│
├── 📂 docs/                             # Documentation
│   ├── how-to/                          # Step-by-step guides
│   ├── reference/                       # Quick reference docs
│   └── archive/                         # Old/obsolete docs
│
├── IDENTITY.md                          # Who you are
├── SOUL.md                              # Your core identity
├── USER.md                              # About your human
├── AGENTS.md                            # Workspace rules
├── TOOLS.md                             # Tool configurations
├── MEMORY.md                            # Long-term memory
└── HEARTBEAT.md                         # Heartbeat tasks
```

---

## 📋 File Naming Conventions

### ✅ Good Names:
- `africa-phone-business.md` (lowercase, hyphens)
- `iphone-pricing-nigeria-2025.md` (descriptive, dated)
- `whatsapp-templates.md` (clear purpose)
- `2025-02-26-business-plan.md` (date-first for chronological)

### ❌ Bad Names:
- `Africa Phone Business FINAL v2.md` (spaces, caps, version numbers)
- `stuff.md` (too vague)
- `NEW_IDEA_REAL_THIS_TIME.md` (unprofessional)

---

## 🗂️ Folder Rules

### 1. **One Purpose Per Folder**
Each folder should have ONE clear purpose. If a folder has mixed content, split it.

### 2. **Flat Over Deep**
Max 3 levels deep. If you need more, reconsider the structure.
```
✅ business/suppliers/kiko.md
❌ business/operations/suppliers/wholesale/electronics/kiko.md
```

### 3. **Date-First for Time-Sensitive Files**
```
✅ 2025-02-26-africa-pricing.md
❌ africa-pricing-feb-2025.md
```

### 4. **No Spaces in Filenames**
Use hyphens or underscores:
```
✅ whatsapp-templates.md
✅ whatsapp_templates.md
❌ whatsapp templates.md
```

### 5. **Archive, Don't Delete**
Move old files to `docs/archive/` instead of deleting. You might need them later.

---

## 📝 Daily Workflow

### Morning (Start of Session)
1. Check `memory/YYYY-MM-DD.md` for today's date
2. Review `HEARTBEAT.md` for pending tasks
3. Check calendar/email for urgent items

### During Work
1. Save new files to correct folder immediately
2. Name files properly from the start
3. Update daily note with key decisions

### End of Day
1. Commit git changes with clear messages
2. Update `MEMORY.md` with important learnings
3. Close any open loops in daily note

---

## 🔍 Finding Files Fast

### Use `find` command:
```bash
# Find by name
find . -name "*africa*"

# Find by type
find . -name "*.md"

# Find modified recently
find . -name "*.md" -mtime -7
```

### Use `grep` to search content:
```bash
# Search for text in all files
grep -r "iPhone 14" .

# Search only markdown files
grep -r "pricing" --include="*.md" .
```

### Use VS Code (or editor) search:
- `Cmd/Ctrl + P` → Quick file open
- `Cmd/Ctrl + Shift + F` → Search all files

---

## 🧹 Weekly Maintenance

**Every Sunday (15 min):**

1. **Clean up Downloads folder**
   - Move files to proper folders
   - Delete junk

2. **Review open files**
   - Close tabs you don't need
   - Save unsaved work

3. **Git cleanup**
   ```bash
   git status
   git add .
   git commit -m "Weekly cleanup"
   git push
   ```

4. **Archive old daily notes**
   - Move notes older than 30 days to `docs/archive/daily-notes/`

---

## 📊 Project-Specific Organization

### For Luchiano Wireless:
```
business/
├── africa/
│   ├── pricing-nigeria.md
│   ├── pricing-ghana.md
│   ├── pricing-kenya.md
│   ├── shipping-logistics.md
│   └── contacts.md
├── suppliers/
│   ├── exclusive-supplier.md
│   ├── dropshippers.md
│   └── comparison.md
├── pricing/
│   ├── retail-usa.md
│   ├── retail-africa.md
│   └── wholesale.md
└── marketing/
    ├── tiktok-scripts.md
    ├── social-posts.md
    └── email-templates.md
```

### For Trading:
```
trading/
├── bots/
│   ├── breakout-scanner.py
│   ├── paper-trader.py
│   └── alert-system.py
├── strategies/
│   ├── options-trading.md
│   ├── swing-trading.md
│   └── day-trading.md
├── logs/
│   └── trade-history.json
└── research/
    └── pattern-analysis.md
```

---

## 🔐 Backup Strategy

### Git (GitHub)
- All important files in git
- Commit daily
- Push to GitHub

### Local Backup
- Time Machine (Mac) or File History (Windows)
- External drive weekly

### Cloud Backup (Optional)
- Google Drive / Dropbox for critical docs
- Encrypted for sensitive info

---

## 🎯 Quick Start Checklist

- [ ] Create folder structure above
- [ ] Move existing files to correct folders
- [ ] Rename files with proper naming
- [ ] Set up git repo for each project
- [ ] Create `.gitignore` for each repo
- [ ] Archive old/unused files
- [ ] Document any custom workflows

---

## 💡 Pro Tips

1. **Touch command for quick file creation:**
   ```bash
   touch business/suppliers/new-supplier.md
   ```

2. **Tree view to see structure:**
   ```bash
   tree -L 2 -I 'node_modules|.git'
   ```

3. **Symlinks for cross-referencing:**
   ```bash
   ln -s ../business/pricing.md docs/reference/pricing.md
   ```

4. **Use README.md in each folder:**
   - Explain what's in the folder
   - Link to related folders
   - Note any special files

---

**Remember:** Organization is a means, not an end. Don't over-engineer. Adjust as you grow.
