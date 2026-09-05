# Safety Policy

1. Read-only inspection runs directly. `pick` and `claim` may run when a requested development task needs a port; report any lease that matters to the caller.
2. Before terminating a process, inspect its current identity and ownership. Authorization to stop a known task-owned server persists; a changed PID/process, shared service or unrelated application requires reassessment and, if not covered, user approval.
3. `free`, `init --force` and configuration migration require task authorization for their actual scope; do not ask again when already granted. Preserve unrelated configuration and processes.
4. Resolve the bundled CLI relative to this Skill. Try normal permissions first; request platform escalation only for a demonstrated permission restriction on an authorized operation.
5. Prefer graceful termination and verify the target port state. Do not infer authorization for a stronger signal or a different process from a failed attempt.
