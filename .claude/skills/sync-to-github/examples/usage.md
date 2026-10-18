# Sync to GitHub Usage Examples

## Example 1: Preview Changes (Dry Run)

Preview changed files and the generated commit message without creating a commit:

```bash
python3 tools/git_sync.py --dry-run
```

**Output:**
```text
sync-to-github - Analyzing changes...
====================================

Files changed
------------
  new file: README.md
  new file: docs/api.md

Change summary
--------------
  Added: 2
  Modified: 0
  Deleted: 0
  Languages: Markdown

Generated commit message
------------------------
docs(documentation): update documentation (2 files)

- Add README.md
- Add docs/api.md

Dry run mode - no commit created
```

## Example 2: Local Commit

Create a local commit from staged changes without pushing:

```bash
python3 tools/git_sync.py
```

**Output:**
```text
sync-to-github - Analyzing changes...
====================================

Files changed
------------
  modified: src/utils/api.ts
  modified: tests/api.test.ts

Change summary
--------------
  Added: 0
  Modified: 2
  Deleted: 0
  Languages: TypeScript

Generated commit message
------------------------
fix(typescript): fix bugs and issues (2 files)

- Update src/utils/api.ts
- Update tests/api.test.ts

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: 456789ghi

Done!
```

## Example 3: Commit and Push

Create a commit and push to the upstream remote in one step:

```bash
python3 tools/git_sync.py --push
```

**Output:**
```text
sync-to-github - Analyzing changes...
====================================

Files changed
------------
  new file: src/components/Button.tsx
  modified: src/styles/button.css

Change summary
--------------
  Added: 1
  Modified: 1
  Deleted: 0
  Languages: TypeScript, CSS

Generated commit message
------------------------
feat(typescript): add new features (2 files)

- Add src/components/Button.tsx
- Update src/styles/button.css

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: abc123def

Pushing to remote
-----------------
  Pushed to origin/main

Done!
```

## Error Scenarios

### No Changes Detected

```bash
python3 tools/git_sync.py
```

**Output:**
```text
ERROR: No changes to commit
Working directory is clean. Stage changes before running sync-to-github.
```

### Push Rejection or Authentication Failure

```bash
python3 tools/git_sync.py --push
```

**Output:**
```text
Creating commit
---------------
  Commit created: abc123def

Pushing to remote
-----------------
WARNING: Push failed: fatal: Authentication failed
  Commit hash: abc123def
  Manual push required: git push
```