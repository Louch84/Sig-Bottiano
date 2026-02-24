---
name: api-integrations
description: Standardized API connectivity for GitHub, Stripe, Notion, and other common services. Supports authentication, rate limiting, pagination, and webhook handling. Use when integrating with third-party APIs or automating service interactions.
---

# API Integrations

Unified interface for popular APIs.

## Quick Start

GitHub:
```bash
python3 scripts/github_api.py --endpoint repos/owner/repo/issues --method GET
```

Stripe:
```bash
python3 scripts/stripe_api.py --endpoint customers --method POST --data '{"email": "user@example.com"}'
```

Notion:
```bash
python3 scripts/notion_api.py --endpoint databases --method GET
```

## Scripts

- `scripts/github_api.py` - GitHub REST API client
- `scripts/stripe_api.py` - Stripe API client
- `scripts/notion_api.py` - Notion API client
- `scripts/generic_api.py` - Generic HTTP API client for other services

## Authentication

Store tokens in environment variables:
```bash
export GITHUB_TOKEN=ghp_xxx
export STRIPE_KEY=sk_xxx
export NOTION_TOKEN=secret_xxx
```

Or use `--token` flag.

## Usage Examples

### GitHub - List issues
```bash
python3 scripts/github_api.py --endpoint repos/owner/repo/issues --params '{"state": "open"}'
```

### Stripe - Create customer
```bash
python3 scripts/stripe_api.py --endpoint customers --method POST --data '{"email": "test@example.com", "name": "Test User"}'
```

### Notion - Query database
```bash
python3 scripts/notion_api.py --endpoint databases/DB_ID/query --method POST --data '{"filter": {"property": "Status", "select": {"equals": "Done"}}}'
```

### Generic API
```bash
python3 scripts/generic_api.py --url https://api.example.com/v1/resource --header "Authorization: Bearer $TOKEN"
```

## References

- [references/github_patterns.md](references/github_patterns.md) - GitHub API patterns
- [references/stripe_patterns.md](references/stripe_patterns.md) - Stripe API patterns
- [references/notion_patterns.md](references/notion_patterns.md) - Notion API patterns
