---
name: git-operations
description: Native Git version control operations including clone, init, add, commit, push, pull, branch, merge, status, log, and diff. Supports SSH and token-based authentication. Use when managing Git repositories, automating Git workflows, or performing version control tasks.
---

# Git Operations

Execute Git commands with proper error handling and authentication.

## Quick Start

Clone a repository:
```bash
python3 scripts/git_clone.py --url https://github.com/user/repo.git --dest ./repo
```

Check status:
```bash
python3 scripts/git_status.py --repo ./repo
```

Commit changes:
```bash
python3 scripts/git_commit.py --repo ./repo --message "Update files"
```

## Scripts

- `scripts/git_clone.py` - Clone repositories
- `scripts/git_init.py` - Initialize new repo
- `scripts/git_status.py` - Check working tree status
- `scripts/git_add.py` - Stage files
- `scripts/git_commit.py` - Commit changes
- `scripts/git_push.py` - Push to remote
- `scripts/git_pull.py` - Pull from remote
- `scripts/git_branch.py` - Manage branches
- `scripts/git_merge.py` - Merge branches
- `scripts/git_log.py` - View commit history
- `scripts/git_diff.py` - Show differences

## Authentication

### SSH Keys
Use your existing SSH keys at `~/.ssh/id_rsa` or specify with `--key`.

### Personal Access Tokens
```bash
export GITHUB_TOKEN=ghp_xxx
python3 scripts/git_clone.py --url https://github.com/user/repo.git --token $GITHUB_TOKEN
```

## Usage Examples

### Full workflow
```bash
python3 scripts/git_clone.py --url git@github.com:user/repo.git --dest ./myrepo
python3 scripts/git_add.py --repo ./myrepo --files "*.py"
python3 scripts/git_commit.py --repo ./myrepo --message "Add Python scripts"
python3 scripts/git_push.py --repo ./myrepo --branch main
```

### Create and switch branch
```bash
python3 scripts/git_branch.py --repo ./myrepo --create feature-branch
python3 scripts/git_branch.py --repo ./myrepo --switch feature-branch
```

### View log with graph
```bash
python3 scripts/git_log.py --repo ./myrepo --graph --oneline -10
```

## References

See [references/git_workflows.md](references/git_workflows.md) for common Git workflows and patterns.
