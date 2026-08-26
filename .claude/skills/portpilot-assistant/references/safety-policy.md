# Safety Policy

1. Auto-run read operations: `scan`, `who`, `doctor`, and `init --dry-run`.
2. `pick` creates a temporary lease; run it only for an explicit request and report its expiry. `claim` consumes a lease and also requires an explicit request.
3. Confirm write operations: `free`, `init --force`, and `config migrate`.
4. Before `free`, run `who` and display PID/command/cwd/startTime.
5. Never skip confirmation unless user explicitly asks.
6. Resolve the bundled CLI relative to this Skill's directory.
7. Run read actions without escalation first.
8. Request escalation only after a read action fails with an operating-system permission error.
9. Write actions still require explicit confirmation before execution.
