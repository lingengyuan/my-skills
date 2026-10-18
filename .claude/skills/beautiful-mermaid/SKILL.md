---
name: beautiful-mermaid
description: Render Mermaid diagrams (.mmd, .mermaid, code blocks) to polished SVG or terminal ASCII using beautiful-mermaid. Use when generating diagrams, converting Mermaid files, previewing flowcharts or architecture diagrams, or when the user mentions beautiful-mermaid.
---

# Beautiful Mermaid Skill

Render Mermaid diagram source files into SVG images or ASCII terminal text with the bundled renderer. Standard Mermaid syntax is assumed knowledge.

## Workflow

1. **Locate directory**: Resolve `<skill-dir>` from the loaded `SKILL.md` path. Do not use hardcoded absolute user paths.
2. **Verify dependencies**: Verify that dependencies are installed. If missing, install them:
   ```bash
   npm install --prefix "<skill-dir>"
   ```
3. **Inspect source**: Read the input `.mmd` or Mermaid text. Keep node labels short and concise.
4. **Render output**: Execute the bundled script with the target output format (SVG by default).
5. **Verify result**: Verify that the output file exists, is non-empty, and contains valid syntax.
6. **Handle fallbacks**: If `beautiful-mermaid` fails on unsupported Mermaid syntax, use `mmdc` and report the fallback.

## CLI Usage

Run the bundled script with Node.js 18+:

```bash
# Default SVG output (theme: github-light)
node "<skill-dir>/scripts/render-beautiful-mermaid.mjs" input.mmd output.svg

# SVG with custom theme
node "<skill-dir>/scripts/render-beautiful-mermaid.mjs" input.mmd output.svg --theme github-dark

# ASCII text output for terminal viewing
node "<skill-dir>/scripts/render-beautiful-mermaid.mjs" input.mmd output.txt --format ascii
```

## Options

| Option | Value | Default | Description |
|--------|-------|---------|-------------|
| `--format` | `svg` \| `ascii` | `svg` | Output format |
| `--theme` | theme name | `github-light` | Theme name for SVG rendering |
| `--ascii` | flag | - | Shorthand for `--format ascii` |

## Guidelines

- **Preserve source**: Never overwrite or delete the input `.mmd` file. Write the rendered artifact beside it unless directed otherwise.
- **Format selection**: Use SVG by default. Use ASCII only when terminal text output is explicitly requested.
- **Label length**: Keep diagram node labels compact, especially for Chinese text, to prevent text truncation or layout overflow.

## Verification Checklist

Before completing the task, verify:

1. The output file exists and has non-zero byte size.
2. SVG files contain a valid root `<svg` element.
3. Text files contain legible ASCII characters.
4. The original Mermaid source file remains unmodified.
5. Report the input path, output path, and renderer used to the user.
