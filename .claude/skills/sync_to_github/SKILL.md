---
name: sync_to_github
description: Automated git commit and push tool with AI-generated commit messages
tags: [工程化, Git, 自动化, DevOps]
---

# sync_to_github

Automatically analyze project changes, generate descriptive commit messages using AI, and commit to git.

## Purpose

This skill automates the git workflow by:
1. Analyzing current git status (staged and unstaged changes)
2. Generating descriptive commit messages based on change content
3. Creating commits with AI-generated messages
4. Optionally pushing to remote repository

## Input/Output Contract

### Input
- No required parameters
- Optional flags:
  - `--push`: Automatically push to remote after committing
  - `--dry-run`: Preview commit message without committing

### Output
- Git commit created with descriptive message
- Optional: Push to remote repository
- Console output showing:
  - Files changed
  - Generated commit message
  - Commit hash

## Dependencies

- Git (command line)
- Python 3.x
- Working git repository with commits

## Usage

### Basic Usage

```bash
# Analyze changes and create commit
Skill(sync_to_github)

# Commit and push to remote
Skill(sync_to_github, args="--push")

# Preview without committing
Skill(sync_to_github, args="--dry-run")
```

### Examples

#### Example 1: Feature Development

```bash
# After implementing a new feature
Skill(sync_to_github)
```

Output:
```
Analyzing changes...
Files modified:
  src/components/Button.tsx
  src/styles/button.css

Generated commit message:
feat: add Button component with hover states

- Add reusable Button component with props interface
- Implement hover and active state animations
- Add CSS module for button styling

Commit created: abc123def
```

#### Example 2: Bug Fix

```bash
# After fixing a bug
Skill(sync_to_github, args="--push")
```

Output:
```
Analyzing changes...
Files modified:
  src/utils/api.ts
  tests/api.test.ts

Generated commit message:
fix: resolve API timeout error in data fetching

- Increase timeout from 5s to 30s for slow endpoints
- Add retry logic with exponential backoff
- Update test coverage for timeout scenarios

Commit created: 456789ghi
Pushed to origin/main
```

#### Example 3: Documentation Update

```bash
# After updating documentation
Skill(sync_to_github)
```

Output:
```
Analyzing changes...
Files modified:
  README.md
  docs/api.md
  docs/examples.md

Generated commit message:
docs: update API documentation with new endpoints

- Add new authentication endpoint examples
- Clarify rate limiting behavior
- Fix broken links in API reference

Commit created: def123ghi
```

## Implementation

The skill uses the Python tool at `tools/git_sync.py` which:

1. **Analyzes git status**
   ```bash
   git status --porcelain
   git diff --cached
   git diff
   ```

2. **Generates commit message**
   - Categorizes change type (feat/fix/docs/refactor/test/chore)
   - Summarizes main changes in title
   - Lists specific changes in bullet points
   - Follows conventional commits format

3. **Creates commit**
   ```bash
   git add .
   git commit -m "<generated message>"
   ```

4. **Optional push**
   ```bash
   git push
   ```

## Commit Message Format

Follows conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

## Error Handling

### No Changes Detected
```
Error: No changes to commit
Working directory is clean. Make some changes before running sync_to_github.
```

### Git Repository Not Found
```
Error: Not a git repository
Initialize with: git init
```

### Nothing Staged
The skill automatically stages all changes with `git add .`

### Push Fails
```
Warning: Commit created but push failed
Commit hash: abc123def
Error: <git error message>
Manual push required: git push
```

## Integration

### Permissions

Add to `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Skill(sync_to_github)",
      "Bash(python3:.claude/skills/sync_to_github/tools/*)",
      "Bash(git:*)"
    ]
  }
}
```

### Workflow Integration

Can be chained with other skills:

```bash
# After note creation
Skill(note-creator, "Create API docs")
Skill(sync_to_github, args="--push")

# After code generation
# ... code changes ...
Skill(sync_to_github)
```

## Configuration

### Commit Message Customization

Edit `tools/git_sync.py` to customize:

```python
# Default commit types
COMMIT_TYPES = ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf"]

# Message template
COMMIT_TEMPLATE = """{type}({scope}): {subject}

{body}

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>
"""
```

### Branch Behavior

Default behavior:
- Commits to current branch
- Pushes to current branch's remote
- To change branch: `git checkout <branch>` before running skill

## Best Practices

1. **Review before committing**: Use `--dry-run` to preview commit message
2. **Stage selectively**: Commit all changes or stage specific files first
3. **Meaningful changes**: Ensure changes are complete before committing
4. **Branch management**: Commit to feature branches, not main directly
5. **Commit frequency**: Use for logical units of work, not every file save

## Limitations

1. Requires at least one existing commit in repository
2. Cannot handle merge conflicts
3. Does not create pull requests
4. Requires git configured with user.name and user.email
5. Only commits to current branch

## Troubleshooting

### "git config" errors
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Large commits fail
- Consider splitting into smaller commits
- Check git LFS for large files

### Push permission denied
- Check remote URL: `git remote -v`
- Verify authentication credentials
- Check branch permissions on GitHub
