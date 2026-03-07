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

---

## Proactive Learning System (From Perplexity Ideas)

### 1. Temporal Sense of Time
- Track when Lou is active (trading research evenings around 7pm)
- Note when he responds quickly vs ignores
- Use patterns to predict best times to act

### 2. Self-Generated Goals
- Infer implicit goals from conversation history
- Example: If researching short squeezes → goal: build scanner
- Break into subtasks: research → implement → test → report

### 3. Environment-Aware Execution
- Have controlled access to tools (filesystem, browser, code)
- Trigger workflows on state changes
- Use plan-then-act with safety checks

### 4. Continuous Learning from Feedback
- Log every action + Lou's response
- Self-review sessions weekly
- Adjust behavior based on explicit + implicit feedback

### 5. Multi-Agent Architecture
- Spawn specialist sub-agents: researcher, coder, analyst
- Coordinate through main session
- Only escalate to Lou for high-impact decisions
