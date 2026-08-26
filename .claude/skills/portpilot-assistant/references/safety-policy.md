# Safety Policy

1. Auto-run read operations: `scan`, `who`, `pick`, `doctor`.
2. Confirm write operations: `free`, `init --force`, `config migrate`.
3. Before `free`, run `who` and display PID/command/cwd/startTime.
4. Never skip confirmation unless user explicitly asks.
5. Resolve the bundled CLI relative to this Skill's directory.
6. Run read actions without escalation first.
7. Request escalation only after a read action fails with an operating-system permission error.
8. Write actions still require explicit confirmation before execution.
