# sync_to_github Usage Examples

## Example 1: Basic Commit

After implementing a new feature or making changes:

```bash
Skill(sync_to_github)
```

**Expected Output:**
```
sync_to_github - Analyzing changes...
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
feat(typescript): add Button component

- Add src/components/Button.tsx
- Update src/styles/button.css

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: abc123def

Done!
```

## Example 2: Commit and Push

After fixing a bug and wanting to push immediately:

```bash
Skill(sync_to_github, args="--push")
```

**Expected Output:**
```
sync_to_github - Analyzing changes...
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
fix(typescript): update api.ts and api.test.ts (2 files)

- Update src/utils/api.ts
- Update tests/api.test.ts

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: 456789ghi

Pushing to remote
-----------------
  Pushed to origin/main

Done!
```

## Example 3: Dry Run (Preview)

To preview the commit message without actually committing:

```bash
Skill(sync_to_github, args="--dry-run")
```

**Expected Output:**
```
sync_to_github - Analyzing changes...
====================================

Files changed
------------
  new file: README.md
  new file: docs/api.md
  new file: docs/examples.md

Change summary
--------------
  Added: 3
  Modified: 0
  Deleted: 0
  Languages: Markdown

Generated commit message
------------------------
docs(documentation): add new features (3 files)

- Add README.md
- Add docs/api.md
- Add docs/examples.md

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>

Dry run mode - no commit created
```

## Example 4: Documentation Update

After updating documentation files:

```bash
Skill(sync_to_github)
```

**Expected Output:**
```
sync_to_github - Analyzing changes...
====================================

Files changed
------------
  modified: README.md
  modified: docs/guide.md

Change summary
--------------
  Added: 0
  Modified: 2
  Deleted: 0
  Languages: Markdown

Generated commit message
------------------------
docs(documentation): update project (2 files)

- Update README.md
- Update docs/guide.md

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: def123abc

Done!
```

## Example 5: Test Updates

After adding or updating tests:

```bash
Skill(sync_to_github)
```

**Expected Output:**
```
sync_to_github - Analyzing changes...
====================================

Files changed
------------
  modified: tests/unit/button.test.ts

Change summary
--------------
  Added: 0
  Modified: 1
  Deleted: 0
  Languages: TypeScript

Generated commit message
------------------------
test(tests): update button.test.ts

- Update tests/unit/button.test.ts

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: 789xyz123

Done!
```

## Example 6: Mixed Changes (Code + Docs)

After making both code and documentation changes:

```bash
Skill(sync_to_github, args="--push")
```

**Expected Output:**
```
sync_to_github - Analyzing changes...
====================================

Files changed
------------
  new file: src/utils/helpers.ts
  modified: README.md
  modified: src/index.ts

Change summary
--------------
  Added: 1
  Modified: 2
  Deleted: 0
  Languages: Markdown, TypeScript

Generated commit message
------------------------
feat(typescript): add new features (3 files)

- Add src/utils/helpers.ts
- Update README.md
- Update src/index.ts

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>

Staging changes
---------------
  All changes staged

Creating commit
---------------
  Commit created: xyz789abc

Pushing to remote
-----------------
  Pushed to origin/main

Done!
```

## Error Scenarios

### No Changes

```bash
Skill(sync_to_github)
```

**Output:**
```
ERROR: No changes to commit
Working directory is clean. Make some changes before running sync_to_github.
```

### Not a Git Repository

```bash
Skill(sync_to_github)
```

**Output:**
```
ERROR: Not a git repository
Initialize with: git init
```

### Push Fails (Authentication Issue)

```bash
Skill(sync_to_github, args="--push")
```

**Output:**
```
...
Commit created: abc123def

Pushing to remote
-----------------
WARNING: Push failed: fatal: Authentication failed
  Commit hash: abc123def
  Manual push required: git push
```

## Workflow Examples

### After Creating Notes with note-creator

```bash
# Create a note
Skill(note-creator, "Create API documentation")

# Commit and push the changes
Skill(sync_to_github, args="--push")
```

### After Code Generation Session

```bash
# ... after making multiple code changes ...

# Review what will be committed
Skill(sync_to_github, args="--dry-run")

# If satisfied, commit for real
Skill(sync_to_github)

# Later, when ready to push
Skill(sync_to_github, args="--push")
```

### Feature Branch Workflow

```bash
# Create and switch to feature branch
git checkout -b feature/new-ui

# Make changes...

# Commit changes
Skill(sync_to_github)

# Push to feature branch
Skill(sync_to_github, args="--push")
```