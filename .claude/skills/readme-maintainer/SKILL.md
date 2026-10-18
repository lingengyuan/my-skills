---
name: readme-maintainer
description: Maintain, update, and rewrite concise, publication-ready repository README files grounded in codebase facts. Use when updating README.md, refreshing installation and usage guides, verifying CLI commands, or aligning bilingual documentation.
---

# README Maintainer Skill

Generate and maintain clear, verified README files directly from repository source code, build manifests, and runtime configuration. Standard Markdown is assumed knowledge.

## Workflow

1. **Locate README and files**: Identify repository root and existing `README.md`. Read the current content.
2. **Collect repository facts**: Inspect `package.json`, `Cargo.toml`, `pyproject.toml`, CLI help outputs, and configuration files. For repository-wide updates, run:
   ```bash
   bash "<skill-dir>/scripts/collect_repo_facts.sh" "<repo-path>"
   ```
3. **Verify claims against code**: Verify installation steps, prerequisites, environment variables, and CLI commands against actual repository source code. Delete stale claims and unverified statements.
4. **Structure the document**:
   - **Project Overview**: One concise sentence describing what the project does.
   - **Prerequisites & Installation**: Exact runtime versions, package managers, and setup commands.
   - **Quick Start / Basic Usage**: Minimal runnable command or code example with realistic input and output.
   - **Configuration / Key Options**: Essential configuration table or common operations.
   - **Documentation Links**: Link detailed architectural guides, API references, and development procedures to existing files instead of duplicating them.
5. **Apply publication pass**:
   - Delete meta-discourse, author reflections, and review commentary.
   - State product features and constraints directly in active voice.
   - Define each technical fact in one authoritative place.
   - Keep only sections the reader needs. A README is an entry point, not an exhaustive encyclopedia.
6. **Align bilingual documentation (if applicable)**:
   - Match the existing language convention.
   - If bilingual READMEs exist, ensure semantic parity across sections. Run:
     ```bash
     bash "<skill-dir>/scripts/check_bilingual_readme.sh" README.md
     ```
7. **Verify & report**: Test links, verify command syntax, and report material changes outside the README.

## Guidelines

- **Grounding**: Never invent compatibility guarantees, benchmarks, test coverage stats, or feature lists.
- **Single source of truth**: Link to specialized documentation (architecture, full API, contributing guides) rather than duplicating large sections.
- **Brevity with completeness**: Delete conversational filler, but keep essential setup commands, parameter definitions, and failure recovery notes.

## Verification Checklist

Before completing the task, verify:

1. All installation and run commands match repository build tools.
2. Code examples and CLI flags reflect current implementations.
3. All internal links and relative file paths resolve correctly.
4. If bilingual, both language sections cover identical concepts without drift.
5. Output contains no internal editing chatter or temporary task notes.
