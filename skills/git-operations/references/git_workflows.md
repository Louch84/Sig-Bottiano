# Git Workflows

## Feature Branch Workflow

1. Create feature branch
2. Make commits
3. Push to remote
4. Create pull request
5. Merge to main

## Common Patterns

### Stash changes
```bash
git stash push -m "description"
git stash pop
git stash list
```

### Undo last commit
```bash
git reset --soft HEAD~1  # Keep changes
git reset --hard HEAD~1  # Discard changes
```

### Interactive rebase
```bash
git rebase -i HEAD~3
```

## Best Practices

1. Commit often with clear messages
2. Pull before pushing
3. Use branches for features/bugs
4. Review changes before committing
