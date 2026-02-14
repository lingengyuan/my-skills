import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function runRaw(command, args, { timeout = 3000 } = {}) {
  const result = spawnSync(command, args, {
    encoding: 'utf8',
    timeout,
    windowsHide: true
  });

  if (result.error) {
    return {
      ok: false,
      status: -1,
      stdout: result.stdout ?? '',
      stderr: result.stderr ?? '',
      error: result.error
    };
  }

  return {
    ok: result.status === 0,
    status: result.status ?? -1,
    stdout: result.stdout ?? '',
    stderr: result.stderr ?? ''
  };
}

function stderrHasPermissionHint(stderr = '') {
  const text = String(stderr).toLowerCase();
  return (
    text.includes('operation not permitted') ||
    text.includes('permission denied') ||
    text.includes('cannot open netlink socket') ||
    text.includes('cannot open a network socket')
  );
}

function resultHasPermissionIssue(result) {
  if (!result) {
    return false;
  }
  const code = result.error?.code;
  if (code === 'EPERM' || code === 'EACCES') {
    return true;
  }
  return stderrHasPermissionHint(result.stderr);
}

function summarizeProbeResults(results) {
  return {
    probeFailed: results.length > 0 && results.every((result) => !result.ok),
    permissionDenied: results.some((result) => resultHasPermissionIssue(result))
  };
}

export function which(cmd, options = {}) {
  if (!cmd) {
    return '';
  }

  if (cmd.includes('/')) {
    try {
      fs.accessSync(cmd, fs.constants.X_OK);
      return cmd;
    } catch {
      return '';
    }
  }

  const pathEnv = process.env.PATH || '';
  for (const base of pathEnv.split(path.delimiter).filter(Boolean)) {
    const candidate = path.join(base, cmd);
    try {
      fs.accessSync(candidate, fs.constants.X_OK);
      return candidate;
    } catch {
      // continue
    }
  }
  return '';
}

export function detectPackageManager(options = {}) {
  for (const pm of ['apt-get', 'dnf', 'yum', 'pacman', 'zypper', 'apk', 'brew']) {
    if (which(pm, options)) {
      return pm;
    }
  }
  return '';
}

export function installHintFor(pm) {
  switch (pm) {
    case 'apt-get':
      return 'sudo apt-get update && sudo apt-get install -y lsof iproute2 psmisc';
    case 'dnf':
      return 'sudo dnf install -y lsof iproute psmisc';
    case 'yum':
      return 'sudo yum install -y lsof iproute psmisc';
    case 'pacman':
      return 'sudo pacman -S --needed lsof iproute2 psmisc';
    case 'zypper':
      return 'sudo zypper install -y lsof iproute2 psmisc';
    case 'apk':
      return 'sudo apk add lsof iproute2 psmisc';
    case 'brew':
      return 'xcode-select --install # optional: brew install lsof iproute2mac';
    default:
      return '';
  }
}

export function getPlatform() {
  const p = os.platform();
  if (p === 'darwin') {
    return 'macos';
  }
  if (p === 'linux') {
    return 'linux';
  }
  return p;
}

export function runCommand(command, args, options = {}) {
  return runRaw(command, args, options);
}

function parsePsLine(line) {
  const parts = line.trim().split(/\s+/);
  if (parts.length < 7) {
    return null;
  }

  const pid = Number(parts[0]);
  const ppid = Number(parts[1]);
  const user = parts[2];
  const command = parts[3];
  const startTime = parts.slice(4).join(' ');

  return { pid, ppid, user, command, startTime };
}

export function getProcessInfo(pid, options = {}) {
  const ps = runRaw('ps', ['-p', String(pid), '-o', 'pid=,ppid=,user=,comm=,lstart='], options);
  if (!ps.ok) {
    return null;
  }

  const line = ps.stdout
    .split('\n')
    .map((x) => x.trim())
    .find(Boolean);

  if (!line) {
    return null;
  }

  const parsed = parsePsLine(line);
  if (!parsed) {
    return null;
  }

  const platform = getPlatform();
  let cwd = '';
  if (platform === 'linux') {
    const pwdx = runRaw('pwdx', [String(pid)], options);
    if (pwdx.ok) {
      const m = /:\s*(.+)$/.exec(pwdx.stdout.trim());
      if (m) {
        cwd = m[1].trim();
      }
    }
  }

  if (!cwd) {
    const lsof = runRaw('lsof', ['-a', '-p', String(pid), '-d', 'cwd', '-Fn'], options);
    if (lsof.ok) {
      const pathLine = lsof.stdout
        .split('\n')
        .map((x) => x.trim())
        .find((x) => x.startsWith('n'));
      if (pathLine) {
        cwd = pathLine.slice(1);
      }
    }
  }

  return { ...parsed, cwd };
}

