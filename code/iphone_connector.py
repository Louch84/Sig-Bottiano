#!/usr/bin/env python3
"""iPhone Connector - Run shortcuts via Mac"""
import subprocess
import os

def run_shortcut(name):
    """Run a Siri Shortcut"""
    try:
        result = subprocess.run(
            ["shortcuts", "run", name],
            capture_output=True,
            text=True
        )
        return {"status": "ok", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def list_shortcuts():
    """List available shortcuts"""
    try:
        result = subprocess.run(
            ["shortcuts", "list"],
            capture_output=True,
            text=True
        )
        return result.stdout.split('\n')[:10]
    except:
        return []

# Example: Create a shortcut for Lou
def create_lou_shortcuts():
    """Create useful shortcuts for Lou's business"""
    shortcuts = [
        "Text-Lou-Status",
        "Check-MPT",
        "Post-to-Mastodon"
    ]
    return shortcuts

if __name__ == "__main__":
    print("=== iPHONE CONNECTOR ===")
    print("Available shortcuts:")
    for s in list_shortcuts()[:5]:
        if s.strip():
            print(f"  - {s}")
