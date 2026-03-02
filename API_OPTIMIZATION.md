# API Optimization Playbook

## Core Principle
**1 phone sale = weeks of API credits.** Every call counts.

---

## 🎯 Optimization Strategies

### 1. Search Hierarchy (Cheapest → Most Expensive)
```
1. Local files (FREE) - Check workspace first
2. memory_search (FREE) - Semantic search our own data
3. ollama_web_search (FREE) - Ollama's search API
4. web_search (COSTS) - Brave API - LAST RESORT
5. web_fetch (COSTS) - Only if page content needed
```

### 2. File Operation Rules
- **Read:** Use `offset/limit` for large files, don't read full file unless needed
- **Write:** Batch multiple updates into one write, not 5 small writes
- **Edit:** Use `edit` for small changes (saves tokens vs full rewrite)
- **Cache:** After first web search, save results to `/business/cache/` for reuse

### 3. Memory System Efficiency
- **Search first:** Always `memory_search` before `memory_get`
- **Batch reads:** Read full daily file once, not 3 partial reads
- **Append-only:** Never overwrite, always append (saves re-reading context)
- **Smart indexing:** Use headers like `## 📱 Phones`, `## 💰 Prices` for faster search

### 4. Response Efficiency
- **Be concise:** Less tokens out = less tokens in next turn
- **Batch operations:** Do 3 file writes in one turn, not 3 separate turns
- **Skip unnecessary tool calls:** Don't call tools just to narrate
- **NO_REPLY when done:** Don't send duplicate confirmations

### 5. Sub-agent Strategy
- **Use for:** Heavy research, parallel tasks, complex analysis
- **Avoid for:** Simple file ops, quick searches, one-step tasks
- **Cost awareness:** Each sub-agent = separate API session

### 6. Local-First Knowledge Base
Build these reference files (FREE to read anytime):
- `/business/QUICK_PRICE_REFERENCE.md` ✅ Created
- `/business/SUPPLIER_CACHE.md` - Save supplier searches here
- `/business/CUSTOMER_FAQS.md` - Common questions + answers
- `/business/COMPETITOR_PRICING.md` - Market research cache

### 7. Smart Defaults
```markdown
- web_search count: 5 (not 10) - only get what you need
- memory_search maxResults: 5 (not 20) - top results usually enough
- web_fetch maxChars: 5000 (not full page) - extract key info only
- ollama_web_search: DEFAULT for all web searches (free)
```

---

## 📊 Token Budget Tracking

### Daily Limits (Self-Imposed)
| Operation | Daily Limit | Cost Priority |
|-----------|-------------|---------------|
| web_search (Brave) | 5 calls | 🔴 High |
| web_fetch | 10 calls | 🟡 Medium |
| ollama_web_search | Unlimited | 🟢 FREE |
| memory_search | Unlimited | 🟢 FREE |
| File ops | Unlimited | 🟢 FREE |

### Before Any API Call, Ask:
1. Is this info already in our workspace?
2. Can I use ollama_web_search instead?
3. Do I need this NOW or can it wait?
4. Can I batch this with other calls?

---

## 🚀 Quick Wins Implemented

### ✅ Done
- Switched default search to `ollama_web_search` (free)
- Created price reference card (no re-searching prices)
- Memory append-only system (saves re-reading)
- Unified WhatsApp guide (one reference, not scattered)

### 🔄 In Progress
- Build supplier cache (save LCD supplier searches)
- Create FAQ cache (common customer questions)
- Add search result caching to `/business/cache/`

### 📋 Future Optimizations
- Pre-compute common responses (templates)
- Build local supplier database (scrape once, reference forever)
- Create price tracking sheet (update weekly, not per-query)

---

## 💡 Pro Tips

1. **Morning cache check:** Before any research, check `/business/cache/` first
2. **End-of-day save:** After any web search, cache results to file
3. **Batch thinking:** "What else do I need?" before making calls
4. **File > API:** If it can be a file, make it a file

---

## 🧠 Mindset Shift

**Before:** "Let me search for that"
**After:** "Do we already have this locally?"

**Before:** 10 web searches to build knowledge
**After:** 1 web search + save to cache + reference forever

**Revenue funds API.** Every optimization = more profit margin.
