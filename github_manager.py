#!/usr/bin/env python3
"""
GitHub Manager - Auto version control for AI workspace
Handles commits, pushes, issues, and repo management
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

class GitHubManager:
    """
    Manages GitHub integration for the workspace
    Auto-commits changes, tracks versions, creates issues
    """
    
    def __init__(self, workspace_path: str = "/Users/sigbotti/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.git_dir = self.workspace / ".git"
        
    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run git command in workspace"""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=False
        )
        
        if check and result.returncode != 0:
            print(f"⚠️ Git command failed: {' '.join(args)}")
            print(f"   Error: {result.stderr}")
        
        return result
    
    def is_repo_initialized(self) -> bool:
        """Check if git repo exists"""
        return self.git_dir.exists()
    
    def init_repo(self) -> bool:
        """Initialize git repo if not exists"""
        if self.is_repo_initialized():
            print("✅ Git repo already initialized")
            return True
        
        result = self._run_git(["init"], check=False)
        
        if result.returncode == 0:
            print("✅ Git repo initialized")
            return True
        else:
            print("❌ Failed to initialize git repo")
            return False
    
    def set_remote(self, repo_url: str) -> bool:
        """Set GitHub remote origin"""
        # Check if remote exists
        result = self._run_git(["remote", "get-url", "origin"], check=False)
        
        if result.returncode == 0:
            # Remote exists, update it
            self._run_git(["remote", "set-url", "origin", repo_url], check=False)
        else:
            # Add new remote
            self._run_git(["remote", "add", "origin", repo_url], check=False)
        
        print(f"✅ Remote set to: {repo_url}")
        return True
    
    def get_changed_files(self) -> List[str]:
        """Get list of modified files"""
        result = self._run_git(["status", "--porcelain"], check=False)
        
        if result.returncode != 0:
            return []
        
        files = []
        for line in result.stdout.strip().split('\n'):
            if line:
                # Format: XY filename (X=staged, Y=unstaged)
                files.append(line[3:])
        
        return files
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        files = self.get_changed_files()
        return len(files) > 0
    
    def commit_all(self, message: Optional[str] = None, auto_message: bool = True) -> bool:
        """
        Stage and commit all changes
        
        Args:
            message: Custom commit message
            auto_message: Generate message from changed files
        """
        if not self.has_changes():
            print("ℹ️ No changes to commit")
            return False
        
        # Stage all changes
        self._run_git(["add", "."], check=False)
        
        # Generate commit message
        if message is None and auto_message:
            files = self.get_changed_files()
            if len(files) == 1:
                message = f"Update {files[0]}"
            elif len(files) <= 5:
                message = f"Update {', '.join(files[:3])}..."
            else:
                message = f"Update {len(files)} files"
        elif message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"Auto-commit at {timestamp}"
        
        # Commit
        result = self._run_git(["commit", "-m", message], check=False)
        
        if result.returncode == 0:
            print(f"✅ Committed: {message}")
            return True
        else:
            print(f"❌ Commit failed")
            return False
    
    def push(self, branch: str = "main") -> bool:
        """Push to GitHub"""
        # Check if remote exists
        result = self._run_git(["remote", "get-url", "origin"], check=False)
        if result.returncode != 0:
            print("❌ No remote configured. Run set_remote() first.")
            return False
        
        # Push
        result = self._run_git(["push", "-u", "origin", branch], check=False)
        
        if result.returncode == 0:
            print(f"✅ Pushed to {branch}")
            return True
        else:
            # Try with force (if needed)
            print("⚠️ Push failed, trying force...")
            result = self._run_git(["push", "-u", "origin", branch, "--force"], check=False)
            return result.returncode == 0
    
    def auto_commit_and_push(self, message: Optional[str] = None) -> bool:
        """One-shot: commit and push"""
        if not self.commit_all(message):
            return False
        return self.push()
    
    def get_commit_history(self, n: int = 10) -> List[dict]:
        """Get recent commits"""
        result = self._run_git(
            ["log", f"--max-count={n}", "--pretty=format:%h|%s|%ai|%an"],
            check=False
        )
        
        if result.returncode != 0:
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'date': parts[2],
                    'author': parts[3]
                })
        
        return commits
    
    def get_status_summary(self) -> dict:
        """Get repo status summary"""
        return {
            'initialized': self.is_repo_initialized(),
            'has_changes': self.has_changes(),
            'changed_files': self.get_changed_files(),
            'recent_commits': self.get_commit_history(5)
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status_summary()
        
        print("="*70)
        print("📊 GITHUB STATUS")
        print("="*70)
        print(f"Repo initialized: {status['initialized']}")
        print(f"Uncommitted changes: {status['has_changes']}")
        
        if status['changed_files']:
            print(f"\nChanged files ({len(status['changed_files'])}):")
            for f in status['changed_files'][:10]:
                print(f"  - {f}")
            if len(status['changed_files']) > 10:
                print(f"  ... and {len(status['changed_files']) - 10} more")
        
        if status['recent_commits']:
            print(f"\nRecent commits:")
            for commit in status['recent_commits'][:3]:
                print(f"  {commit['hash']}: {commit['message'][:50]}")
        
        print("="*70)


class AutoBackup:
    """
    Automatic backup system
    Commits changes periodically or on significant events
    """
    
    def __init__(self, github: GitHubManager):
        self.github = github
        self.backup_interval_minutes = 30
        self.last_backup = None
    
    def should_backup(self) -> bool:
        """Check if backup is due"""
        if self.last_backup is None:
            return True
        
        elapsed = (datetime.now() - self.last_backup).total_seconds() / 60
        return elapsed >= self.backup_interval_minutes
    
    def backup_if_needed(self, force: bool = False) -> bool:
        """Backup if interval passed or forced"""
        if not force and not self.should_backup():
            return False
        
        if not self.github.has_changes():
            return False
        
        success = self.github.auto_commit_and_push(
            message=f"Auto-backup: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        if success:
            self.last_backup = datetime.now()
        
        return success
    
    def backup_on_event(self, event_type: str):
        """Backup after significant events"""
        if self.github.has_changes():
            self.github.auto_commit_and_push(
                message=f"{event_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )


# Global instance
github_manager = GitHubManager()
auto_backup = AutoBackup(github_manager)

# Convenience function
def commit_workspace(message: str = None, push: bool = True) -> bool:
    """
    Quick function to commit current workspace
    
    Usage:
        commit_workspace("Added new feature")
        commit_workspace()  # Auto-message
    """
    if not github_manager.is_repo_initialized():
        print("⚠️ Git repo not initialized")
        return False
    
    if push:
        return github_manager.auto_commit_and_push(message)
    else:
        return github_manager.commit_all(message)


# Demo
if __name__ == "__main__":
    print("="*70)
    print("🔧 GITHUB MANAGER")
    print("="*70)
    print()
    
    # Initialize
    github_manager.init_repo()
    
    # Show status
    github_manager.print_status()
    
    # If changes, offer to commit
    if github_manager.has_changes():
        print("\n💡 Uncommitted changes detected!")
        print("Run: github_manager.auto_commit_and_push()")
    
    print()
    print("Setup complete. Configure remote with:")
    print("  github_manager.set_remote('https://github.com/YOURNAME/sigbotti-workspace.git')")
