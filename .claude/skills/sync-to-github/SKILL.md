---
name: sync-to-github
description: Safely prepare, commit, and optionally push Git changes. Use when the user asks to commit, commit and push, sync to GitHub, save work to Git, inspect staged changes, or generate a commit message.
---

# Sync to GitHub

Use the bundled script for deterministic staged-change commits. Resolve it relative to this Skill.

## Safe workflow

1. Inspect `git status --short`, the staged diff, current branch, and remote.
2. Check staged files for secrets, generated output, and unrelated changes.
3. Stage only the files authorized by the user.
4. Preview the generated message:

```bash
python "<skill-dir>/tools/git_sync.py" --dry-run
```

5. Commit the currently staged files:

```bash
python "<skill-dir>/tools/git_sync.py"
```

6. Push only when explicitly requested:

```bash
python "<skill-dir>/tools/git_sync.py" --push
```

7. After pushing, verify the exact remote ref with `git ls-remote`.

## Rules

- Default behavior commits staged files only and does not push.
- Never stage all files implicitly.
- Do not add assistant co-author trailers unless the user asks.
- Stop if nothing is staged.
- Preserve the local commit if pushing fails and report the exact failure.
