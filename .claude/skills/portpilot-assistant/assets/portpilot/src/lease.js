import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { homeStateDir } from './utils.js';

const LEASE_FILE = 'leases.json';
const LOCK_FILE = 'leases.lock';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function ensureDir() {
  const preferred = homeStateDir();
  try {
    await fs.mkdir(preferred, { recursive: true });
    return preferred;
  } catch (error) {
    if (error?.code !== 'EACCES' && error?.code !== 'EPERM') {
      throw error;
    }
    const fallback = '/tmp/.portpilot';
    await fs.mkdir(fallback, { recursive: true });
    return fallback;
  }
}

async function withLock(fn) {
  const dir = await ensureDir();
  const lockPath = path.join(dir, LOCK_FILE);
  const retries = 10;

  for (let i = 0; i < retries; i += 1) {
    try {
      const handle = await fs.open(lockPath, 'wx');
      try {
        return await fn(dir);
      } finally {
        await handle.close();
        await fs.rm(lockPath, { force: true });
      }
    } catch (error) {
      if (error?.code !== 'EEXIST') {
        throw error;
      }
      await sleep(20 * (i + 1));
    }
  }

  throw new Error('Could not acquire lease lock');
}

async function readStore(dir) {
  const file = path.join(dir, LEASE_FILE);
  try {
    const raw = await fs.readFile(file, 'utf8');
    const json = JSON.parse(raw);
    if (typeof json !== 'object' || json === null || typeof json.leases !== 'object') {
      return { leases: {} };
    }
    return json;
  } catch (error) {
    if (error?.code === 'ENOENT') {
      return { leases: {} };
    }
    return { leases: {} };
  }
}

async function writeStore(dir, store) {
  const file = path.join(dir, LEASE_FILE);
  const temp = path.join(dir, `${LEASE_FILE}.tmp`);
  await fs.writeFile(temp, JSON.stringify(store, null, 2));
  await fs.rename(temp, file);
}

function prune(store, now = Date.now()) {
  const leases = store.leases ?? {};
  for (const [id, lease] of Object.entries(leases)) {
    if (!lease || Number(lease.expiresAt) <= now) {
      delete leases[id];
    }
  }
  return { leases };
}

export async function createLeases(ports, leaseMs) {
  return withLock(async (dir) => {
    const now = Date.now();
    const store = prune(await readStore(dir), now);
    const out = [];

    for (const port of ports) {
      const id = crypto.randomUUID();
      const lease = {
        id,
        port,
        createdAt: now,
        expiresAt: now + leaseMs,
        ownerPid: process.pid
      };
      store.leases[id] = lease;
      out.push(lease);
    }

    await writeStore(dir, store);
    return out;
  });
}

export async function claimLease(id) {
  return withLock(async (dir) => {
    const now = Date.now();
    const store = prune(await readStore(dir), now);
    const lease = store.leases[id];
    if (!lease) {
      await writeStore(dir, store);
      return null;
    }

    delete store.leases[id];
    await writeStore(dir, store);
    return lease;
  });
}

export async function listLeases() {
  return withLock(async (dir) => {
    const store = prune(await readStore(dir), Date.now());
    await writeStore(dir, store);
    return Object.values(store.leases);
  });
}
