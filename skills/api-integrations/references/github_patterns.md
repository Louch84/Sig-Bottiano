# GitHub API Patterns

## Authentication
Use Personal Access Token with `repo` scope.

## Common Operations

### List Issues
```bash
python3 scripts/github_api.py -e repos/owner/repo/issues -p '{"state":"open"}'
```

### Create Issue
```bash
python3 scripts/github_api.py -e repos/owner/repo/issues -m POST \
  -d '{"title":"Bug","body":"Description"}'
```

### Get Rate Limit
```bash
python3 scripts/github_api.py -e rate_limit
```

## Pagination
API returns 30 items by default. Use `?page=2&per_page=100` for more.

## Best Practices

1. Cache responses to avoid rate limits
2. Use appropriate scopes for tokens
3. Handle 404 errors gracefully
4. Check rate limit headers
