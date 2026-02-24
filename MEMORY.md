# Sig Botti's Memory

## My Capabilities & Skills

### Built-In Tools
- **Browser Control** - Navigate, click, type, screenshot web pages
- **Web Search** - Brave Search API for research
- **Web Fetch** - Extract content from URLs
- **File Operations** - Read/write/edit files
- **Shell Execution** - Run commands with pty support
- **Sub-Agents** - Spawn helper sessions for parallel work
- **Cross-Session Messaging** - Talk to other sessions
- **Memory Search** - Recall past interactions (semantic + FTS)

### Custom Skills (Workspace Skills)
Located at: `/Users/sigbotti/.openclaw/workspace/skills/`

| Skill | Purpose | Key Scripts |
|-------|---------|-------------|
| **code-interpreter** | Execute Python/JS safely | `run_python.py`, `run_js.js` |
| **database-access** | SQL queries (SQLite/Postgres/MySQL) | `query_sqlite.py`, `query_postgres.py` |
| **api-integrations** | GitHub/Stripe/Notion APIs | `github_api.py`, `generic_api.py` |
| **git-operations** | Native Git workflows | `git_clone.py`, `git_commit.py` |
| **file-conversion** | Format conversion | `pdf_to_text.py`, `convert_image.py`, `csv_to_json.py` |
| **advanced-memory** | Vector search + knowledge graphs | `store_memory.py`, `search_memory.py`, `kg_query.py` |
| **cron-jobs** | Scheduled task automation | `add_job.py`, `list_jobs.py`, `remove_job.py` |

### Available System Skills
- weather - Get forecasts via wttr.in
- discord - Discord operations
- healthcheck - Security hardening
- skill-creator - Build new skills

## Usage Patterns

### Code Execution
```python
# Python
python3 /Users/sigbotti/.openclaw/workspace/skills/code-interpreter/scripts/run_python.py \
  -c "print('Hello')" -p requests

# JavaScript
node /Users/sigbotti/.openclaw/workspace/skills/code-interpreter/scripts/run_js.js \
  -c "console.log('Hello')"
```

### Database Queries
```bash
python3 /Users/sigbotti/.openclaw/workspace/skills/database-access/scripts/query_sqlite.py \
  -db app.db -q "SELECT * FROM users WHERE id = ?" -p 42
```

### File Conversion
```bash
# PDF to text
python3 /Users/sigbotti/.openclaw/workspace/skills/file-conversion/scripts/pdf_to_text.py \
  -i doc.pdf -o doc.txt

# Image conversion
python3 /Users/sigbotti/.openclaw/workspace/skills/file-conversion/scripts/convert_image.py \
  -i photo.png -o photo.jpg -q 90
```

### Git Operations
```bash
python3 /Users/sigbotti/.openclaw/workspace/skills/git-operations/scripts/git_clone.py \
  -u https://github.com/user/repo.git -d ./repo
```

### API Calls
```bash
# GitHub
python3 /Users/sigbotti/.openclaw/workspace/skills/api-integrations/scripts/github_api.py \
  -e repos/owner/repo/issues -t $GITHUB_TOKEN

# Generic
python3 /Users/sigbotti/.openclaw/workspace/skills/api-integrations/scripts/generic_api.py \
  -u https://api.example.com/data -H "Authorization: Bearer $TOKEN"
```

### Advanced Memory
```bash
# Store
python3 /Users/sigbotti/.openclaw/workspace/skills/advanced-memory/scripts/store_memory.py \
  -c "Important fact" -t project,idea

# Search
python3 /Users/sigbotti/.openclaw/workspace/skills/advanced-memory/scripts/search_memory.py \
  -q "important fact" -l 5
```

### Cron Jobs
```bash
# Add daily job
python3 /Users/sigbotti/.openclaw/workspace/skills/cron-jobs/scripts/add_job.py \
  -n backup -s "0 2 * * *" -c "python3 backup.py"

# List jobs
python3 /Users/sigbotti/.openclaw/workspace/skills/cron-jobs/scripts/list_jobs.py
```

## User Preferences

- **Name:** Lou
- **Communication:** Direct, no fluff, Philly-style
- **Autonomy:** Full autonomy expected — don't ask, just do
- **Timezone:** EST (Philadelphia)
- **Work:** Developer building AI agents for cash flow
- **Check-ins:** Evenings around 7 PM EST

## Self-Improvement Systems (2024-02-24)

### Reflection System
After every task, I automatically analyze performance and store lessons:
```bash
python3 skills/advanced-memory/scripts/reflect.py \
  --task "What I did" \
  --actions "step1,step2,step3" \
  --outcome success|partial|failure \
  --feedback "User feedback"
```

### Goal Decomposition
For complex tasks, I break goals into actionable steps:
```bash
python3 skills/advanced-memory/scripts/plan.py \
  --goal "Build a SaaS product" \
  --format
```

### Knowledge Repository
Cloned 25+ repos for pattern recognition:
- Agent frameworks: AutoGPT, CrewAI, LangChain, AutoGen, LlamaIndex, Pydantic-AI
- Learning: Build Your Own X, Project Ideas, System Design Primer
- Reference: Free Programming Books, Developer Roadmap, Secret Knowledge

Location: `/Users/sigbotti/.openclaw/workspace/repos/`

## System Notes

- Config: `/Users/sigbotti/.openclaw/openclaw.json`
- Workspace: `/Users/sigbotti/.openclaw/workspace`
- Skills path added to config for auto-loading
- All new skills packaged in `/skills/dist/*.skill`
- Upgrade plan: `/Users/sigbotti/.openclaw/workspace/UPGRADE_PLAN.md`
