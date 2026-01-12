# Postmortem Reports Index

This directory contains detailed postmortem reports for incidents and bugs discovered during the development of the my-skills project. Each report provides a comprehensive analysis of what went wrong, why it happened, how it was fixed, and what we learned.

## Report Summary

| Report ID | Title | Severity | Status | Date |
|-----------|-------|----------|--------|------|
| POSTMORTEM-2026-001 | [Obsidian Base Filters Configuration Failure](./POSTMORTEM-2026-001-base-filters-failure.md) | P0 - Critical | ✅ Resolved | 2026-01-12 |
| POSTMORTEM-2026-002 | [Obsidian Base basePath Path Resolution Error](./POSTMORTEM-2026-002-basepath-resolution-error.md) | P0 - Critical | ✅ Resolved | 2026-01-12 |
| POSTMORTEM-2026-003 | [wechat2md Windows Subprocess Encoding Error](./POSTMORTEM-2026-003-wechat2md-encoding.md) | P1 - High | ✅ Resolved | 2026-01-12 |
| POSTMORTEM-2026-004 | [Overly Broad Base Auto-Detection Rules](./POSTMORTEM-2026-004-overbroad-base-detection.md) | P2 - Medium | ✅ Resolved | 2026-01-12 |
| POSTMORTEM-2026-005 | [Duplicate Article Ingestion Due to Slug Collision](./POSTMORTEM-2026-005-duplicate-ingestion.md) | P2 - Medium | ⏳ Partially Resolved | 2026-01-12 |
| POSTMORTEM-2026-006 | [wechat2md v2 Image Path Error](./POSTMORTEM-2026-006-image-path-error.md) | P1 - High | ✅ Resolved | 2026-01-12 |
| POSTMORTEM-2026-006 | [wechat2md v2 Image Path Error](./POSTMORTEM-2026-006-image-path-error.md) | P1 - High | ✅ Resolved | 2026-01-12 |

## Severity Levels

- **P0 - Critical**: Complete feature failure, data integrity issues, no workaround available
- **P1 - High**: Major functionality broken on specific platforms, significant user impact
- **P2 - Medium**: Feature works but has UX issues, wasted resources, confusion
- **P3 - Low**: Minor issues, cosmetic problems, documentation gaps

## Quick Links

### Most Critical (Read First)
1. **[POSTMORTEM-2026-001](./POSTMORTEM-2026-001-base-filters-failure.md)** - Table base filters not working
2. **[POSTMORTEM-2026-002](./POSTMORTEM-2026-002-basepath-resolution-error.md)** - Wrong directory scanning

### Platform-Specific Issues
- **Windows**: [POSTMORTEM-2026-003](./POSTMORTEM-2026-003-wechat2md-encoding.md) - Encoding errors

### Design Issues
- **Auto-Detection**: [POSTMORTEM-2026-004](./POSTMORTEM-2026-004-overbroad-base-detection.md) - False positives
- **Idempotency**: [POSTMORTEM-2026-005](./POSTMORTEM-2026-005-duplicate-ingestion.md) - Duplicate content

## Common Themes

### 1. YAML Configuration Issues (Reports 001, 002)
- **Problem**: Obsidian Base configuration has strict syntax requirements
- **Root Cause**: Insufficient understanding of Obsidian Base behavior
- **Fix**: Detailed documentation, examples, and validation guides
- **Prevention**: Always test generated YAML in Obsidian, validate syntax

### 2. Platform-Specific Encoding (Report 003)
- **Problem**: Windows uses GBK encoding by default for Chinese
- **Root Cause**: subprocess.run() without explicit encoding
- **Fix**: Always specify `encoding='utf-8'`
- **Prevention**: Cross-platform testing, explicit encoding in all I/O

### 3. False Positive Detection (Report 004)
- **Problem**: Overly broad keywords trigger base generation inappropriately
- **Root Cause**: Insufficient testing against real data
- **Fix**: Refined keywords, removed common words
- **Prevention**: Test with real corpus, measure precision/recall

