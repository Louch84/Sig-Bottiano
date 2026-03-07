# Memory Importance System

## Priority Levels

### HIGH (Never decay)
- User preferences
- Business details (Luchiano Wireless, Spring Finds)
- Core identity
- Long-term goals
- Recurring tasks

### MEDIUM (Review monthly)
- Project details
- Technical decisions
- Conversation context
- Active tasks

### LOW (Can decay)
- Temporary troubleshooting
- One-off questions
- Test outputs
- Session-specific context

## Auto-Retention Rules
- HIGH: Keep forever
- MEDIUM: Archive after 30 days to separate file
- LOW: Keep only in daily log, prune after 7 days

## Implementation
- When storing memory, add priority tag
- During heartbeat, check for items to archive/prune
