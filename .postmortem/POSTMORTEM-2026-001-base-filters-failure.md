# Postmortem Report: Obsidian Base Filters Configuration Failure

**Report ID**: POSTMORTEM-2026-001
**Date**: 2026-01-12
**Severity**: P0 - Critical
**Status**: Resolved
**Author**: Claude Code + User Review

## Executive Summary

A critical configuration error in Obsidian Base `filters` specification caused table views to display all files in the vault instead of the intended filtered subset. The filters were missing required string quotes, causing YAML parsing issues and filter expression failures.

**Impact**: Users seeing incorrect data in comparison tables, making the base feature unusable for its intended purpose.

**Root Cause**: Misunderstanding of Obsidian Base's filter expression syntax - filters must be YAML strings, not raw expressions.

---

## Timeline

| Date | Time | Event |
|------|------|-------|
| 2026-01-11 | Late evening | Initial implementation of comparison mode table.base |
| 2026-01-12 | Morning | User reported table.base displaying all files instead of filtered compare items |
| 2026-01-12 | 07:30 | Investigation revealed missing quotes in filter expressions |
| 2026-01-12 | 07:45 | Fix applied: added quotes to all filter conditions |
| 2026-01-12 | 08:00 | Verification confirmed filters working correctly |
| 2026-01-12 | 08:14 | Commit with fix pushed to GitHub (5eb3800) |

---

## Incident Details

### Severity Assessment

**Severity Level**: P0 - Critical

**Rationale**:
- Complete feature failure - table.base functionality completely broken
- Data integrity issue - showing wrong data to users
- User experience impact - comparison tables unusable
- No workaround available - manual filtering impossible

**Affected Components**:
- `.claude/skills/note-creator/` - note-creator orchestrator
- `obsidian-bases` skill integration
- Generated `table.base` files in comparison mode

### Root Cause Analysis

#### Direct Cause

The generated `table.base` file contained filters without YAML string quotes:

```yaml
# ❌ INCORRECT - Generated code
filters:
  and:
    - item_type == "tool"         # Missing outer quotes
    - file.hasTag("对比")          # Missing outer quotes
```

#### Underlying Causes

1. **Documentation Gap**
   - Obsidian Base documentation exists but filter syntax requirements not emphasized
   - No examples in immediate context showing quoted filter strings
   - Team unfamiliar with Obsidian Base expression syntax

2. **Missing Validation**
   - No automated validation of generated YAML syntax
   - No test cases for table.base filter configuration
   - Manual review process didn't catch the error

3. **Misunderstanding of YAML Parsing**
   - Assumed filters could be raw expressions
   - Didn't realize Obsidian Base requires string expressions to be parsed later
   - Lack of YAML knowledge about when quotes are required

### Contributing Factors

- **Time Pressure**: Focused on getting comparison mode working quickly
- **Complex Integration**: First implementation of comparison mode with obsidian-bases
- **Limited Testing**: Only tested that table.base opened, not that filtering worked
- **Documentation Not Internalized**: Had access to docs but didn't review filter syntax section

---

## Reproduction Steps

### How to Reproduce