### 4. Idempotency Failures (Report 005)
- **Problem**: Same content creates multiple directories on different days
- **Root Cause**: Date prefix in slug causes variations
- **Fix**: Documented workaround (--simple-slug), proper fix pending
- **Prevention**: Design for uniqueness, check by content hash

## Statistics

### Impact Summary
- **Total Issues**: 5
- **Critical (P0)**: 2 (40%) - Both fixed
- **High (P1)**: 1 (20%) - Fixed
- **Medium (P2)**: 2 (40%) - One fixed, one workaround
- **Low (P3)**: 0 (0%)

### Resolution Status
- **Fully Resolved**: 4 (80%)
- **Partially Resolved**: 1 (20%)
- **Pending**: 0 (0%)

### Commit References
- **Fix Commit**: 5eb3800 (all resolved issues)
- **GitHub**: https://github.com/lingengyuan/my-skills/commit/5eb3800

## Key Learnings

### Technical Lessons
1. **Always Test Generated Artifacts**: Opening in Obsidian is not enough testing
2. **Cross-Platform Matters**: Windows encoding differences are real
3. **YAML Syntax is Strict**: Filters and paths require specific formats
4. **Keyword Selection Needs Data**: Can't rely on intuition for auto-detection

### Process Lessons
1. **Document Decisions**: Write down why we chose certain approaches
2. **Test Real Scenarios**: Test with real data, not just happy path
3. **User Feedback is Gold**: Users notice issues immediately, listen to them
4. **Postmortems are Valuable**: Document incidents to prevent recurrence

### Prevention Strategies
1. **Create Validation Guides**: Documentation with examples and anti-patterns
2. **Add Automated Tests**: Catch regressions before deployment
3. **Cross-Platform Testing**: Test on Windows, Linux, macOS
4. **Incremental Rollout**: Test with small group before general use

## Using These Reports

### For Developers
1. Read relevant postmortems before implementing similar features
2. Check "Prevention Measures" sections for guidelines
3. Review "Lessons Learned" to avoid same mistakes
4. Use references to understand related documentation

### For Code Reviewers
1. Check if changes address issues mentioned in postmortems
2. Verify prevention measures are implemented
3. Look for patterns that might cause similar issues
4. Ask: "Did we learn from previous postmortems?"

### For Users
1. Understand known issues and workarounds
2. Learn why certain features behave the way they do
3. See what we're doing to prevent future issues
4. Provide feedback based on real-world usage

## Related Documentation

- **Bug Fixes**: `.claude/skills/wechat-archiver/BUGFIXES.md`
- **Table Base Guide**: `.claude/skills/note-creator/rules/base.path.guide.md`
- **Fix Log**: `.claude/skills/note-creator/rules/table.base.fix.log.md`
- **Classification Rules**: `.claude/skills/wechat-archiver/rules/classification.md`

## Maintenance

### Updating Reports
- If new information discovered, update relevant postmortem
- Link related postmortems for cross-reference
- Update statistics as new issues discovered
- Archive old reports to historical/ subdirectory

### Creating New Reports
- Use existing reports as templates
- Follow standard structure: Summary → Timeline → Analysis → Resolution → Lessons
- Be specific and detailed
- Include code examples and reproduction steps
- Focus on learning and prevention

### Review Schedule
- **Monthly**: Review P0/P1 issues for recurrence
- **Quarterly**: Review all postmortems for patterns
- **Annually**: Update prevention strategies based on new learnings

## Acknowledgments

These postmortems were created through collaborative investigation between:
- **Hugh Lin** - Project owner, user feedback, testing
- **Claude Code (Sonnet 4.5)** - Technical investigation, documentation, fixes

The open and honest documentation of these incidents is essential for continuous improvement of the my-skills framework.

---

**Last Updated**: 2026-01-12
**Total Reports**: 5
**Overall Status**: Healthy, Learning, Improving
