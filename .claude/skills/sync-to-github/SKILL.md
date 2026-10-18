---
name: sync-to-github
description: Inspect, stage, commit, and push Git repository changes safely within authorized scope. Use when committing code, pushing to GitHub, inspecting staged diffs, creating commits, or drafting commit messages.
---

# Sync to GitHub Skill

Inspect, stage, commit, and push Git changes according to explicit user authorization. Standard Git commands and concepts are assumed knowledge.

## Authorization Scopes

- **Inspect / Preview**: Read-only operations. Do not stage files or create commits.
- **Commit**: Authorized to stage task-related files and create local commits.
- **Push / Sync**: Authorized to create local commits and push to the configured upstream remote.

## Workflow

1. **Inspect repository state**: Inspect `git status`, current branch, and tracking remotes. Inspect both staged and unstaged diffs.
2. **Stage task-related changes**: Verify that changes do not contain API keys, credentials, or unintended build artifacts. Stage only files related to the task. Never use blanket staging (`git add .` or `git add -A`) when unrelated modifications exist.
3. **Draft commit message**: Create a concise commit message following Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). Describe the specific change and motivation. Do not add assistant co-author trailers unless explicitly requested.
4. **Create commit**: Run the bundled `tools/git_sync.py` or standard `git commit`. Preview the staged diff before finalizing.
5. **Push to remote (if authorized)**: Push only to the current branch upstream remote. Never force-push or rewrite public history unless explicitly instructed.
6. **Verify synchronization**: Verify tracking status with `git status` or `git rev-parse`. Report local commit hash, branch name, and remote status.

## CLI Usage

### Bundled Tool

```bash
# Preview status and generated commit message without committing
python3 "<skill-dir>/tools/git_sync.py" --dry-run

# Commit staged changes
python3 "<skill-dir>/tools/git_sync.py"

# Commit staged changes and push to upstream
python3 "<skill-dir>/tools/git_sync.py" --push
```

### Standard Git Fallback

```bash
# Stage specific files
git add <file1> <file2>

# Commit with message
git commit -m "<type>(<scope>): <summary>"

# Push to current tracking branch
git push origin <branch>
```

## Guidelines & Safety Rules

- **Preserve unrelated work**: Never discard, restage, or overwrite changes outside the current task.
- **No secret exposure**: Inspect diffs before staging to prevent committing tokens, keys, or passwords.
- **No force push**: Never use `--force` or `--force-with-lease` unless explicitly instructed by the user.
- **Handle push rejection**: On rejection, inspect remote divergence with `git fetch` and `git status`. Do not force-push over remote changes.
- **No unsolicited trailers**: Do not add assistant co-author trailers (`Co-Authored-By`) unless requested.

## Verification Checklist

Before completing the task, verify:

1. Staged diff contains only task-related files and no sensitive credentials.
2. Commit exists locally with a valid hash and clear message.
3. If push was requested, remote ref matches local branch tip.
4. Output reports the exact commit hash, branch, and push status.
