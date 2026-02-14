import fs from 'node:fs/promises';
import path from 'node:path';
import { relativeTo, safeJsonParse } from './utils.js';

const DEFAULT_EXCLUDES = [
  'node_modules',
  '.git',
  'dist',
  'build',
  '.next',
  '.turbo',
  '.cache'
];

export function defaultConfig() {
  return {
    $schema: 'https://portpilot.dev/schema/portmanrc.v1.json',
    version: 1,
    tool: {
      version: '0.1.0'
    },
    defaults: {
      range: '3000-3999',
      freePolicy: 'confirm-first',
      pickStrategy: 'lowest-first'
    },
    scan: {
      include: ['.'],
      exclude: DEFAULT_EXCLUDES.map((x) => `**/${x}/**`),
      maxDepth: 8,
      maxFiles: 10000,
      maxFileSizeKB: 2048,
      maxTotalScanMB: 200,
      scanTimeoutMs: 20000
    },
    resolutionPolicy: 'suggest',
    projects: [],
    reservedPorts: [5432, 6379],
    ranges: [
      { name: 'frontend', value: '3000-3999' },
      { name: 'backend', value: '7000-7999' }
    ]
  };
}

function shouldSkipDir(name, extraExcludes = []) {
  return DEFAULT_EXCLUDES.includes(name) || extraExcludes.includes(name);
}

async function walk(root, options = {}) {
  const {
    maxDepth = 8,
    maxFiles = 10000,
    maxFileSizeKB = 2048,
    maxTotalScanMB = 200,
    scanTimeoutMs = 20000,
    extraExcludes = []
  } = options;

  const out = [];
  const start = Date.now();
  let totalBytes = 0;

  async function visit(dir, depth) {
    if (Date.now() - start > scanTimeoutMs) {
      return;
    }
    if (depth > maxDepth || out.length >= maxFiles) {
      return;
    }

    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      if (Date.now() - start > scanTimeoutMs || out.length >= maxFiles) {
        return;
      }

      const abs = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (shouldSkipDir(entry.name, extraExcludes)) {
          continue;
        }
        await visit(abs, depth + 1);
        continue;
      }

      if (!entry.isFile()) {
        continue;
      }

      let stat;
      try {
        stat = await fs.stat(abs);
      } catch {
        continue;
      }

      if (stat.size > maxFileSizeKB * 1024) {
        continue;
      }
      totalBytes += stat.size;
      if (totalBytes > maxTotalScanMB * 1024 * 1024) {
        return;
      }

      out.push(abs);
    }
  }

  await visit(root, 0);
  return {
    files: out,
    truncated: out.length >= maxFiles || totalBytes > maxTotalScanMB * 1024 * 1024 || Date.now() - start > scanTimeoutMs,
    elapsedMs: Date.now() - start,
    totalBytes
  };
}

