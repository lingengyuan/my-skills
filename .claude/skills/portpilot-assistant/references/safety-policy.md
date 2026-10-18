# Safety Policy

1. Read-only inspection commands run without prompt. `pick` and `claim` may run when an authorized task requires an available port. Report lease IDs and expirations to the caller.
2. Before terminating a process, inspect its identity, PID, command line, and working directory. Authorization to stop a known task-owned server persists across turns. If the PID or process changes, or if the process belongs to a shared system daemon, ask for user confirmation before stopping it.
3. Commands that mutate state (`free`, `init --force`, and `config migrate`) require explicit task authorization. Do not request repetitive approval for operations already authorized. Preserve unrelated configuration files and processes.
4. Resolve the bundled CLI relative to this Skill's directory. Use standard user permissions first. Request system elevation only when an authorized operation encounters a concrete permission error.
5. Use graceful process termination first. Verify port release before continuing. Never assume permission for forced termination or unrelated processes from a failed initial attempt.
