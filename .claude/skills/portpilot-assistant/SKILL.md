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

## Workflow

1. Map the request to `scan`, `who`, `pick`, `doctor`, `free`, `init`, or `config`.
2. Run read-only commands normally with `--json`.
3. Request elevated permission only if a read-only command fails because the operating system blocks process or socket inspection.
4. Before `free`, show the port, PID, command, working directory, start time, and intended signal, then obtain explicit confirmation.
5. Preview configuration changes before `init --force` or `config migrate`.
6. Return the conclusion first and the relevant command result second.

## Commands

```bash
node "<cli>" pick --range 3000-3999 --count 1 --lease-ms 20000 --json
node "<cli>" scan --protocol both --json
node "<cli>" who 3000 --json
node "<cli>" doctor --json
node "<cli>" init --dry-run --json
node "<cli>" free 3000 --yes --json
```

Read [references/intent-map.md](references/intent-map.md) for routing and [references/safety-policy.md](references/safety-policy.md) before terminating a process.
