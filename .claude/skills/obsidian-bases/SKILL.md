---
name: obsidian-bases
description: Create, edit, and validate Obsidian Bases .base files with filters, formulas, properties, summaries, and table/card/list views. Use whenever the user works with Obsidian Bases, database-like note views, Base filters, formulas, lookup-style displays, or .base files.
---

# Obsidian Bases

Create valid YAML-based `.base` files. Read [REFERENCE.md](REFERENCE.md) for the full syntax and examples.

## Workflow

1. Read the existing Base and the frontmatter of representative source notes.
2. Define the source scope with the narrowest correct filter.
3. Add formulas only for requested computed values.
4. Configure views and display order.
5. Preserve unrelated existing views and properties.
6. Parse the result as YAML and verify referenced properties and formulas.
7. When Obsidian is available, open the Base and confirm it renders.

## Structure

```yaml
filters:
  and:
    - 'file.inFolder("Projects")'
    - 'status == "active"'

formulas:
  days_open: '(today() - file.ctime).days'

properties:
  formula.days_open:
    displayName: Days open

views:
  - type: table
    name: Active projects
    order:
      - file.name
      - status
      - formula.days_open
```

## Rules

- Quote filter and formula expressions.
- Use only supported view types documented in the local reference.
- Define every `formula.X` before using it.
- Keep one logical key under each recursive `and`, `or`, or `not` filter object.
- Do not claim successful rendering from YAML parsing alone.
