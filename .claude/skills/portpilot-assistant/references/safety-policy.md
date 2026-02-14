# Safety Policy

1. Auto-run read operations: `scan`, `who`, `pick`, `doctor`.
2. Confirm write operations: `free`, `init --force`, `config migrate`.
3. Before `free`, run `who` and display PID/command/cwd/startTime.
4. Never skip confirmation unless user explicitly asks.
5. On the first `portpilot` action in a session, proactively do one escalation bootstrap (`doctor --json`) and request a reusable prefix:
   - `prefix_rule: ["node", "/root/projects/portpilot/skills/portpilot-assistant/assets/portpilot/bin/portpilot.js"]`
6. Explain that the escalation is one-time to avoid repeated prompts for future `portpilot` commands.
7. If bootstrap was skipped or denied, rerun once with escalation only after a read-action permission error.
8. Write actions still require explicit confirmation before execution.
