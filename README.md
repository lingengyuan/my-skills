# My Skills - Claude Code Skills Framework

A framework for creating and managing Claude Code skills focused on content generation and Obsidian ecosystem integration.

## Overview

This project implements an **orchestrator pattern** where the `note-creator` skill acts as the main coordinator, delegating content generation tasks to specialized format-specific skills. The framework produces structured content artifacts including Markdown notes, visual diagrams, and database-like tables.

### Architecture

```
wechat-archiver (wrapper)
    ├── wechat2md          (WeChat article fetcher)
    └── note-creator       (orchestrator)
            ├── obsidian-markdown  (Markdown notes with YAML frontmatter)
            ├── json-canvas        (Visual diagrams and canvases)
            └── obsidian-bases     (Database-like table views)
```

## Skills

### note-creator (Orchestrator)

The main entry point for content generation. It:

1. Classifies user intent using a strict JSON schema
2. Selects destination folder from a predefined whitelist
3. Determines which artifact types to generate (markdown, canvas, base)
4. Delegates to specialized format skills
5. Writes all artifacts to disk following a strict output contract

**Usage:**
```bash
Skill(note-creator)
```

### obsidian-markdown

Generates Obsidian Flavored Markdown including:
- YAML frontmatter with properties
- Wikilinks and embeds
- Callouts and code blocks
- Tags and metadata

### json-canvas

Creates JSON Canvas files (`.canvas`) for visual diagrams including:
- Sequence diagrams
- Flowcharts
- Architecture diagrams
- Artifact relationship diagrams

### obsidian-bases

Generates Obsidian Base files (`.base`) with:
- Multiple view types (table, cards, list)
- Filters and formulas
- Property configurations
- Comparison tables

### wechat2md

Utility for converting WeChat articles to local Markdown:
- Downloads article content from `mp.weixin.qq.com`
- Downloads all images and converts to local references
- Outputs to `./outputs/` with organized image directories

**Usage:**
```bash
python3 .claude/skills/wechat2md/tools/wechat2md.py "<URL>"
```

### wechat-archiver

Wrapper skill that combines wechat2md and note-creator for automated WeChat article archiving:
- Fetches WeChat articles using wechat2md
- Automatically calls note-creator to generate structured notes
- Consolidates all artifacts (article.md, note.md, diagram.canvas, table.base) in a single directory
- Implements idempotency checks to avoid regenerating content
- Supports automatic detection of canvas/base generation based on article keywords

**Usage:**
```bash
/wechat-archiver article_url=https://mp.weixin.qq.com/s/xxxxx
```

**Features:**
- Unified asset directory with all files
- Content hashing for idempotency
- Smart artifact plan (canvas/base) based on content analysis
- Comparison mode for articles comparing tools/technologies

## Installation

### Prerequisites

- Python 3.8+
- Claude Code CLI

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd my-skills
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install beautifulsoup4
```

4. Configure permissions in `.claude/settings.local.json` (already configured)

## Output Structure

All generated content follows this structure (relative to current working directory):

```
outputs/<folder>/<title>/
  ├── note.md          (required)
  ├── diagram.canvas   (optional)
  ├── table.base       (optional)
  ├── meta.json        (required)
  └── compare/         (optional - for comparison tables)
```

**Note:** `outputs/` and `images/` directories contain generated artifacts and are **not tracked in git**. These are process outputs that should be regenerated as needed. The `.gitignore` file is configured to exclude these directories.

### Folder Whitelist

Content is organized into these folders:

- `00-Inbox` - Unclassified or temporary content
- `10-项目` - Project-specific notes and documentation
- `20-阅读笔记` - Reading notes, article summaries
- `30-方法论` - Methods, frameworks, comparisons, best practices
- `40-工具脚本` - Actual executable scripts and tools
- `50-运维排障` - Troubleshooting guides and debugging notes
- `60-数据与表` - Database schemas and data models
- `90-归档` - Deprecated or completed content

## Usage Examples

### Create a Note with Diagram

```bash
# Invoke the skill
Skill(note-creator)

