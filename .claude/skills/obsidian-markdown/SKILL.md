---
name: obsidian-markdown
description: Create, edit, and validate Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, tags, block references, and Obsidian-specific syntax. Use for Obsidian notes or whenever .md files require vault-aware links and metadata.
---

# Obsidian Markdown

Use standard Markdown normally and apply Obsidian-specific syntax only where useful. Read [REFERENCE.md](REFERENCE.md) for detailed syntax.

## Workflow

1. Read the target note and nearby notes before editing.
2. Preserve the existing frontmatter style and link convention.
3. Use wikilinks for notes inside the vault and standard Markdown links for external URLs.
4. Use embeds only when inline content is actually needed.
5. Add callouts sparingly for information that benefits from emphasis.
6. Validate frontmatter, link targets when discoverable, and code fences.
7. Re-read the final note.

## Core syntax

```markdown
[[Note Name]]
[[Note Name#Heading|Display text]]
![[image.png|300]]

> [!warning] Title
> Content
```

Frontmatter must be the first content in the file:

```yaml
---
title: Example
tags:
  - project
aliases:
  - Alternate name
---
```

## Rules

- Use spaces, not tabs, in YAML.
- Do not duplicate properties already present under another spelling.
- Do not convert ordinary Markdown links to wikilinks when the target is external.
- Preserve user prose and unrelated formatting during surgical edits.
