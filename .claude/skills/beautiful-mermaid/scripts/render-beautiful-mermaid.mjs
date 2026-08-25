#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync } from 'node:fs'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath, pathToFileURL } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))

function usage() {
  console.error([
    'Usage:',
    '  node render-beautiful-mermaid.mjs <input.mmd> <output.svg> [--format svg|ascii] [--theme name] [--ascii]',
    '',
    'Examples:',
    '  node render-beautiful-mermaid.mjs diagram.mmd diagram.svg',
    '  node render-beautiful-mermaid.mjs diagram.mmd diagram.svg --theme github-light',
    '  node render-beautiful-mermaid.mjs diagram.mmd diagram.txt --format ascii',
  ].join('\n'))
}

function parseArgs(argv) {
  const positional = []
  const options = {
    format: 'svg',
    theme: 'github-light',
  }

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--format') {
      options.format = requireValue(argv, ++index, '--format')
    } else if (arg === '--theme') {
      options.theme = requireValue(argv, ++index, '--theme')
    } else if (arg === '--ascii') {
      options.format = 'ascii'
    } else if (arg === '--help' || arg === '-h') {
      usage()
      process.exit(0)
    } else if (arg.startsWith('--')) {
      throw new Error(`Unknown option: ${arg}`)
    } else {
      positional.push(arg)
    }
  }

  if (positional.length !== 2) {
    usage()
    throw new Error('input and output paths are required')
  }
  if (!['svg', 'ascii'].includes(options.format)) {
    throw new Error(`Unsupported format: ${options.format}`)
  }

  return {
    inputPath: resolve(positional[0]),
    outputPath: resolve(positional[1]),
    ...options,
  }
}

function requireValue(argv, index, flag) {
  const value = argv[index]
  if (!value || value.startsWith('--')) {
    throw new Error(`${flag} requires a value`)
  }
  return value
}

async function loadBeautifulMermaid() {
  const errors = []

  try {
    return await import('beautiful-mermaid')
  } catch (error) {
    errors.push(`direct import: ${error.message}`)
  }

  const candidates = []
  if (process.env.BEAUTIFUL_MERMAID_NODE_PATH) {
    candidates.push(process.env.BEAUTIFUL_MERMAID_NODE_PATH)
  }
  candidates.push(process.cwd())
  candidates.push(scriptDir)
  candidates.push(resolve(scriptDir, '..'))
  if (process.env.APPDATA) {
    candidates.push(join(process.env.APPDATA, 'npm', 'node_modules'))
  }

  for (const npmCommand of process.platform === 'win32' ? ['npm.cmd', 'npm'] : ['npm']) {
    try {
      const globalRoot = execFileSync(npmCommand, ['root', '-g'], { encoding: 'utf8' }).trim()
      if (globalRoot) candidates.push(globalRoot)
      break
    } catch {
      // npm may be unavailable in restricted environments. Other candidates still apply.
    }
  }

  for (const base of candidates) {
    const normalizedBase = isAbsolute(base) ? base : resolve(base)
    const moduleFiles = [
      join(normalizedBase, 'dist', 'index.js'),
      join(normalizedBase, 'node_modules', 'beautiful-mermaid', 'dist', 'index.js'),
    ]

    for (const moduleFile of moduleFiles) {
      if (!existsSync(moduleFile)) continue

      try {
        return await import(pathToFileURL(moduleFile).href)
      } catch (error) {
        errors.push(`${moduleFile}: ${error.message}`)
      }
    }

    try {
      return await import(pathToFileURL(join(normalizedBase, 'beautiful-mermaid', 'dist', 'index.js')).href)
    } catch (error) {
      errors.push(`${base}: ${error.message}`)
    }
  }

  throw new Error(
    'Could not resolve beautiful-mermaid. Install it with `npm install -g beautiful-mermaid` or set BEAUTIFUL_MERMAID_NODE_PATH.\n'
    + errors.join('\n')
  )
}

function svgOptions(module, themeName) {
  const theme = module.THEMES?.[themeName] ?? module.THEMES?.['github-light'] ?? {}
  return {
    ...theme,
    font: 'Inter, Microsoft YaHei, PingFang SC, Noto Sans CJK SC, Arial, sans-serif',
    padding: 48,
    nodeSpacing: 32,
    layerSpacing: 56,
    componentSpacing: 32,
    thoroughness: 5,
  }
}

function asciiOptions() {
  return {
    useAscii: false,
    paddingX: 5,
    paddingY: 4,
    boxBorderPadding: 1,
    colorMode: 'none',
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  if (!existsSync(args.inputPath)) {
    throw new Error(`Input file does not exist: ${args.inputPath}`)
  }

  const source = readFileSync(args.inputPath, 'utf8')
  const module = await loadBeautifulMermaid()
  const output =
    args.format === 'ascii'
      ? module.renderMermaidASCII(source, asciiOptions())
      : module.renderMermaidSVG(source, svgOptions(module, args.theme))

  mkdirSync(dirname(args.outputPath), { recursive: true })
  writeFileSync(args.outputPath, output, 'utf8')

  const size = statSync(args.outputPath).size
  if (size <= 0) {
    throw new Error(`Rendered output is empty: ${args.outputPath}`)
  }
  if (args.format === 'svg' && !output.includes('<svg')) {
    throw new Error(`Rendered output does not look like SVG: ${args.outputPath}`)
  }

  console.log(JSON.stringify({
    ok: true,
    renderer: 'beautiful-mermaid',
    format: args.format,
    input: args.inputPath,
    output: args.outputPath,
    bytes: size,
    theme: args.theme,
  }, null, 2))
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
