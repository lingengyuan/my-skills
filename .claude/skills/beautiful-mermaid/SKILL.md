---
name: beautiful-mermaid
description: Render, beautify, preview, or export Mermaid source as polished SVG or terminal text with beautiful-mermaid. Use for .mmd/.mermaid files, Mermaid code blocks, architecture diagrams, flowcharts, and diagram regeneration; use mmdc only when explicitly requested or when the bundled renderer does not support the syntax.
---

# Beautiful Mermaid

Render Mermaid source reproducibly with the script and dependency bundled in this Skill.

## Workflow

1. Resolve this Skill's directory from the loaded `SKILL.md`; never use a user-specific absolute path.
2. Preserve the Mermaid source and write the rendered artifact beside it unless the user specifies another path.
3. Run:

```bash
node "<skill-dir>/scripts/render-beautiful-mermaid.mjs" input.mmd output.svg
```

Optional forms:

```bash
node "<skill-dir>/scripts/render-beautiful-mermaid.mjs" input.mmd output.svg --theme github-light
node "<skill-dir>/scripts/render-beautiful-mermaid.mjs" input.mmd output.txt --format ascii
```

4. Verify that SVG output is non-empty and contains `<svg`. For text output, verify that it is non-empty.
5. If the package is missing, install it inside this Skill:

```bash
npm install --prefix "<skill-dir>"
```

6. If the syntax is unsupported, use `mmdc` and report the fallback.

## Source guidance

- Keep labels short, especially in Chinese.
- Preserve the source file; never replace it with rendered output.
- Use SVG by default. Use ASCII only when terminal output is requested.

## Report

Return the source path, output path, renderer used, and any remaining visual limitation.
