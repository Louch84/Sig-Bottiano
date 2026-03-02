# Business Cache Directory

**Purpose:** Store search results, supplier info, and research data to avoid repeat API calls.

## Cache Rules
1. After ANY web search → save results here
2. Before ANY search → check here first
3. Format: `YYYY-MM-DD_search-topic.md`
4. Include: Source URLs, key data, date fetched

## Current Cache Files

### LCD Suppliers (2026-03-01)
- File: `lcd-suppliers-usa.md`
- Sources: iPhoneLCD.net, SLcells, Lcdfactories.com
- Status: Ready for reference

### Price Data
- File: `iphone-prices-africa-usa.md`
- Source: User's supplier list + market research
- Location: Also in `/business/QUICK_PRICE_REFERENCE.md`

---

## How to Cache (Template)

```markdown
# [Topic] - [Date]

## Sources
- URL 1
- URL 2

## Key Data
[Copy/paste or summarize findings]

## Action Items
[What we learned / next steps]

## Cached
[Date] - By [agent]
```

---

**NEVER search twice for the same thing.** Cache it.