function parseLsofOutput(port, raw, options = {}) {
  const lines = raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length <= 1) {
    return [];
  }

  const records = [];
  for (const line of lines.slice(1)) {
    const chunks = line.split(/\s+/);
    if (chunks.length < 2) {
      continue;
    }
    const command = chunks[0];
    const pid = Number(chunks[1]);
    if (!Number.isInteger(pid)) {
      continue;
    }
    const extra = getProcessInfo(pid, options) ?? { pid, ppid: null, user: chunks[2] || '', command, startTime: '', cwd: '' };
    records.push({
      port,
      protocol: 'tcp',
      pid,
      ppid: extra.ppid,
      user: extra.user,
      command: extra.command || command,
      cwd: extra.cwd,
      startTime: extra.startTime,
      isLikelyDevProcess: /node|python|vite|next|nuxt|webpack|bun|deno|go|java/i.test(extra.command || command)
    });
  }
  return records;
}

function parseSsOutput(port, raw, options = {}) {
  const lines = raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => line.startsWith('LISTEN'));

  const records = [];
  for (const line of lines) {
    const pidMatches = [...line.matchAll(/pid=(\d+)/g)].map((m) => Number(m[1]));
    const commandMatch = /users:\(\("([^\"]+)"/.exec(line);

    for (const pid of pidMatches) {
      const extra = getProcessInfo(pid, options) ?? { pid, ppid: null, user: '', command: commandMatch?.[1] || '', startTime: '', cwd: '' };
      records.push({
        port,
        protocol: 'tcp',
        pid,
        ppid: extra.ppid,
        user: extra.user,
        command: extra.command || commandMatch?.[1] || '',
        cwd: extra.cwd,
        startTime: extra.startTime,
        isLikelyDevProcess: /node|python|vite|next|nuxt|webpack|bun|deno|go|java/i.test(extra.command || commandMatch?.[1] || '')
      });
    }
  }

  return records;
}

function parseFuserOutput(port, raw, options = {}) {
  const nums = raw
    .split(/\s+/)
    .map((x) => x.trim())
    .filter((x) => /^\d+$/.test(x))
    .map(Number);

  return nums.map((pid) => {
    const extra = getProcessInfo(pid, options) ?? { pid, ppid: null, user: '', command: '', startTime: '', cwd: '' };
    return {
      port,
      protocol: 'tcp',
      pid,
      ppid: extra.ppid,
      user: extra.user,
      command: extra.command,
      cwd: extra.cwd,
      startTime: extra.startTime,
      isLikelyDevProcess: /node|python|vite|next|nuxt|webpack|bun|deno|go|java/i.test(extra.command || '')
    };
  });
}

function extractPortFromAddress(address) {
  const match = /:(\d+)$/.exec(String(address ?? '').trim());
  if (!match) {
    return null;
  }
  const port = Number(match[1]);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    return null;
  }
  return port;
}

function parseSsListening(stdout, protocol) {
  const lines = stdout
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => line.startsWith('LISTEN') || line.startsWith('UNCONN'));

  const records = [];
  for (const line of lines) {
    const parts = line.split(/\s+/);
    if (parts.length < 5) {
      continue;
    }
    const localAddress = parts[3];
    const port = extractPortFromAddress(localAddress);
    if (!port) {
      continue;
    }

    const pidMatches = [...line.matchAll(/pid=(\d+)/g)].map((m) => Number(m[1]));
    const commandMatch = /users:\(\("([^\"]+)"/.exec(line);
    records.push({
      protocol,
      localAddress,
      port,
      pids: pidMatches,
      command: commandMatch?.[1] || ''
    });
  }
  return records;
}

function parseLsofListening(stdout) {
  const lines = stdout
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length <= 1) {
    return [];
  }

  const records = [];
  for (const line of lines.slice(1)) {
    const parts = line.split(/\s+/);
    if (parts.length < 9) {
      continue;
    }
    const command = parts[0] || '';
    const pid = Number(parts[1]);
    const endpoint = parts[8] || '';
    const port = extractPortFromAddress(endpoint);
    if (!port) {
      continue;
    }
    records.push({
      protocol: 'tcp',
      localAddress: endpoint.split('->')[0],
      port,
      pids: Number.isInteger(pid) ? [pid] : [],
      command
    });
  }

  return records;
}

