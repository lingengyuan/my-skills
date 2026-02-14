import os from 'node:os';
import path from 'node:path';

export const EXIT_CODES = {
  OK: 0,
  ARG_ERROR: 2,
  PORT_NOT_OCCUPIED: 4,
  SYSTEM_PROBE_FAILED: 10,
  CONFLICT_FOUND: 20,
  CONFIG_ERROR: 30,
  PERMISSION_DENIED: 40,
  LEASE_NOT_FOUND_OR_EXPIRED: 50,
  LEASE_RACE_LOST: 51,
  TARGET_CHANGED: 52
};

export const GLOBAL_FLAGS = new Map([
  ['--json', { key: 'json', type: 'boolean' }],
  ['--cwd', { key: 'cwd', type: 'string' }],
  ['--quiet', { key: 'quiet', type: 'boolean' }],
  ['--verbose', { key: 'verbose', type: 'boolean' }],
  ['--no-color', { key: 'noColor', type: 'boolean' }],
  ['--timeout', { key: 'timeout', type: 'number' }]
]);

export function nowIso() {
  return new Date().toISOString();
}

export function homeStateDir() {
  if (process.env.PORTPILOT_STATE_DIR) {
    return process.env.PORTPILOT_STATE_DIR;
  }

  if (process.env.XDG_STATE_HOME) {
    return path.join(process.env.XDG_STATE_HOME, 'portpilot');
  }

  return path.join(os.homedir(), '.portpilot');
}

export function parseArgs(argv, flagDefs = new Map()) {
  const options = {};
  const positionals = [];

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      positionals.push(token);
      continue;
    }

    const [rawKey, inlineValue] = token.split('=', 2);
    const def = flagDefs.get(rawKey);

    if (!def) {
      positionals.push(token);
      continue;
    }

    if (def.type === 'boolean') {
      options[def.key] = inlineValue ? inlineValue !== 'false' : true;
      continue;
    }

    const next = inlineValue ?? argv[i + 1];
    if (next === undefined || next.startsWith('--')) {
      throw new Error(`Missing value for ${rawKey}`);
    }

    if (inlineValue === undefined) {
      i += 1;
    }

    if (def.type === 'number') {
      const value = Number(next);
      if (!Number.isFinite(value)) {
        throw new Error(`Invalid number for ${rawKey}: ${next}`);
      }
      options[def.key] = value;
      continue;
    }

    options[def.key] = next;
  }

  return { options, positionals };
}

export function parseGlobalArgs(argv) {
  const { options, positionals } = parseArgs(argv, GLOBAL_FLAGS);
  if (!options.timeout) {
    options.timeout = 3000;
  }
  return { global: options, rest: positionals };
}

export function parsePort(input) {
  const port = Number(input);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error(`Invalid port: ${input}`);
  }
  return port;
}

export function parseRange(input) {
  const match = /^\s*(\d+)\s*-\s*(\d+)\s*$/.exec(String(input ?? ''));
  if (!match) {
    throw new Error(`Invalid range: ${input}`);
  }
  const start = Number(match[1]);
  const end = Number(match[2]);
  if (!Number.isInteger(start) || !Number.isInteger(end) || start < 1 || end > 65535 || start > end) {
    throw new Error(`Invalid range: ${input}`);
  }
  return { start, end };
}

export function parsePortList(input) {
  if (!input) {
    return [];
  }
  return String(input)
    .split(',')
    .map((x) => x.trim())
    .filter(Boolean)
    .map(parsePort);
}

export function createResult(command, data, { ok = true, warnings = [], errors = [], exitCode = EXIT_CODES.OK } = {}) {
  return {
    ok,
    command,
    timestamp: nowIso(),
    data,
    warnings,
    errors,
    exitCode
  };
}

export function printResult(result, { json = false, quiet = false } = {}) {
  if (json) {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    return;
  }

  if (result.ok) {
    if (!quiet) {
      process.stdout.write(`[ok] ${result.command}\n`);
    }
    if (result.data !== undefined) {
      if (typeof result.data === 'string') {
        process.stdout.write(`${result.data}\n`);
      } else {
        process.stdout.write(`${JSON.stringify(result.data, null, 2)}\n`);
      }
    }
  } else {
    process.stderr.write(`[error] ${result.command}\n`);
    for (const err of result.errors) {
      process.stderr.write(`- ${err.code}: ${err.message}${err.detail ? ` (${err.detail})` : ''}\n`);
    }
    if (result.warnings.length > 0) {
      for (const warning of result.warnings) {
        process.stderr.write(`- warning: ${warning}\n`);
      }
    }
  }
}

export function toCommandError(code, message, detail) {
  return { code, message, detail };
}

export function safeJsonParse(text) {
  try {
    return { ok: true, value: JSON.parse(text) };
  } catch (error) {
    return { ok: false, error };
  }
}

export function relativeTo(base, target) {
  const rel = path.relative(base, target);
  return rel === '' ? '.' : rel;
}
