#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""git_sync: Automated git commit and push with AI-generated commit messages.

Deterministic pipeline:
1) Check git status (staged and unstaged changes)
2) Analyze changed files and their content
3) Generate descriptive commit message based on changes
4) Stage all changes (git add .)
5) Create commit with generated message
6) Optionally push to remote

Output contract:
- Git commit created with AI-generated message
- Optional: Push to remote repository
- Console output with file list, commit message, and commit hash

Usage:
  python3 git_sync.py [--push] [--dry-run]
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import List, Optional


@dataclass
class FileChange:
    path: str
    status: str  # M, A, D, R, etc.
    is_staged: bool


@dataclass
class ChangeSummary:
    files: List[FileChange]
    added_count: int
    modified_count: int
    deleted_count: int
    has_code: bool
    has_docs: bool
    has_tests: bool
    languages: List[str]


def run_git_command(args: List[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    cmd = ["git"] + args
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd or Path.cwd(),
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def check_git_repo() -> bool:
    """Check if current directory is a git repository."""
    _, _, err = run_git_command(["rev-parse", "--git-dir"])
    return err == ""


def get_file_changes() -> List[FileChange]:
    """Get all changed files (staged and unstaged)."""
    changes: List[FileChange] = []

    # Get staged changes
    _, staged_out, _ = run_git_command(["diff", "--cached", "--name-status"])
    for line in staged_out.splitlines():
        if not line:
            continue
        parts = line.split("\t", 1)
        status = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        changes.append(FileChange(path=path, status=status, is_staged=True))

    # Get unstaged changes
    _, unstaged_out, _ = run_git_command(["diff", "--name-only"])
    for line in unstaged_out.splitlines():
        if not line:
            continue
        # Check if file already in staged (modified and then staged again)
        if not any(c.path == line for c in changes):
            changes.append(FileChange(path=line, status="M", is_staged=False))

    # Get untracked files
    _, untracked_out, _ = run_git_command(["ls-files", "--others", "--exclude-standard"])
    for line in untracked_out.splitlines():
        if not line:
            continue
        changes.append(FileChange(path=line, status="A", is_staged=False))

    return changes


def get_file_diff(path: str, staged: bool) -> str:
    """Get diff for a specific file."""
    args = ["diff"]
    if staged:
        args.append("--cached")
    args.append(path)
    _, diff, _ = run_git_command(args)
    return diff


def detect_language(path: str) -> Optional[str]:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".jsx": "JavaScript",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".c": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".h": "C/C++",
        ".hpp": "C++",
        ".cs": "C#",
        ".php": "PHP",
        ".rb": "Ruby",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".sh": "Shell",
        ".bash": "Shell",
        ".zsh": "Shell",
        ".fish": "Shell",
        ".sql": "SQL",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".less": "Less",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
        ".toml": "TOML",
        ".ini": "INI",
        ".cfg": "Config",
        ".conf": "Config",
    }
    _, ext = os.path.splitext(path)
    return ext_map.get(ext.lower())


def analyze_changes(changes: List[FileChange]) -> ChangeSummary:
    """Analyze file changes to generate commit message."""
    added = 0
    modified = 0
    deleted = 0
    has_code = False
    has_docs = False
    has_tests = False
    languages = set()

    for change in changes:
        status = change.status
        if status == "A":
            added += 1
        elif status == "D":
            deleted += 1
        else:
            modified += 1

        # Detect file type
        path_lower = change.path.lower()
        if any(x in path_lower for x in ["readme", "doc", ".md", "docs/"]):
            has_docs = True
        if any(x in path_lower for x in ["test", "spec", "__tests__"]):
            has_tests = True

        lang = detect_language(change.path)
        if lang:
            languages.add(lang)
            has_code = True

    return ChangeSummary(
        files=changes,
        added_count=added,
        modified_count=modified,
        deleted_count=deleted,
        has_code=has_code,
        has_docs=has_docs,
        has_tests=has_tests,
        languages=sorted(languages),
    )


def generate_commit_message(summary: ChangeSummary) -> str:
    """Generate commit message based on change analysis."""
    # Determine commit type
    if summary.has_tests and summary.modified_count <= 2:
        commit_type = "test"
        scope = "tests"
    elif summary.has_docs and not summary.has_code:
        commit_type = "docs"
        scope = "documentation"
    elif summary.deleted_count > summary.added_count + summary.modified_count:
        commit_type = "refactor"
        scope = "cleanup"
    elif summary.added_count > summary.modified_count:
        commit_type = "feat"
        scope = summary.languages[0].lower() if summary.languages else "general"
    else:
        commit_type = "chore"
        scope = summary.languages[0].lower() if summary.languages else "general"

    # Generate title
    total_files = len(summary.files)
    if total_files == 1:
        file_path = summary.files[0].path
        file_name = Path(file_path).name
        if summary.deleted_count > 0:
            title = f"remove {file_name}"
        elif summary.added_count > 0:
            title = f"add {file_name}"
        else:
            title = f"update {file_name}"
    else:
        if commit_type == "feat":
            title = f"add new features ({total_files} files)"
        elif commit_type == "fix":
            title = f"fix bugs and issues ({total_files} files)"
        elif commit_type == "docs":
            title = f"update documentation ({total_files} files)"
        elif commit_type == "test":
            title = f"update tests ({total_files} files)"
        elif commit_type == "refactor":
            title = f"refactor and cleanup ({total_files} files)"
        else:
            title = f"update project ({total_files} files)"

    # Generate body
    body_parts = []
    for change in summary.files[:10]:  # Limit to first 10 files
        action = ""
        if change.status == "A":
            action = "Add"
        elif change.status == "D":
            action = "Remove"
        else:
            action = "Update"
        body_parts.append(f"- {action} {change.path}")

    if len(summary.files) > 10:
        body_parts.append(f"- ... and {len(summary.files) - 10} more files")

    # Build message
    message_lines = [
        f"{commit_type}({scope}): {title}",
        "",
        "\n".join(body_parts),
        "",
        "Co-Authored-By: Claude Sonnet <noreply@anthropic.com>",
    ]

    return "\n".join(message_lines)


def stage_all_changes() -> bool:
    """Stage all changes using git add ."""
    code, _, _ = run_git_command(["add", "."])
    return code == 0


def create_commit(message: str) -> tuple[bool, str]:
    """Create git commit with message."""
    code, stdout, err = run_git_command(["commit", "-m", message])
    if code == 0:
        # Extract commit hash from output
        match = re.search(r"\[([a-z0-9]+)\]", stdout)
        if match:
            return True, match.group(1)
        # Fallback: get latest commit hash
        _, hash_out, _ = run_git_command(["rev-parse", "HEAD"])
        return True, hash_out
    return False, err


def push_to_remote() -> tuple[bool, str]:
    """Push commits to remote repository."""
    # Get current branch
    _, branch, _ = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    if not branch or branch == "HEAD":
        return False, "Not on any branch"

    code, _, err = run_git_command(["push"])
    if code == 0:
        return True, f"Pushed to origin/{branch}"
    return False, err


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{text}")
    print("=" * len(text))


def print_section(text: str) -> None:
    """Print formatted section."""
    print(f"\n{text}")
    print("-" * len(text))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated git commit and push with AI-generated commit messages"
    )
    parser.add_argument(
        "--push", action="store_true", help="Push to remote after committing"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview commit message without committing"
    )
    args = parser.parse_args()

    # Check if we're in a git repository
    if not check_git_repo():
        print("ERROR: Not a git repository", file=sys.stderr)
        print("Initialize with: git init", file=sys.stderr)
        return 1

    # Get file changes
    changes = get_file_changes()
    if not changes:
        print("ERROR: No changes to commit", file=sys.stderr)
        print("Working directory is clean. Make some changes before running sync_to_github.", file=sys.stderr)
        return 1

    print_header("sync_to_github - Analyzing changes...")

    print_section("Files changed")
    for change in changes:
        status_symbol = {
            "A": "new file",
            "M": "modified",
            "D": "deleted",
            "R": "renamed",
        }.get(change.status, "changed")
        print(f"  {status_symbol}: {change.path}")

    # Analyze changes
    summary = analyze_changes(changes)

    print_section("Change summary")
    print(f"  Added: {summary.added_count}")
    print(f"  Modified: {summary.modified_count}")
    print(f"  Deleted: {summary.deleted_count}")
    if summary.languages:
        print(f"  Languages: {', '.join(summary.languages)}")

    # Generate commit message
    commit_message = generate_commit_message(summary)

    print_section("Generated commit message")
    print(commit_message)

    # Dry run mode
    if args.dry_run:
        print_section("Dry run mode - no commit created")
        return 0

    # Stage all changes
    print_section("Staging changes")
    if not stage_all_changes():
        print("ERROR: Failed to stage changes", file=sys.stderr)
        return 1
    print("  All changes staged")

    # Create commit
    print_section("Creating commit")
    success, result = create_commit(commit_message)
    if not success:
        print(f"ERROR: Failed to create commit: {result}", file=sys.stderr)
        return 1

    print(f"  Commit created: {result}")

    # Push to remote if requested
    if args.push:
        print_section("Pushing to remote")
        success, result = push_to_remote()
        if not success:
            print(f"WARNING: Push failed: {result}", file=sys.stderr)
            print(f"  Commit hash: {result}")
            print("  Manual push required: git push")
            return 1
        print(f"  {result}")

    print_header("Done!")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
