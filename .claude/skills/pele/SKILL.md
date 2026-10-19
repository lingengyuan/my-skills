---
name: pele
description: Render, preview, and export Mermaid diagrams as SVG with Pele. Use for .mmd or .mermaid files, Mermaid code blocks, flowcharts, sequences, state diagrams, and diagram regeneration. Prefer this skill for routine Mermaid SVG output.
---

# Pele

Use the installed `pele` command to render Mermaid source. This machine provides a local CLI wrapper around the published package.

## Workflow

1. Preserve the Mermaid source. Save new source as `.mmd` beside its output, unless the user specifies another location.
2. Run `pele --version` to check the installed version.
3. Render the source:

```sh
pele input.mmd output.svg
pele input.mmd output-dark.svg --theme dark
```

The default theme is `light`. The local CLI accepts `light` and `dark`.
If the command is absent from PATH, check the current user's `.local/bin/pele`.
The upstream npm package has no CLI entry point. A global npm installation alone does not provide this command.

4. Check the exit code and parse the output as SVG XML. Preview the SVG to check labels, arrows, and group boundaries.
5. Return links to the source and SVG. State the Pele version and any remaining visual limitation.

## Source and compatibility

- Keep labels short, especially in Chinese. Preserve conditions and relationships when revising a diagram.
- Use SVG as the output format. Pele uses its own layout, so migration can change node positions and page dimensions.
- Use CSS variables for custom colors. Mermaid theme settings do not map directly to Pele colors.
- Check requested configuration behavior. Accepted input does not prove that every setting affects the output.
- Pele 1.6.0 ignores `state.curve`. Do not claim that it produces the requested linear or stepped state transitions.
- If Pele rejects the syntax, report the error. Do not silently change renderers or remove diagram content.

Official references: [API](https://pele.run/api), [compatibility](https://pele.run/compatibility), [theming](https://pele.run/theming).
