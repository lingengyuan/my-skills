---
name: pele
description: Render Mermaid diagrams as SVG with Pele. Use its JavaScript API for custom rendering, theming and browser integration.
---

# Pele

Use the official JavaScript API from the current local Pele installation. Do not pin a release.

Save the Mermaid source beside its SVG. Read, render and write in one Node invocation. For standalone use on this machine, the package is installed in `~/.local/share/pele`; run inline Node there with absolute input and output paths:

```sh
cd ~/.local/share/pele && node --input-type=module - /absolute/input.mmd /absolute/output.svg <<'JS'
import { readFileSync, writeFileSync } from 'node:fs';
import { render } from 'pele';

const [input, output] = process.argv.slice(2);
writeFileSync(output, render(readFileSync(input, 'utf8')).svg);
JS
```

Pass `RenderOptions` when the task needs custom layout, fonts, padding, diagram configuration, icons or math. Use CSS variables for theming. For browser integration, use `mount()` for container sizing, zoom and updates. Consult the installed types or official [API](https://pele.run/api) and [theming](https://pele.run/theming) docs only when needed.

Return links to the source and SVG after success. Do not query versions, fetch documentation, parse XML separately or create browser previews by default. Preview only when requested or when a layout problem needs inspection.

Preserve diagram content. Report errors or limitations without silently changing renderers. State diagrams use `flowchart.curve` for transitions.
