---
name: portpilot-assistant
description: Inspect, diagnose, allocate, and free local development ports using the bundled PortPilot CLI. Use when finding available ports, inspecting port listeners, resolving port conflicts, freeing ports, or managing PortPilot configuration.
---

# PortPilot Assistant Skill

Inspect, allocate, and manage local network development ports using the bundled PortPilot CLI. Node.js 18+ is required. No global npm installation is needed.

## CLI Location

Resolve the bundled executable relative to this Skill's directory:

```bash
node "<skill-dir>/assets/portpilot/bin/portpilot.js" --help
```

In POSIX environments, `scripts/run_portpilot.sh` provides an optional wrapper for the same binary.

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `pick` | Reserve an available port with temporary lease | `node "<cli>" pick --range 3000-3999 --count 1 --lease-ms 20000 --json` |
| `claim` | Consume an existing port lease | `node "<cli>" claim --lease-id <id> --json` |
| `scan` | List currently listening ports and services | `node "<cli>" scan --protocol both --json` |
| `who` | Identify process owning a specific port | `node "<cli>" who 3000 --json` |
| `doctor` | Diagnose configuration issues and port conflicts | `node "<cli>" doctor --json` |
| `free` | Terminate process holding a target port | `node "<cli>" free 3000 --yes --json` |
| `init` | Create default port configuration | `node "<cli>" init --dry-run --json` |
| `config` | View or migrate PortPilot configuration | `node "<cli>" config migrate --json` |

## Workflow

1. **Map user intent**: Identify the matching subcommand using [references/intent-map.md](references/intent-map.md).
2. **Execute read-only commands**: Pass `--json` to produce machine-readable output. Parse the JSON result directly.
3. **Allocate ports (`pick`)**: When starting a service, request a lease. State the allocated port and lease expiration in the response.
4. **Inspect before terminating (`free`)**:
   - Always execute `who <port>` to inspect the process name, PID, working directory, and start time.
   - If the process is a recognized development server created for the task, proceed with `free`.
   - If the process is unexpected, shared, or a system daemon, ask for user confirmation before terminating.
5. **Report findings**: State the direct answer first (e.g., port availability, PID owner, conflict cause), followed by command details.

## Safety Rules

- **Inspect first**: Never terminate a process with `free` without first identifying its PID and command line.
- **Permission elevation**: Use normal user permissions first. Request elevation (sudo/administrator) only when permission restrictions occur on an authorized task.
- **Signal escalation**: Prefer standard termination signals before forced termination. Never kill unrelated system services.

See [references/safety-policy.md](references/safety-policy.md) for detailed process management policies.

## Verification Checklist

Before completing the task, verify:

1. Target port status matches `who` or `scan` output.
2. Allocated lease IDs and expiry times are recorded when using `pick`.
3. Target port is unbound after executing `free`.
4. Output report states the final port state clearly.
