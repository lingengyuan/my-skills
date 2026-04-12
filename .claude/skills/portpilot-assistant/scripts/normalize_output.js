#!/usr/bin/env node
import fs from 'node:fs';

const input = fs.readFileSync(0, 'utf8').trim();
if (!input) {
  process.exit(0);
}

try {
  const parsed = JSON.parse(input);
  const out = {
    ok: Boolean(parsed.ok),
    command: parsed.command,
    exitCode: parsed.exitCode,
    summary: parsed.ok ? 'success' : 'failed',
    data: parsed.data,
    errors: parsed.errors || []
  };
  process.stdout.write(`${JSON.stringify(out, null, 2)}\n`);
} catch {
  process.stdout.write(input + '\n');
}
