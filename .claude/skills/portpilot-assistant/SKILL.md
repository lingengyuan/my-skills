---
name: portpilot-assistant
description: Manage local development ports through the bundled PortPilot CLI. Use when users ask to find an available port, inspect a port owner, scan conflicts, diagnose port problems, free a port, or initialize and migrate PortPilot configuration.
---

# PortPilot Assistant

Resolve the bundled CLI relative to this Skill:

```bash
node "<skill-dir>/assets/portpilot/bin/portpilot.js" --help
```

No global installation is required. Node.js 18 or newer is required. Port inspection supports Windows, macOS, and Linux using the operating system's native tools.

In a POSIX shell, [scripts/run_portpilot.sh](scripts/run_portpilot.sh) is an optional wrapper for the same bundled CLI. It does not install a package from the network.

## Workflow

1. Map the request to `scan`, `who`, `pick`, `claim`, `doctor`, `free`, `init`, or `config`.
2. Run read-only commands with `--json`. Use `pick` when the requested development task needs a port; it creates a temporary lease, so report the expiry when handing it off.
3. Try normal permissions first; request elevation only for an observed permission restriction on an already authorized operation.
4. Before `free`, inspect the current port owner, PID, command, working directory and start time. If the user already authorized stopping this exact process or the task-owned development server, proceed with the intended signal. Ask only if the owner is unexpected, shared, unrelated, or the stopping scope is unclear; do not reconfirm unchanged authorization.
5. Inspect configuration differences before `init --force` or `config migrate`; use `claim` only when consuming the lease is part of the authorized task.
6. Return the conclusion first and the relevant command result second.

## Commands

```bash
node "<cli>" pick --range 3000-3999 --count 1 --lease-ms 20000 --json
node "<cli>" claim --lease-id <id> --json
node "<cli>" scan --protocol both --json
node "<cli>" who 3000 --json
node "<cli>" doctor --json
node "<cli>" init --dry-run --json
node "<cli>" config migrate --json
node "<cli>" free 3000 --yes --json
```

For downstream automation that needs a compact summary, optionally pipe a JSON result through [scripts/normalize_output.js](scripts/normalize_output.js).

Read [references/intent-map.md](references/intent-map.md) for routing and [references/safety-policy.md](references/safety-policy.md) before terminating a process.