1. Create a comparison article requiring table.base
2. Generate compare/*.md files with frontmatter including `item_type` and `tags`
3. Generate table.base with filters but without quotes:
   ```yaml
   filters:
     and:
       - item_type == "tool"
       - file.hasTag("对比")
   ```
4. Open table.base in Obsidian
5. **Expected**: Only compare/*.md files displayed
6. **Actual**: All files in vault displayed (or scoped directory scanned without filtering)

### Actual Behavior

When Obsidian Base parses the YAML:
- Without quotes, YAML tries to parse `item_type == "tool"` as a boolean expression or other type
- The parsed value is not a valid filter expression string
- Obsidian Base either ignores the filter or applies it incorrectly
- Result: No filtering occurs, all matching files are displayed

### Expected Behavior

With proper quotes:
```yaml
filters:
  and:
    - 'item_type == "tool"'      # String expression
    - 'file.hasTag("对比")'       # String expression
```

Obsidian Base:
- Parses each item as a string
- Passes string to filter expression engine
- Engine evaluates expression and applies filtering
- Result: Only files matching conditions displayed

---

## Impact Analysis

### Affected Artifacts

**Generated Files**:
- `outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/table.base`

**Affected Users**:
- Anyone using comparison mode articles
- Users relying on table.base for structured comparisons

### Data Integrity Impact

**Before Fix**:
- table.base showed all files in scoped directory
- User sees: file_name only (no custom fields from frontmatter)
- Comparison table unusable for intended purpose

**After Fix**:
- table.base shows only compare/*.md files
- User sees: all custom fields (name, 输入, 输出, 定位, 边界, 产物)
- Comparison table functional

**Business Impact**:
- Loss of trust in generated artifacts
- Time wasted debugging table.base configuration
- Feature essentially broken until fix applied

---

## Resolution

### Fix Applied

**Commit**: 5eb38000339e720c4b138f82f806c8e5623dea80

**File Modified**:
```
outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/table.base
```

**Change**:
```diff
 filters:
   and:
-    - item_type == "tool"
-    - file.hasTag("对比")
+    - 'item_type == "tool"'
+    - 'file.hasTag("对比")'
```

### Verification Steps

1. ✅ Open table.base in Obsidian
2. ✅ Verify only 2 files displayed (speckit.md, openspec.md)
3. ✅ Verify all custom columns show correct data
4. ✅ Verify filters working (item_type and tags checked)

### Documentation Updates

**Created Files**:
1. `.claude/skills/note-creator/rules/base.path.guide.md`
   - Added ⚠️ warning section about required quotes
   - Included correct/incorrect examples
   - Explained WHY quotes are required

2. `.claude/skills/note-creator/rules/table.base.fix.log.md`
   - Detailed fix log and root cause analysis
   - Common errors troubleshooting guide

---

## Lessons Learned

### Technical Lessons

1. **YAML String Quoting is Critical**
   - Filter expressions MUST be YAML strings
   - Always use quotes: `'expression'` or `"expression"`
   - Never rely on YAML's implicit type conversion

2. **Obsidian Base Filter Syntax**
   - Filters are string expressions evaluated at runtime
   - Not parsed as YAML boolean/logic expressions
   - Must be quoted to preserve string format until evaluation

3. **Testing Configuration Files**
   - Generated YAML must be validated
   - Opening in Obsidian is not sufficient testing
   - Must verify actual behavior, not just "no errors"

### Process Lessons

1. **Documentation Review**
   - Should review Obsidian Base docs before implementation
   - Filter syntax section should have been carefully read
   - Examples from docs should be followed exactly

2. **Incremental Testing**
   - Should test with simple case first
   - Verify filters work before adding complexity
   - Don't assume "it opened" means "it works"

3. **Code Review**
   - Generated configuration needs review like code
   - YAML syntax should be validated
   - Filter expressions should be checked against docs

---

## Prevention Measures

### Immediate Actions

1. ✅ **Add Comprehensive Documentation**
   - Created `base.path.guide.md` with detailed filter syntax
   - Added warning boxes emphasizing quotes requirement
   - Included common errors and troubleshooting

2. ✅ **Create Quick Checklist**
   - Added checklist in guide for post-generation validation
   - Includes: filters have quotes, paths are correct, frontmatter matches

3. ✅ **Document Correct Examples**
   - Show both correct and incorrect examples side-by-side
   - Explain WHY each format is correct/incorrect

### Long-term Actions

1. **Add Automated Tests**
   - [ ] Write test to validate table.base YAML syntax
   - [ ] Test that filters are properly quoted
   - [ ] Validate filter expressions against Obsidian Base schema

2. **Create Validation Script**
   - [ ] Python script to validate table.base before writing
   - [ ] Check that all filter conditions are strings
   - [ ] Verify basePath uses full relative paths

3. **Template Validation**
   - [ ] Add YAML validation to skill templates
   - [ ] Use YAML parser to check syntax during generation
   - [ ] Fail fast if generated YAML is invalid

4. **Improved Testing Protocol**
   - [ ] Test generated artifacts in Obsidian immediately
   - [ ] Verify filters work, don't just check "no errors"
   - [ ] Add to skill generation checklist

5. **Documentation Integration**
   - [ ] Link Obsidian Base docs directly in skill specs
   - [ ] Add required reading sections for skill developers
   - [ ] Create "common pitfalls" page

---

## Follow-up Actions

### Completed ✅

1. Fix applied to all affected table.base files
2. Documentation created with warnings and examples
3. Commit pushed to GitHub

### Pending ⏳

1. [ ] Add validation function to wechat_archiver.py
2. [ ] Create unit tests for table.base generation
3. [ ] Review other skills for similar YAML quoting issues
4. [ ] Add table.base validation to note-creator workflow
5. [ ] Update SKILL.md specs with filter syntax requirements

### Recommendations

1. **For Future Development**
   - Always quote filter expressions in YAML
   - Test generated configurations immediately
   - Validate YAML syntax before writing to disk

2. **For Code Reviews**
   - Check YAML files for proper quoting
   - Verify filter expressions are strings
   - Test generated artifacts in target application

3. **For Documentation**
   - Keep this postmortem as reference
   - Link from SKILL.md files
   - Review before any table.base modifications

---

## References

**Related Files**:
- `.claude/skills/note-creator/rules/base.path.guide.md`
- `.claude/skills/note-creator/rules/table.base.fix.log.md`
- `.claude/skills/obsidian-bases/SKILL.md`
- `outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/table.base`

**Related Commits**:
- 5eb3800 - feat: add wechat-archiver skill and improve base table generation

**External References**:
- Obsidian Base Documentation: `.claude/skills/obsidian-bases/SKILL.md`
- YAML Specification: https://yaml.org/spec/

---

**Report Status**: ✅ Complete
**Next Review**: After next table.base generation cycle
