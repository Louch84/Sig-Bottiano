# Cron Patterns Reference

## Common Schedules

| Schedule | Description |
|----------|-------------|
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 9 * * 1-5` | 9 AM weekdays |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |

## Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6, 0=Sunday)
│ │ │ │ │
* * * * *
```

## Special Strings

- `@yearly` - Once per year
- `@monthly` - Once per month
- `@weekly` - Once per week
- `@daily` - Once per day
- `@hourly` - Once per hour