# Provide a prompt like:
"Create a note explaining how the note-creator orchestrator works"
```

This generates:
- `note.md` - Detailed markdown with sections
- `diagram.canvas` - Visual sequence diagram
- `meta.json` - Metadata about the generated content

### Create a Comparison Table

```bash
Skill(note-creator)

# Prompt:
"Compare obsidian-markdown, json-canvas, and obsidian-bases skills"
```

This generates:
- `note.md` - Comparison overview
- `compare/*.md` - Individual item files
- `table.base` - Queryable comparison table
- `meta.json` - Metadata

### Convert WeChat Article

```bash
python3 .claude/skills/wechat2md/tools/wechat2md.py "https://mp.weixin.qq.com/s/xxxxx"
```

This downloads:
- Article content as Markdown in `./outputs/<title>/<title>.md`
- All images in `./images/<title>/001.jpg`, `002.png`, etc.

## Development

### Adding New Skills

1. Create skill directory under `.claude/skills/<skill-name>/`
2. Add `SKILL.md` specification following the established pattern
3. Define input/output contracts
4. Create templates in `templates/` subdirectory
5. Add examples in `examples/` subdirectory
6. Update `.claude/settings.local.json` with permissions

### File Structure

```
.claude/skills/
├── note-creator/              # Main orchestrator
│   ├── SKILL.md               # Main specification
│   ├── rules/                 # Classification and contracts
│   ├── templates/             # Prompt templates
│   └── examples/              # Usage examples
├── obsidian-markdown/         # Markdown generation
│   └── SKILL.md
├── json-canvas/               # Canvas/diagram generation
│   └── SKILL.md
├── obsidian-bases/            # Base/table generation
│   └── SKILL.md
├── wechat-archiver/           # WeChat article archiver wrapper
│   ├── SKILL.md
│   ├── rules/                 # Classification rules
│   ├── tools/
│   │   └── wechat_archiver.py
│   └── templates/
└── wechat2md/                 # WeChat article fetcher
    ├── SKILL.md
    └── tools/
        └── wechat2md.py
```

## Key Concepts

### Process Artifacts

Generated content in `outputs/` and `images/` directories are **process artifacts**:
- These are not tracked in git (see `.gitignore`)
- They should be regenerated as needed using the skills
- The framework focuses on the generation process, not the outputs
- Source of truth is the skill definitions and templates, not the generated files

This approach ensures:
- Git repository stays small and focused
- Skills remain reproducible
- Content can be regenerated with improvements to the skills
- No manual editing of generated artifacts (should be regenerated)

### Mandatory File Writing

All skills **MUST** write generated content to disk. Generating content without writing files is considered a FAILURE.

### Strict Classification Schema

The orchestrator uses a strict JSON schema for intent classification including:
- Title and folder selection
- Diagram type determination
- Artifact planning (md, canvas, base)
- Tag generation (3-8 tags)
- Property metadata

### Canvas Node Format

Text nodes in JSON Canvas must use:
- `"type": "text"`
- `"text": "<content>"`
- **NEVER** `"label"` (reserved for groups only)

### Comparison Mode

For comparison tables:
- Set `base_mode: "comparison"` in classification
- Create individual `.md` files in `compare/` subdirectory
- Scope Base sources to `compare/` directory only

## Configuration

Skills are configured in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Skill(note-creator)",
      "Skill(json-canvas)",
      "Bash(mkdir:*)",
      "Bash(echo:*)",
      "Bash(python3:*)",
      "Bash(cat:*)"
    ]
  }
}
```

## Dependencies

- **Python 3.8+**
- **beautifulsoup4** - For wechat2md HTML parsing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Hugh Lin

## Contributing

Contributions are welcome! Please follow the established patterns when adding new skills or modifying existing ones.