export function listListeningPorts(options = {}) {
  const timeout = options.timeout ?? 3000;
  const diagnostics = [];
  const probeResults = [];

  const tcp = runRaw('ss', ['-ltnp'], { timeout });
  probeResults.push(tcp);
  diagnostics.push({ probe: 'ss-tcp', ok: tcp.ok, status: tcp.status, stderr: tcp.stderr.trim() });
  const udp = runRaw('ss', ['-lunp'], { timeout });
  probeResults.push(udp);
  diagnostics.push({ probe: 'ss-udp', ok: udp.ok, status: udp.status, stderr: udp.stderr.trim() });

  let records = [
    ...parseSsListening(tcp.stdout, 'tcp'),
    ...parseSsListening(udp.stdout, 'udp')
  ];

  if (records.length === 0) {
    const lsof = runRaw('lsof', ['-nP', '-iTCP', '-sTCP:LISTEN'], { timeout });
    probeResults.push(lsof);
    diagnostics.push({ probe: 'lsof-listen', ok: lsof.ok, status: lsof.status, stderr: lsof.stderr.trim() });
    records = parseLsofListening(lsof.stdout);
  }

  const dedupe = new Map();
  for (const record of records) {
    const key = `${record.protocol}:${record.port}:${record.command}:${record.pids.join(',')}`;
    dedupe.set(key, record);
  }

  const out = [...dedupe.values()].sort((a, b) => a.port - b.port);
  if (out.length > 0) {
    return { records: out, diagnostics, probeFailed: false, permissionDenied: false };
  }
  const { probeFailed, permissionDenied } = summarizeProbeResults(probeResults);
  return { records: out, diagnostics, probeFailed, permissionDenied };
}

export function probeTcpPort(port, options = {}) {
  const timeout = options.timeout ?? 3000;
  const diagnostics = [];
  const probeResults = [];

  const lsof = runRaw('lsof', ['-nP', `-iTCP:${port}`, '-sTCP:LISTEN'], { timeout });
  probeResults.push(lsof);
  diagnostics.push({ probe: 'lsof', ok: lsof.ok, status: lsof.status, stderr: lsof.stderr.trim() });
  if (lsof.ok && lsof.stdout.trim()) {
    return {
      occupied: true,
      records: parseLsofOutput(port, lsof.stdout, { timeout }),
      diagnostics,
      probeFailed: false,
      permissionDenied: false
    };
  }

  const ss = runRaw('ss', ['-lptn', `sport = :${port}`], { timeout });
  probeResults.push(ss);
  diagnostics.push({ probe: 'ss', ok: ss.ok, status: ss.status, stderr: ss.stderr.trim() });
  if (ss.ok && ss.stdout.trim()) {
    const records = parseSsOutput(port, ss.stdout, { timeout });
    if (records.length > 0) {
      return { occupied: true, records, diagnostics, probeFailed: false, permissionDenied: false };
    }
  }

  const fuser = runRaw('fuser', ['-n', 'tcp', String(port)], { timeout });
  probeResults.push(fuser);
  diagnostics.push({ probe: 'fuser', ok: fuser.ok, status: fuser.status, stderr: fuser.stderr.trim() });
  if (fuser.ok && fuser.stdout.trim()) {
    const records = parseFuserOutput(port, fuser.stdout, { timeout });
    if (records.length > 0) {
      return { occupied: true, records, diagnostics, probeFailed: false, permissionDenied: false };
    }
  }

  const { probeFailed, permissionDenied } = summarizeProbeResults(probeResults);
  return {
    occupied: false,
    records: [],
    diagnostics,
    probeFailed,
    permissionDenied
  };
}

export function listPreflight() {
  const platform = getPlatform();
  const pm = detectPackageManager();
  const required = platform === 'macos' ? ['lsof', 'ps', 'kill'] : ['ps', 'kill'];
  const alternatives = platform === 'linux' ? ['lsof', 'ss', 'fuser'] : [];

  const missing = [];
  for (const cmd of required) {
    if (!which(cmd)) {
      missing.push(cmd);
    }
  }

  if (platform === 'linux') {
    const hasAlternative = alternatives.some((cmd) => Boolean(which(cmd)));
    if (!hasAlternative) {
      missing.push('lsof|ss|fuser');
    }
  }

  if (platform === 'macos' && !which('lsof')) {
    missing.push('lsof');
  }

  const installHint = installHintFor(pm);

  return {
    platform,
    detectedPackageManager: pm,
    missingDeps: [...new Set(missing)],
    installHints: installHint ? [installHint] : []
  };
}
