import fs from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import { createLeases, claimLease } from './lease.js';
import { listListeningPorts, listPreflight, probeTcpPort } from './system.js';
import { defaultConfig, lintConfig, mergeConfig, migrateConfig, readConfig, scanForConfig } from './config.js';
import {
  EXIT_CODES,
  createResult,
  parseArgs,
  parsePort,
  parsePortList,
  parseRange,
  toCommandError
} from './utils.js';

function fingerprint(record) {
  return `${record.pid}:${record.startTime}:${record.command}:${record.port}`;
}

function normalizeRecords(records) {
  const seen = new Set();
  const out = [];
  for (const r of records) {
    const key = `${r.port}:${r.pid}:${r.command}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    out.push(r);
  }
  return out;
}

async function confirmPrompt(message) {
  if (!process.stdin.isTTY) {
    return false;
  }
  const rl = readline.createInterface({ input: stdin, output: stdout });
  try {
    const answer = await rl.question(`${message} [y/N] `);
    return /^y(es)?$/i.test(answer.trim());
  } finally {
    rl.close();
  }
}

function classifyPermissionError(error) {
  if (!error) {
    return false;
  }
  return error.code === 'EPERM' || error.code === 'EACCES';
}

function diagnosticsHavePermissionIssue(diagnostics = []) {
  return diagnostics.some((diag) => {
    const text = String(diag?.stderr || '').toLowerCase();
    return (
      text.includes('operation not permitted') ||
      text.includes('permission denied') ||
      text.includes('cannot open netlink socket') ||
      text.includes('cannot open a network socket')
    );
  });
}

function createProbeError(command, data, probe, permissionMessage) {
  const permissionDenied = Boolean(probe?.permissionDenied) || diagnosticsHavePermissionIssue(probe?.diagnostics);
  return createResult(command, data, {
    ok: false,
    exitCode: permissionDenied ? EXIT_CODES.PERMISSION_DENIED : EXIT_CODES.SYSTEM_PROBE_FAILED,
    errors: [
      toCommandError(
        permissionDenied ? 'probe-permission-denied' : 'probe-failed',
        permissionDenied
          ? (permissionMessage || 'Unable to inspect port state due permission restrictions')
          : 'Unable to inspect port state due probe failures'
      )
    ]
  });
}

export async function cmdWho(args, global) {
  try {
    const port = parsePort(args[0]);
    const probe = probeTcpPort(port, global);
    const records = normalizeRecords(probe.records);

    if (records.length === 0) {
      if (probe.probeFailed) {
        return createProbeError(
          'who',
          { port, occupied: false, records: [], diagnostics: probe.diagnostics },
          probe,
          `Unable to inspect port ${port} due permission restrictions`
        );
      }
      return createResult('who', { port, occupied: false, records: [], diagnostics: probe.diagnostics }, {
        ok: false,
        exitCode: EXIT_CODES.PORT_NOT_OCCUPIED,
        errors: [toCommandError('not-occupied', `Port ${port} is not occupied`)]
      });
    }

    return createResult('who', {
      port,
      occupied: true,
      records,
      diagnostics: probe.diagnostics
    });
  } catch (error) {
    return createResult('who', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
  }
}

export async function cmdPick(args, global) {
  const defs = new Map([
    ['--range', { key: 'range', type: 'string' }],
    ['--count', { key: 'count', type: 'number' }],
    ['--exclude', { key: 'exclude', type: 'string' }],
    ['--lease-ms', { key: 'leaseMs', type: 'number' }]
  ]);

  try {
    const { options } = parseArgs(args, defs);
    const range = parseRange(options.range || '3000-3999');
    const count = options.count ? Math.max(1, Math.floor(options.count)) : 1;
    const exclude = new Set(parsePortList(options.exclude));
    const leaseMs = options.leaseMs ? Math.max(1000, Math.floor(options.leaseMs)) : 20000;

    const picked = [];
    const unknownPorts = [];
    for (let p = range.start; p <= range.end && picked.length < count; p += 1) {
      if (exclude.has(p)) {
        continue;
      }
      const probe = probeTcpPort(p, global);
      if (probe.probeFailed) {
        unknownPorts.push({ port: p, diagnostics: probe.diagnostics });
        continue;
      }
      if (!probe.occupied) {
        picked.push(p);
      }
    }

    if (picked.length < count) {
      const permissionDenied = unknownPorts.some((item) => diagnosticsHavePermissionIssue(item.diagnostics));
      const hasProbeFailures = unknownPorts.length > 0;
      return createResult('pick', {
        picked,
        checkedRange: `${range.start}-${range.end}`,
        requestedCount: count,
        unknownCount: unknownPorts.length,
        unknownPorts: unknownPorts.map((item) => item.port),
        strategy: 'lowest-first'
      }, {
        ok: false,
        exitCode: hasProbeFailures
          ? (permissionDenied ? EXIT_CODES.PERMISSION_DENIED : EXIT_CODES.SYSTEM_PROBE_FAILED)
          : EXIT_CODES.SYSTEM_PROBE_FAILED,
        errors: [
          hasProbeFailures
            ? toCommandError(
              permissionDenied ? 'probe-permission-denied' : 'probe-failed',
              permissionDenied
                ? `Unable to safely inspect ${unknownPorts.length} port(s) in range ${range.start}-${range.end}`
                : `Probe failed for ${unknownPorts.length} port(s) in range ${range.start}-${range.end}`
            )
            : toCommandError('insufficient-ports', `Only found ${picked.length} available ports`)
        ]
      });
    }

    const leases = await createLeases(picked, leaseMs);
    return createResult('pick', {
      picked,
      leases: leases.map((lease) => ({
        leaseId: lease.id,
        port: lease.port,
        leaseMs,
        leaseExpiresAt: new Date(lease.expiresAt).toISOString()
      })),
      checkedRange: `${range.start}-${range.end}`,
      excluded: [...exclude],
      strategy: 'lowest-first'
    });
  } catch (error) {
    return createResult('pick', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
  }
}

export async function cmdClaim(args, global) {
  const defs = new Map([
    ['--lease-id', { key: 'leaseId', type: 'string' }]
  ]);

  try {
    const { options } = parseArgs(args, defs);
    const leaseId = options.leaseId;
    if (!leaseId) {
      throw new Error('Missing --lease-id');
    }

    const lease = await claimLease(leaseId);
    if (!lease) {
      return createResult('claim', null, {
        ok: false,
        exitCode: EXIT_CODES.LEASE_NOT_FOUND_OR_EXPIRED,
        errors: [toCommandError('lease-missing', 'Lease not found or expired')]
      });
    }

    const probe = probeTcpPort(lease.port, global);
    if (probe.probeFailed) {
      return createProbeError(
        'claim',
        { leaseId, port: lease.port, diagnostics: probe.diagnostics },
        probe,
        `Unable to verify lease port ${lease.port} due permission restrictions`
      );
    }
    if (probe.occupied) {
      return createResult('claim', {
        leaseId,
        port: lease.port
      }, {
        ok: false,
        exitCode: EXIT_CODES.LEASE_RACE_LOST,
        errors: [toCommandError('race-lost', `Port ${lease.port} is no longer available`)]
      });
    }

    return createResult('claim', {
      leaseId,
      port: lease.port,
      claimed: true
    });
  } catch (error) {
    return createResult('claim', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
  }
}

function conflictAnalysis(config, global) {
  const conflicts = [];
  const suggestions = [];
  const seen = new Map();

  for (const project of config.projects || []) {
    for (const port of project.declaredPorts || []) {
      if (!seen.has(port)) {
        seen.set(port, []);
      }
      seen.get(port).push(project.name || project.root || '<unknown>');
    }
  }

  for (const [port, projects] of seen.entries()) {
    if (projects.length > 1) {
      conflicts.push({
        type: 'config-conflict',
        port,
        projects
      });
      suggestions.push(`portpilot pick --range 3000-3999 --count 1 --json # for ${projects.join(', ')}`);
    }

    const probe = probeTcpPort(port, global);
    if (probe.occupied) {
      const pids = normalizeRecords(probe.records).map((x) => `${x.pid}:${x.command}`);
      conflicts.push({
        type: 'runtime-occupied',
        port,
        projects,
        occupiedBy: pids
      });
      suggestions.push(`portpilot who ${port}`);
      suggestions.push(`portpilot free ${port}`);
    }
  }

  return { conflicts, suggestions: [...new Set(suggestions)] };
}

