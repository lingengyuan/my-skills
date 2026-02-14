import path from 'node:path';
import {
  EXIT_CODES,
  createResult,
  parseGlobalArgs,
  printResult,
  toCommandError
} from './utils.js';
import {
  cmdClaim,
  cmdConfig,
  cmdDoctor,
  cmdFree,
  cmdInit,
  cmdPick,
  cmdScan,
  cmdWho,
  helpText
} from './commands.js';

export async function runCli(rawArgv = process.argv.slice(2)) {
  let global;
  let rest;

  try {
    ({ global, rest } = parseGlobalArgs(rawArgv));
  } catch (error) {
    const result = createResult('global', null, {
      ok: false,
      exitCode: EXIT_CODES.ARG_ERROR,
      errors: [toCommandError('arg-error', error.message)]
    });
    printResult(result, global || {});
    process.exitCode = result.exitCode;
    return;
  }

  const command = rest[0];
  const args = rest.slice(1);
  const cwd = global.cwd ? path.resolve(global.cwd) : process.cwd();

  if (!command || ['-h', '--help', 'help'].includes(command)) {
    const result = createResult('help', helpText());
    printResult(result, global);
    process.exitCode = EXIT_CODES.OK;
    return;
  }

  if (command === '--version' || command === '-v' || command === 'version') {
    const result = createResult('version', { version: '0.1.0' });
    printResult(result, global);
    process.exitCode = EXIT_CODES.OK;
    return;
  }

  let result;
  switch (command) {
    case 'who':
      result = await cmdWho(args, global);
      break;
    case 'pick':
      result = await cmdPick(args, global);
      break;
    case 'claim':
      result = await cmdClaim(args, global);
      break;
    case 'scan':
      result = await cmdScan(args, global);
      break;
    case 'doctor':
      result = await cmdDoctor(args, global, cwd);
      break;
    case 'free':
      result = await cmdFree(args, global);
      break;
    case 'init':
      result = await cmdInit(args, global, cwd);
      break;
    case 'config':
      result = await cmdConfig(args, global, cwd);
      break;
    default:
      result = createResult(command, null, {
        ok: false,
        exitCode: EXIT_CODES.ARG_ERROR,
        errors: [toCommandError('unknown-command', `Unknown command: ${command}`)]
      });
      break;
  }

  printResult(result, global);
  process.exitCode = result.exitCode;
}
