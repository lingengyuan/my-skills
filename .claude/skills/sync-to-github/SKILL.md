---
name: sync-to-github
description: Inspect, stage, commit, and push Git repository changes safely within authorized scope. Use when committing code, pushing to GitHub, inspecting staged diffs, creating commits, or drafting commit messages.
---

# Sync to GitHub

1. **Inspect & Scope**: Check `git status`, branch, tracking remote, and staged/unstaged diffs. Operate strictly within user authorization (`Inspect` = read-only; `Commit` = local commit only; `Push` = commit + push).
2. **Stage Safely**: Stage only task-related files; never run `git add .` or `git add -A` when unrelated changes exist. Verify diffs contain no tokens, keys, or unintended artifacts.
3. **Commit**: Use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`) explaining the change and motivation. Do not add `Co-Authored-By` trailers unless requested.
4. **Push**: Push only to the configured upstream remote of the current branch. Never use `--force` or `--force-with-lease` unless explicitly instructed; if rejected, run `git fetch` and `git status` instead.
5. **Report**: Output the commit hash, branch name, and remote push status.

## CLI Usage

```bash
# Preview / commit / commit+push staged changes
python3 "<skill-dir>/tools/git_sync.py" --dry-run
python3 "<skill-dir>/tools/git_sync.py"
python3 "<skill-dir>/tools/git_sync.py" --push

# Push-only branch (when commits already exist and working tree is clean, do not use git_sync.py)
git push
```