function extractPorts(text) {
  const ports = [];
  const patterns = [
    /(?:--port|-p)\s+(\d{2,5})/g,
    /(?:^|\s)PORT\s*=\s*(\d{2,5})\b/gm,
    /port\s*[:=]\s*(\d{2,5})/gi,
    /["']?(\d{2,5})\s*:\s*(\d{2,5})["']?/g
  ];

  for (const pattern of patterns) {
    for (const match of text.matchAll(pattern)) {
      const candidate = match[2] ? Number(match[1]) : Number(match[1]);
      if (candidate >= 1 && candidate <= 65535) {
        ports.push(candidate);
      }
    }
  }

  return [...new Set(ports)];
}

async function scanPackageJson(file) {
  try {
    const raw = await fs.readFile(file, 'utf8');
    const parsed = JSON.parse(raw);
    const scripts = parsed.scripts ?? {};
    const ports = new Set();
    const source = [];

    for (const [scriptName, scriptValue] of Object.entries(scripts)) {
      const found = extractPorts(String(scriptValue));
      for (const p of found) {
        ports.add(p);
        source.push(`package.json:scripts.${scriptName}`);
      }
    }

    return {
      name: parsed.name || path.basename(path.dirname(file)),
      root: path.dirname(file),
      declaredPorts: [...ports].sort((a, b) => a - b),
      source,
      confidence: ports.size > 0 ? 'high' : 'low'
    };
  } catch {
    return null;
  }
}

function nearestProjectRoot(file, projectRoots, root) {
  let best = root;
  let bestLen = 0;
  for (const p of projectRoots) {
    if (file.startsWith(`${p}${path.sep}`) && p.length > bestLen) {
      best = p;
      bestLen = p.length;
    }
  }
  return best;
}

export async function scanForConfig(root, options = {}) {
  const excludes = (options.exclude || '')
    .split(',')
    .map((x) => x.trim())
    .filter(Boolean)
    .map((x) => x.replace(/\*\*/g, '').replaceAll('/', '').trim())
    .filter(Boolean);

  const scan = await walk(root, {
    maxDepth: 8,
    maxFiles: 10000,
    maxFileSizeKB: 2048,
    maxTotalScanMB: 200,
    scanTimeoutMs: 20000,
    extraExcludes: excludes
  });

  const packageFiles = scan.files.filter((f) => path.basename(f) === 'package.json');
  const projects = new Map();

  for (const pkg of packageFiles) {
    const p = await scanPackageJson(pkg);
    if (!p) {
      continue;
    }
    projects.set(p.root, {
      name: p.name,
      root: p.root,
      declaredPorts: [...p.declaredPorts],
      source: [...p.source],
      confidence: p.confidence,
      protocol: 'tcp'
    });
  }

  if (!projects.has(root)) {
    projects.set(root, {
      name: path.basename(root),
      root,
      declaredPorts: [],
      source: [],
      confidence: 'low',
      protocol: 'tcp'
    });
  }

  const projectRoots = [...projects.keys()].sort((a, b) => b.length - a.length);
  const candidateFiles = scan.files.filter((file) => {
    const base = path.basename(file);
    return (
      base.startsWith('.env') ||
      /^vite\.config\./.test(base) ||
      /^next\.config\./.test(base) ||
      /^nuxt\.config\./.test(base) ||
      /^docker-compose.*\.ya?ml$/.test(base)
    );
  });

  for (const file of candidateFiles) {
    let text = '';
    try {
      text = await fs.readFile(file, 'utf8');
    } catch {
      continue;
    }
    const ports = extractPorts(text);
    if (ports.length === 0) {
      continue;
    }
    const bucketRoot = nearestProjectRoot(file, projectRoots, root);
    const bucket = projects.get(bucketRoot);
    const fileRel = relativeTo(root, file);
    for (const port of ports) {
      if (!bucket.declaredPorts.includes(port)) {
        bucket.declaredPorts.push(port);
      }
      bucket.source.push(fileRel);
    }
    if (bucket.confidence !== 'high') {
      bucket.confidence = 'medium';
    }
  }

  const config = defaultConfig();
  config.projects = [...projects.values()]
    .map((project) => ({
      name: project.name,
      root: relativeTo(root, project.root),
      declaredPorts: [...new Set(project.declaredPorts)].sort((a, b) => a - b),
      preferredRange: project.declaredPorts.length > 0
        ? `${Math.floor(Math.min(...project.declaredPorts) / 100) * 100}-${Math.floor(Math.max(...project.declaredPorts) / 100) * 100 + 99}`
        : '3000-3099',
      protocol: 'tcp',
      source: [...new Set(project.source)],
      confidence: project.confidence
    }))
    .filter((project) => project.declaredPorts.length > 0 || project.root === '.');

  return {
    config,
    stats: {
      scannedFiles: scan.files.length,
      elapsedMs: scan.elapsedMs,
      truncated: scan.truncated
    }
  };
}

export async function readConfig(configPath) {
  try {
    const raw = await fs.readFile(configPath, 'utf8');
    const parsed = safeJsonParse(raw);
    if (!parsed.ok) {
      return { ok: false, error: `Invalid JSON: ${parsed.error.message}` };
    }
    return { ok: true, value: parsed.value };
  } catch (error) {
    if (error?.code === 'ENOENT') {
      return { ok: false, error: 'Config file not found' };
    }
    return { ok: false, error: error.message };
  }
}

export function lintConfig(config) {
  const errors = [];

  if (typeof config !== 'object' || config === null) {
    errors.push('Config must be an object');
    return errors;
  }

  if (config.version !== 1) {
    errors.push('version must equal 1');
  }

  if (!Array.isArray(config.projects)) {
    errors.push('projects must be an array');
  } else {
    for (const project of config.projects) {
      if (!project || typeof project !== 'object') {
        errors.push('project must be an object');
        continue;
      }
      if (!Array.isArray(project.declaredPorts)) {
        errors.push(`project ${project.name || '<unknown>'} declaredPorts must be array`);
      }
    }
  }

  return errors;
}

export function mergeConfig(base, incoming) {
  const out = {
    ...base,
    ...incoming,
    defaults: { ...(base.defaults || {}), ...(incoming.defaults || {}) },
    tool: { ...(base.tool || {}), ...(incoming.tool || {}) },
    scan: { ...(base.scan || {}), ...(incoming.scan || {}) }
  };

  const map = new Map();
  for (const project of [...(base.projects || []), ...(incoming.projects || [])]) {
    const key = project.root || project.name;
    if (!map.has(key)) {
      map.set(key, {
        ...project,
        declaredPorts: [...(project.declaredPorts || [])],
        source: [...(project.source || [])]
      });
      continue;
    }

    const current = map.get(key);
    current.declaredPorts = [...new Set([...(current.declaredPorts || []), ...(project.declaredPorts || [])])].sort((a, b) => a - b);
    current.source = [...new Set([...(current.source || []), ...(project.source || [])])];
    current.confidence = current.confidence === 'high' || project.confidence === 'high' ? 'high' : 'medium';
    map.set(key, current);
  }

  out.projects = [...map.values()];
  out.reservedPorts = [...new Set([...(base.reservedPorts || []), ...(incoming.reservedPorts || [])])].sort((a, b) => a - b);

  const ranges = new Map();
  for (const range of [...(base.ranges || []), ...(incoming.ranges || [])]) {
    ranges.set(range.name, range);
  }
  out.ranges = [...ranges.values()];

  return out;
}

export function migrateConfig(config) {
  const out = { ...defaultConfig(), ...config };
  out.version = 1;
  out.tool = { ...(defaultConfig().tool || {}), ...(config.tool || {}) };
  out.defaults = { ...(defaultConfig().defaults || {}), ...(config.defaults || {}) };
  out.scan = { ...(defaultConfig().scan || {}), ...(config.scan || {}) };
  out.resolutionPolicy = config.resolutionPolicy || 'suggest';
  out.projects = Array.isArray(config.projects) ? config.projects : [];
  out.reservedPorts = Array.isArray(config.reservedPorts) ? config.reservedPorts : defaultConfig().reservedPorts;
  out.ranges = Array.isArray(config.ranges) ? config.ranges : defaultConfig().ranges;
  return out;
}
