---
name: sync-to-github
description: Safely prepare, commit, and optionally push Git changes. Use when the user asks to commit, commit and push, sync to GitHub, save work to Git, inspect staged changes, or generate a commit message.
---

# Sync to GitHub

Match the operation to the user's request: inspection or commit-message drafting is read-only; commit requests authorize a local commit; push/sync requests authorize the corresponding push. Do not commit merely because this Skill was selected.

1. Inspect status, staged and unstaged diffs, current branch and relevant remotes. Isolate task-related changes and preserve unrelated staged work.
2. Check the intended diff for secrets and unintended generated files; stage only authorized paths or hunks. Never use blanket staging to capture unrelated work.
3. When committing, use the bundled `tools/git_sync.py` if it fits the required scope, or ordinary Git for precise control. A script dependency is not a blocker. Preview the actual staged diff and message yourself; existing commit authorization needs no additional approval.
4. If nothing changed, report that result. If a local commit already exists and a push is requested, continue the push even when the index is empty. After committing, do not invoke another commit-only path merely to push.
5. Push only within the requested destination and scope; never force-push or rewrite unrelated history by inference. On rejection, inspect the cause, preserve work, and resolve routine divergence in an isolated checkout when appropriate.
6. Verify the exact remote ref after pushing. Report actual local/remote status and any blocker; do not describe an unpushed local commit as synchronized.

Do not add assistant co-author trailers unless requested. A push does not by itself prove deployment; verify CI or deployment only when required by the user's requested outcome or project checks.