export async function cmdDoctor(args, global, cwd) {
  const defs = new Map([
    ['--strict', { key: 'strict', type: 'boolean' }],
    ['--preflight', { key: 'preflight', type: 'boolean' }],
    ['--config', { key: 'config', type: 'string' }]
  ]);

  try {
    const { options } = parseArgs(args, defs);

    if (options.preflight) {
      const preflight = listPreflight();
      const ok = preflight.missingDeps.length === 0;
      return createResult('doctor', preflight, {
        ok,
        exitCode: ok ? EXIT_CODES.OK : EXIT_CODES.SYSTEM_PROBE_FAILED,
        errors: ok ? [] : [toCommandError('missing-dependencies', 'Some system dependencies are missing')]
      });
    }

    const configPath = path.join(cwd, options.config || '.portmanrc');
    const loaded = await readConfig(configPath);
    if (!loaded.ok) {
      return createResult('doctor', {
        conflicts: [],
        suggestions: ['Run: portpilot init --dry-run']
      }, {
        ok: false,
        exitCode: EXIT_CODES.CONFIG_ERROR,
        errors: [toCommandError('config-missing', loaded.error)]
      });
    }

    const lintErrors = lintConfig(loaded.value);
    if (lintErrors.length > 0) {
      return createResult('doctor', { lintErrors }, {
        ok: false,
        exitCode: EXIT_CODES.CONFIG_ERROR,
        errors: lintErrors.map((e) => toCommandError('config-invalid', e))
      });
    }

    const analysis = conflictAnalysis(loaded.value, global);
    const hasConflict = analysis.conflicts.length > 0;
    return createResult('doctor', analysis, {
      ok: !hasConflict,
      exitCode: hasConflict && options.strict ? EXIT_CODES.CONFLICT_FOUND : EXIT_CODES.OK,
      errors: hasConflict ? [toCommandError('conflicts-found', `Found ${analysis.conflicts.length} conflicts`)] : []
    });
  } catch (error) {
    return createResult('doctor', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
  }
}

export async function cmdScan(args, global) {
  const defs = new Map([
    ['--protocol', { key: 'protocol', type: 'string' }]
  ]);

  try {
    const { options } = parseArgs(args, defs);
    const protocol = (options.protocol || 'both').toLowerCase();
    if (!['tcp', 'udp', 'both'].includes(protocol)) {
      throw new Error('Invalid --protocol, expected tcp|udp|both');
    }

    const scan = listListeningPorts(global);
    if (scan.probeFailed) {
      return createProbeError(
        'scan',
        {
          protocol,
          total: 0,
          ports: { tcp: [], udp: [] },
          records: [],
          diagnostics: scan.diagnostics
        },
        scan,
        'Unable to scan listening ports due permission restrictions'
      );
    }
    const records = scan.records.filter((record) => protocol === 'both' || record.protocol === protocol);
    const tcpPorts = [...new Set(records.filter((r) => r.protocol === 'tcp').map((r) => r.port))].sort((a, b) => a - b);
    const udpPorts = [...new Set(records.filter((r) => r.protocol === 'udp').map((r) => r.port))].sort((a, b) => a - b);

    return createResult('scan', {
      protocol,
      total: records.length,
      ports: {
        tcp: tcpPorts,
        udp: udpPorts
      },
      records,
      diagnostics: scan.diagnostics
    });
  } catch (error) {
    return createResult('scan', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
  }
}

const PROTECTED_PROCESS_NAMES = new Set(['systemd', 'launchd', 'init', 'kernel_task', 'sshd']);

export async function cmdFree(args, global) {
  const defs = new Map([
    ['--yes', { key: 'yes', type: 'boolean' }],
    ['--signal', { key: 'signal', type: 'string' }],
    ['--force', { key: 'force', type: 'boolean' }],
    ['--dry-run', { key: 'dryRun', type: 'boolean' }]
  ]);

  try {
    const port = parsePort(args[0]);
    const { options } = parseArgs(args.slice(1), defs);
    const signal = options.force ? 'SIGKILL' : options.signal || 'SIGTERM';

    const initial = probeTcpPort(port, global);
    const records = normalizeRecords(initial.records);
    if (records.length === 0) {
      if (initial.probeFailed) {
        return createProbeError(
          'free',
          { port, released: false, diagnostics: initial.diagnostics },
          initial,
          `Unable to inspect port ${port} due permission restrictions`
        );
      }
      return createResult('free', { port, released: false }, {
        ok: false,
        exitCode: EXIT_CODES.PORT_NOT_OCCUPIED,
        errors: [toCommandError('not-occupied', `Port ${port} is not occupied`)]
      });
    }

    const blocked = records.find((record) => PROTECTED_PROCESS_NAMES.has(record.command));
    if (blocked) {
      return createResult('free', { port, records }, {
        ok: false,
        exitCode: EXIT_CODES.PERMISSION_DENIED,
        errors: [toCommandError('protected-process', `Refusing to stop protected process ${blocked.command} (${blocked.pid})`)]
      });
    }

    const targets = records.map((record) => ({ ...record, fingerprint: fingerprint(record) }));

    if (!options.yes) {
      const preview = targets.map((record) => `${record.pid} ${record.command} cwd=${record.cwd || '<unknown>'} started=${record.startTime}`);
      const accepted = await confirmPrompt(`Free port ${port}?\n${preview.join('\n')}`);
      if (!accepted) {
        return createResult('free', { port, released: false, canceled: true });
      }
    }

    const recheck = probeTcpPort(port, global);
    if (recheck.probeFailed) {
      return createProbeError(
        'free',
        { port, released: false, diagnostics: recheck.diagnostics },
        recheck,
        `Unable to re-check port ${port} due permission restrictions`
      );
    }
    const current = normalizeRecords(recheck.records);
    for (const target of targets) {
      const match = current.find((record) => fingerprint(record) === target.fingerprint);
      if (!match) {
        return createResult('free', { port, released: false, targetFingerprint: target.fingerprint }, {
          ok: false,
          exitCode: EXIT_CODES.TARGET_CHANGED,
          errors: [toCommandError('target-changed', `Process state changed before kill for pid ${target.pid}`)]
        });
      }
    }

    if (options.dryRun) {
      return createResult('free', {
        port,
        released: false,
        dryRun: true,
        action: `Would send ${signal} to ${targets.map((x) => x.pid).join(', ')}`,
        targetFingerprint: targets.map((x) => x.fingerprint)
      });
    }

    const killed = [];
    for (const target of targets) {
      try {
        process.kill(target.pid, signal);
        killed.push({ pid: target.pid, signal });
      } catch (error) {
        if (classifyPermissionError(error)) {
          return createResult('free', { port, killed }, {
            ok: false,
            exitCode: EXIT_CODES.PERMISSION_DENIED,
            errors: [toCommandError('permission-denied', `Permission denied when signaling pid ${target.pid}`, 'Try with sudo')]
          });
        }
        return createResult('free', { port, killed }, {
          ok: false,
          exitCode: EXIT_CODES.SYSTEM_PROBE_FAILED,
          errors: [toCommandError('kill-failed', error.message)]
        });
      }
    }

    if (signal === 'SIGTERM') {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const afterTerm = probeTcpPort(port, global);
      if (afterTerm.probeFailed) {
        return createProbeError(
          'free',
          { port, released: false, killed, diagnostics: afterTerm.diagnostics },
          afterTerm,
          `Unable to verify port ${port} after SIGTERM due permission restrictions`
        );
      }
      if (afterTerm.occupied) {
        if (!options.yes) {
          const confirmKill = await confirmPrompt(`Port ${port} is still occupied. Escalate to SIGKILL?`);
          if (!confirmKill) {
            return createResult('free', { port, released: false, killed, pending: true }, {
              ok: false,
              exitCode: EXIT_CODES.SYSTEM_PROBE_FAILED,
              errors: [toCommandError('still-occupied', `Port ${port} is still occupied after SIGTERM`)]
            });
          }
        }

        const afterTargets = normalizeRecords(afterTerm.records);
        for (const record of afterTargets) {
          try {
            process.kill(record.pid, 'SIGKILL');
            killed.push({ pid: record.pid, signal: 'SIGKILL' });
          } catch (error) {
            return createResult('free', { port, killed }, {
              ok: false,
              exitCode: EXIT_CODES.SYSTEM_PROBE_FAILED,
              errors: [toCommandError('kill-failed', error.message)]
            });
          }
        }
      }
    }

    const finalProbe = probeTcpPort(port, global);
    if (finalProbe.probeFailed) {
      return createProbeError(
        'free',
        {
          port,
          released: false,
          killed,
          targetFingerprint: targets.map((x) => x.fingerprint),
          revalidated: false,
          diagnostics: finalProbe.diagnostics
        },
        finalProbe,
        `Unable to verify final port state for ${port} due permission restrictions`
      );
    }
    return createResult('free', {
      port,
      released: !finalProbe.occupied,
      killed,
      targetFingerprint: targets.map((x) => x.fingerprint),
      revalidated: true
    }, {
      ok: !finalProbe.occupied,
      exitCode: !finalProbe.occupied ? EXIT_CODES.OK : EXIT_CODES.SYSTEM_PROBE_FAILED,
      errors: !finalProbe.occupied ? [] : [toCommandError('still-occupied', `Port ${port} remains occupied`)]
    });
  } catch (error) {
    return createResult('free', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
  }
}

export async function cmdInit(args, global, cwd) {
  const defs = new Map([
    ['--dry-run', { key: 'dryRun', type: 'boolean' }],
    ['--force', { key: 'force', type: 'boolean' }],
    ['--merge', { key: 'merge', type: 'boolean' }],
    ['--root', { key: 'root', type: 'string' }],
    ['--exclude', { key: 'exclude', type: 'string' }]
  ]);

  try {
    const { options } = parseArgs(args, defs);
    const root = path.resolve(cwd, options.root || '.');
    const configPath = path.join(root, '.portmanrc');

    const { config: scanned, stats } = await scanForConfig(root, { exclude: options.exclude });
    let finalConfig = scanned;

    const existing = await readConfig(configPath);
    if (existing.ok && options.merge) {
      finalConfig = mergeConfig(existing.value, scanned);
    }

    if (existing.ok && !options.merge && !options.force && !options.dryRun) {
      return createResult('init', { path: configPath }, {
        ok: false,
        exitCode: EXIT_CODES.CONFIG_ERROR,
        errors: [toCommandError('config-exists', 'Config exists. Use --merge or --force')]
      });
    }

    const warnings = [];
    if (stats.truncated) {
      warnings.push('Scan truncated by time or size limits');
    }

    if (!options.dryRun) {
      await fs.writeFile(configPath, `${JSON.stringify(finalConfig, null, 2)}\n`);
    }

    return createResult('init', {
      path: configPath,
      dryRun: Boolean(options.dryRun),
      mode: options.merge ? 'merge' : options.force ? 'force' : 'create',
      stats,
      config: finalConfig
    }, { warnings });
  } catch (error) {
    return createResult('init', null, {
      ok: false,
      exitCode: EXIT_CODES.CONFIG_ERROR,
      errors: [toCommandError('init-failed', error.message)]
    });
  }
}

export async function cmdConfig(args, global, cwd) {
  const action = args[0];
  const configPath = path.join(cwd, '.portmanrc');

  if (!action || !['lint', 'migrate'].includes(action)) {
    return createResult('config', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', 'Usage: portpilot config <lint|migrate>')]
    });
  }

  const loaded = await readConfig(configPath);
  if (!loaded.ok) {
    return createResult('config', null, {
      ok: false,
      exitCode: EXIT_CODES.CONFIG_ERROR,
      errors: [toCommandError('config-missing', loaded.error)]
    });
  }

  if (action === 'lint') {
    const errors = lintConfig(loaded.value);
    return createResult('config', {
      path: configPath,
      valid: errors.length === 0,
      lintErrors: errors
    }, {
      ok: errors.length === 0,
      exitCode: errors.length === 0 ? EXIT_CODES.OK : EXIT_CODES.CONFIG_ERROR,
      errors: errors.map((e) => toCommandError('lint-error', e))
    });
  }

  const migrated = migrateConfig(loaded.value);
  await fs.writeFile(configPath, `${JSON.stringify(migrated, null, 2)}\n`);
  return createResult('config', {
    path: configPath,
    migrated: true,
    version: migrated.version
  });
}

export function helpText() {
  return `PortPilot\n\nUsage:\n  portpilot who <port>\n  portpilot pick --range 3000-3999 --count 1\n  portpilot claim --lease-id <id>\n  portpilot scan [--protocol tcp|udp|both]\n  portpilot doctor [--strict] [--preflight]\n  portpilot free <port> [--yes] [--signal SIGTERM|SIGKILL] [--dry-run]\n  portpilot init [--dry-run] [--merge|--force] [--root <path>]\n  portpilot config <lint|migrate>\n\nGlobal flags:\n  --json --cwd <path> --quiet --verbose --no-color --timeout <ms>`;
}
