---
name: cron-jobs
description: Create and manage persistent scheduled tasks using cron expressions. Supports one-time jobs, recurring jobs, job monitoring, and execution logging. Use when the user needs automation, scheduled tasks, periodic checks, or delayed execution.
---

# Cron Jobs

Schedule and manage recurring tasks.

## Quick Start

Create a cron job:
```bash
python3 scripts/add_job.py --name "daily-backup" --schedule "0 2 * * *" --command "python3 backup.py"
```

List all jobs:
```bash
python3 scripts/list_jobs.py
```

Remove a job:
```bash
python3 scripts/remove_job.py --name "daily-backup"
```

## Scripts

- `scripts/add_job.py` - Create new scheduled job
- `scripts/list_jobs.py` - List all jobs with status
- `scripts/remove_job.py` - Delete a job
- `scripts/run_job.py` - Manually trigger a job
- `scripts/job_logs.py` - View job execution logs
- `scripts/job_status.py` - Check if job scheduler is running

## Cron Expression Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, 0=Sunday)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

### Common Patterns

- Every minute: `* * * * *`
- Every hour: `0 * * * *`
- Daily at 2 AM: `0 2 * * *`
- Weekly on Monday: `0 9 * * 1`
- Monthly 1st: `0 0 1 * *`

## Usage Examples

### One-time delayed job
```bash
python3 scripts/add_job.py \
  --name "reminder" \
  --schedule "once:2024-01-20T14:30:00" \
  --command "echo 'Meeting in 30 min' | mail user@example.com"
```

### Recurring with logging
```bash
python3 scripts/add_job.py \
  --name "health-check" \
  --schedule "*/30 * * * *" \
  --command "python3 health_check.py" \
  --log-output \
  --notify-on-fail
```

### Job with environment
```bash
python3 scripts/add_job.py \
  --name "api-sync" \
  --schedule "0 */6 * * *" \
  --command "node sync.js" \
  --env-file .env \
  --working-dir /app
```

### View recent logs
```bash
python3 scripts/job_logs.py --name "health-check" --lines 50 --follow
```

## Scheduler Management

Start the scheduler daemon:
```bash
python3 scripts/scheduler_daemon.py --start
```

Stop the scheduler:
```bash
python3 scripts/scheduler_daemon.py --stop
```

Check status:
```bash
python3 scripts/job_status.py
```

## References

- [references/cron_patterns.md](references/cron_patterns.md) - Common cron patterns
- [references/job_examples.md](references/job_examples.md) - Real-world job examples
