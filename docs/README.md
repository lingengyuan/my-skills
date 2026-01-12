# Documentation Archive

This directory contains historical documentation, audit reports, and reference materials for the my-skills project.

## Directory Structure

```
docs/
├── README.md                           # This file
├── SKILL.md                            # WeChat Article Archiver Skills project documentation
├── WECHAT2MD_OPTIMIZATION.md         # v2 optimization summary (technical decisions)
├── SESSION_SUMMARY_2026-01-12.md       # Daily session summary (2026-01-12)
└── audit/                              # Audit and review reports
    └── 2026-01-12-skills-audit.md      # Skills comprehensive audit
```

## Quick Reference

### For Understanding WeChat Article Archiving

- **[SKILL.md](./SKILL.md)** - Complete guide to wechat2md, wechat-archiver, note-creator skills
  - Quick start for all three skills
  - v2 improvements comparison table
  - Technical details (asset_id, idempotency, directory structure)
  - Troubleshooting guide

### For Understanding v2 Optimization

- **[WECHAT2MD_OPTIMIZATION.md](./WECHAT2MD_OPTIMIZATION.md)** - Complete v2 optimization record
  - Problem analysis (4 major issues with v1)
  - Improvement solutions (markdownify, asset_id, unified structure)
  - File structure comparison (v1 vs v2)
  - Upgrade guide and testing checklist
  - Future improvements roadmap

### For Daily Progress Tracking

- **[SESSION_SUMMARY_2026-01-12.md](./SESSION_SUMMARY_2026-01-12.md)** - Session summary and achievements
  - Articles archived (1 article, 20 images)
  - Bugs fixed (P1: image path error)
  - Project cleanup (6 files deleted)
  - Documentation organized
  - Key learnings and next steps

### For Skills Development

- **[audit/2026-01-12-skills-audit.md](./audit/2026-01-12-skills-audit.md)** - Skills audit report
  - 7 critical issues identified (since resolved)
  - 12 optimization opportunities
  - Gap analysis by skill (note-creator, wechat-archiver, obsidian-markdown, etc.)
  - Implementation checklist (Phase 1-3)
  - ⚠️ **Historical Note**: Most issues have been fixed, preserved for reference

---

## Document Descriptions

### SKILL.md

**Type**: Project-level documentation
**Purpose**: Complete guide for WeChat Article Archiver Skills collection
**Content**:
- Overview of three core skills (wechat2md, wechat-archiver, note-creator)
- Usage methods (CLI, Python API, Claude Skill)
- v2 improvements (markdownify 95% vs 70%, unified structure, asset_id)
- Output contract and directory structure
- Troubleshooting guide
- Related documentation links

**When to Reference**:
- Learning how to use the WeChat article archiving system
- Understanding v2 improvements and migration path
- Troubleshooting common issues

---

### WECHAT2MD_OPTIMIZATION.md

**Type**: Technical decision document
**Purpose**: Complete record of v1 → v2 optimization process
**Content**:
- Problem summary (4 major issues)
- Root cause analysis for each problem
- Solution design (markdownify integration, asset_id, unified structure)
- Code comparison (v1 600+ lines vs v2 20 lines)
- File structure evolution
- Upgrade guide with testing checklist
- Common problems and solutions
- Future improvement roadmap

**When to Reference**:
- Understanding why v2 made certain design decisions
- Migrating from v1 to v2
- Learning from optimization process
- Understanding technical trade-offs

---

### SESSION_SUMMARY_2026-01-12.md

**Type**: Session log / Daily summary
**Purpose**: Record of work completed in 2026-01-12 session
**Content**:
- Article archiving (1 article, 20 images, 4 artifacts generated)
- Bug fixes (P1: image path error)
- Project cleanup (6 obsolete files deleted)
- Documentation updates (3 files updated)
- Statistics and metrics
- Key learnings
- Next steps

**When to Reference**:
- Reviewing what was accomplished in this session
- Understanding context for postmortem reports
- Tracking project progress over time

---

## How to Use This Archive

### For New Users

1. **Start with**: `../README.md` (quick start)
2. **Then read**: `SKILL.md` (complete guide to WeChat archiving)
3. **Reference**: `WECHAT2MD_OPTIMIZATION.md` (if interested in v2 details)

### For Developers

1. **Technical Decisions**: See `WECHAT2MD_OPTIMIZATION.md` for v2 design rationale
2. **Project Evolution**: See `audit/2026-01-12-skills-audit.md` for skills improvement history
3. **Session Progress**: See `SESSION_SUMMARY_2026-01-12.md` for what was done

### For Troubleshooting

1. **Current Issues**: Check `../postmortem/` for active incident reports
2. **Known Issues**: Check `WECHAT2MD_OPTIMIZATION.md` troubleshooting section
3. **Common Problems**: Check `SKILL.md` common problems section

---

## Related Documentation

### In Root Directory

- **README.md** - Quick start guide (active)
- **CLAUDE.md** - Project detailed guide (active)
- **LICENSE** - MIT License

### In Skills Directories

- **.claude/skills/wechat2md/V2_UPGRADE.md** - v2 upgrade guide
- **.claude/skills/wechat-archiver/BUGFIXES.md** - Bug fix log
- **.claude/skills/note-creator/** - Rules, templates, examples

### In Postmortem Directory

- **../postmortem/** - Incident reports (active reference, not archived)
- **POSTMORTEM-2026-006** - Latest: Image path error fix

---

## Archive Policy

### What Goes Here

**Project-level documentation** (moved from root when mature):
- `SKILL.md` - WeChat Article Archiver Skills collection guide
- `WECHAT2MD_OPTIMIZATION.md` - Major version optimization records
- `SESSION_SUMMARY_*.md` - Daily/session logs

**Audit and review reports**:
- `audit/YYYY-MM-DD-*.md` - Skills audits, code reviews
- Historical project assessments

### What Stays in Root

**Active project files**:
- `README.md` - Quick start (always current)
- `CLAUDE.md` - Project guide (always current)
- `LICENSE` - Legal (permanent)

**NOT here**:
- Individual skill SKILL.md files (in `.claude/skills/*/SKILL.md`)
- Postmortem reports (in `../postmortem/`)
- Active work files

---

## Maintenance

### Adding Session Summaries

After each work session:

```bash
# Create session summary
cp SESSION_SUMMARY_TEMPLATE.md docs/SESSION_SUMMARY_YYYY-MM-DD.md
# Edit with actual work done
# Update this README if needed
```

### Updating Documentation

When moving documentation from root to docs:

1. **Add entry** to this README (Quick Reference section)
2. **Update links** in related files
3. **Add summary** with purpose, content, when to reference
4. **Update** Last Updated and Total Documents counts

---

## Document Index

| Document | Type | Purpose | Status |
|----------|------|---------|--------|
| SKILL.md | Project Guide | WeChat Article Archiver complete guide | ✅ v2 (2026-01-12) |
| WECHAT2MD_OPTIMIZATION.md | Technical Record | v1 → v2 optimization details | ✅ v2 (2026-01-12) |
| SESSION_SUMMARY_2026-01-12.md | Session Log | Daily work summary | ✅ Complete |
| audit/2026-01-12-skills-audit.md | Audit Report | Skills standards audit | ⚠️ Historical (most issues fixed) |

---

**Last Updated**: 2026-01-12
**Total Documents**: 4
**Archive Status**: Active, Organized
