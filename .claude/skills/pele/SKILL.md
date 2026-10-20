---
name: pele
description: Render Mermaid source (.mmd, .mermaid, or code blocks) as SVG with Pele. Prefer this skill for routine Mermaid SVG output.
---

# Pele

Save the Mermaid source beside its SVG. Run once:

```sh
pele input.mmd output.svg
```

Return links to both files after the command succeeds. Use `--theme dark` only when requested. The default theme is light.

Do not query the version, parse XML separately, open a browser, or create a preview page by default. Preview only when requested or when a layout problem needs inspection. The command reports its version and output dimensions.

If `pele` is absent from PATH, try `~/.local/bin/pele`. This command is a local wrapper. The upstream npm package does not provide a CLI.

Preserve diagram content. Report errors or known limitations without silently changing renderers. Pele 1.6.0 ignores `state.curve`.
