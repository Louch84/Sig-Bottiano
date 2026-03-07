# Self-Healing Playbook

## Purpose
Document errors + successful fixes for automatic recovery.

## Error → Fix Mappings

### Browser Connection Dropped
- **Error:** "tab not found" / "relay not reachable"
- **Fix:** User clicks extension icon to reconnect
- **Prevention:** Keep user in same tab

### API Errors
- **401:** Invalid key → flag, don't retry
- **429:** Rate limit → backoff 60s, retry once
- **500:** Server error → retry after 10s

### Memory Search Failed
- **Error:** OpenAI embeddings 401
- **Fix:** Use file-based search instead
- **Prevention:** N/A - file memory is fallback

## Auto-Fix Attempts (Before Reporting)
1. Retry with exponential backoff (10s, 30s, 60s)
2. Fall to alternative tool (browser → web_fetch → web_search)
3. Log to shadow_learning.md if persistent failure
