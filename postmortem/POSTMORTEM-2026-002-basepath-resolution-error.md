# Postmortem Report: Obsidian Base basePath Path Resolution Error

**Report ID**: POSTMORTEM-2026-002
**Date**: 2026-01-12
**Severity**: P0 - Critical
**Status**: Resolved
**Author**: Claude Code + User Review

## Executive Summary

A critical path configuration error in Obsidian Base `basePath` caused table views to scan the wrong directory, potentially including unintended files from across the entire vault. The relative path was interpreted from vault root instead of from the table.base file location.

**Impact**: Data leakage - showing files from unintended directories, privacy concern, incorrect data in comparison tables.

**Root Cause**: Misunderstanding of Obsidian Base's `basePath` behavior - it's relative to vault root, not relative to the .base file location.

---

## Timeline

| Date | Time | Event |
|------|------|-------|
| 2026-01-11 | Late evening | Initial implementation of comparison mode table.base |
| 2026-01-12 | Morning | User reported table.base showing files from entire outputs/ directory |
| 2026-01-12 | 07:20 | Investigation revealed basePath path resolution issue |
| 2026-01-12 | 07:40 | Fix applied: use full relative path from vault root |
| 2026-01-12 | 07:45 | Verification confirmed only compare/*.md files shown |
| 2026-01-12 | 08:14 | Commit with fix pushed to GitHub (5eb3800) |

---

## Incident Details

### Severity Assessment

**Severity Level**: P0 - Critical

**Rationale**:
- Data leakage risk - showing files from unintended locations
- Privacy concern - potential to expose unrelated content
- Feature completely broken - not showing intended files
- No validation - silently showing wrong data

**Affected Components**:
- All generated table.base files in comparison mode
- Any skill using obsidian-bases with non-root basePath

### Root Cause Analysis

#### Direct Cause

The generated `table.base` file used relative basePath without accounting for Obsidian Base's resolution behavior:

```yaml
# ❌ INCORRECT - Generated code
sources:
  - type: local
    basePath: compare        # Relative to .base file? NO!
    include:
      - "*.md"
```

**Expected Behavior**:
- Developer expected: `basePath: compare` would resolve to `./compare/` relative to table.base location
- Actual behavior: `basePath: compare` resolves to `vault_root/compare/`

#### Underlying Causes

1. **Incorrect Mental Model**
   - Assumed basePath worked like relative paths in most systems
   - Didn't realize Obsidian Base uses vault root as base
   - No experience with Obsidian Base path resolution

2. **Documentation Not Consulted**
   - Obsidian Base documentation exists but wasn't reviewed
   - No examples showing basePath usage in subdirectories
   - Assumed behavior based on intuition rather than docs

3. **Lack of Path Validation**
   - No validation that basePath points to intended location
   - No checking that scoped files are actually the right ones
   - Manual review in Obsidian didn't catch the issue immediately

### Contributing Factors

- **Complex Directory Structure**: Deep nesting made path assumptions harder to verify
- **No Error Messages**: Obsidian Base silently scans wrong directory
- **Visual Confusion**: Table showed data, so initially appeared to work
- **Time Pressure**: Focused on getting feature working, didn't validate thoroughly

---

## Reproduction Steps

### How to Reproduce

1. Create article in nested directory: `outputs/20-阅读笔记/20260112-article-title/`
2. Generate compare subdirectory: `outputs/20-阅读笔记/20260112-article-title/compare/`
3. Generate table.base with relative basePath:
   ```yaml
   sources:
     - type: local
       basePath: compare
       include:
         - "*.md"
   ```
4. Place table.base in article directory
5. Open table.base in Obsidian
6. **Expected**: Shows files from `outputs/20-阅读笔记/20260112-article-title/compare/`
7. **Actual**: Shows files from `vault_root/compare/` (if exists) or scans unintended location

### Actual Behavior

Obsidian Base path resolution:
1. Parses `basePath: compare`
2. Resolves from vault root, not from .base file location
3. Looks for `vault_root/compare/` directory
4. If that directory doesn't exist, may show nothing or scan other location
5. If other directories named `compare/` exist in vault, shows those files
6. Result: Shows wrong files or no files, never the intended ones

### Expected Behavior

With correct full relative path:
```yaml
sources:
  - type: local
    basePath: outputs/20-阅读笔记/20260112-article-title/compare
    include:
      - "*.md"
```

Obsidian Base path resolution:
1. Parses `basePath: outputs/20-阅读笔记/20260112-article-title/compare`
2. Resolves from vault root: `vault_root/outputs/20-阅读笔记/20260112-article-title/compare`
3. Shows only files from that specific directory
4. Result: Correct files displayed

---

## Impact Analysis

### Affected Artifacts

**Generated Files**:
- All table.base files using relative basePath
- Specifically: `outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit.../table.base`

**Affected Scope**:
- Any comparison mode articles
- Potentially any table.base in subdirectories

### Data Integrity Impact

**User Report (Paraphrased)**:
> "table.base展示了很多不属于自己这个文件夹的记录"

**Before Fix**:
- table.base scanned from wrong base directory
- Showed files from other parts of vault (or nothing)
- User confused why wrong data appearing
- Privacy concern: showing unintended content

**After Fix**:
- table.base scans correct compare/ subdirectory
- Shows only intended comparison item files
- Data isolated to specific article context
- Privacy maintained: only scoped files visible

### Business Impact

- **User Trust**: Users can't trust generated table.base files
- **Feature Usability**: Comparison tables unusable with wrong data
- **Debugging Time**: Significant time spent investigating path issue
- **Support Burden**: Would generate many support requests

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
 sources:
   - type: local
-    basePath: compare
+    basePath: outputs/20-阅读笔记/20260112-OpenSpec vs SpecKit同样是 SDD它们解决的其实不是一类问题-609535/compare
     include:
       - "*.md"
```

### Implementation Details

**Path Calculation Logic**:
```python
import os
from pathlib import Path

# Get current working directory
cwd = os.getcwd()  # e.g., /f/Project/my-skills

# Build asset directory
asset_dir = Path(cwd) / "outputs" / folder / title
compare_dir = asset_dir / "compare"

# Calculate relative path from vault root
relative_path = compare_dir.relative_to(cwd)
# Result: outputs/20-阅读笔记/20260112-OpenSpec.../compare
```

### Verification Steps

1. ✅ Update table.base with full relative path
2. ✅ Open in Obsidian
3. ✅ Verify only 2 files shown (speckit.md, openspec.md)
4. ✅ Verify no files from other directories appear
5. ✅ Verify data.path also uses full path

---

## Lessons Learned

### Technical Lessons

1. **Obsidian Base Path Resolution**
   - `basePath` is relative to vault root, NOT .base file location
   - Always use full relative path from vault root
   - Never assume relative path behavior without checking docs

2. **Path Construction in Skills**
   - Must calculate paths relative to CWD at generation time
   - Use `Path.relative_to()` to get correct relative paths
   - Store full relative paths, not short relative paths

3. **YAML Path Configuration**
   - Paths in YAML files are not context-aware
   - No automatic path resolution relative to file location
   - Must be explicit and absolute from reference point

### Process Lessons

1. **Documentation is Essential**
   - Should have read Obsidian Base docs before implementing
   - Path resolution behavior would have been clear from docs
   - Don't rely on intuition for path behavior

2. **Test with Real Data**
   - Should test with multiple directories to verify scoping
   - Single test case missed the path resolution issue
   - Need to verify what files are actually shown, not just "it works"

3. **User Feedback is Critical**
   - User noticed immediately: "showing wrong files"
   - Should involve users earlier in testing process
   - Visual inspection revealed issue quickly

---

## Prevention Measures

### Immediate Actions

1. ✅ **Create Comprehensive Guide**
   - Created `base.path.guide.md` with detailed path configuration rules
   - Explained Obsidian Base path resolution behavior
   - Added examples of correct/incorrect path configurations

2. ✅ **Document Path Calculation**
   - Included Python code for correct path calculation
   - Showed how to use `Path.relative_to()` properly
   - Added step-by-step algorithm

3. ✅ **Add Warnings**
   - Prominently documented basePath must use full relative path
   - Added "⚠️ Most Important" warnings in guide
   - Included common pitfalls section

### Long-term Actions

1. **Add Path Validation Function**
   ```python
   def validate_base_path(table_base_path: Path, intended_scope_dir: Path) -> bool:
       """Validate that table.base basePath points to intended directory."""
       # Parse YAML
       # Check basePath matches intended scope
       # Return True if correct, False otherwise
   ```

2. **Create Path Helper Module**
   - Centralize path calculation logic
   - Provide utilities for relative path generation
   - Include validation functions

3. **Add Integration Tests**
   - Test table.base generation in various directory depths
   - Verify correct files are shown in Obsidian
   - Test with multiple compare/ directories in vault

4. **Update Skill Templates**
   - Include path calculation examples in templates
   - Add comments explaining path resolution
   - Provide code snippets for correct implementation

5. **Create Validation Checklist**
   - [ ] basePath uses full relative path from vault root
   - [ ] data.path uses full relative path from vault root
   - [ ] Tested in Obsidian with real data
   - [ ] Verified only intended files shown
   - [ ] Checked no files from other directories appear

---

## Follow-up Actions

### Completed ✅

1. Fix applied to affected table.base files
2. Documentation created with path calculation guide
3. Commit pushed to GitHub

### Pending ⏳

1. [ ] Create path validation utility function
2. [ ] Add basePath validation to wechat_archiver.py
3. [ ] Review all other skills using obsidian-bases
4. [ ] Add integration tests for table.base generation
5. [ ] Update note-creator SKILL.md with path requirements

### Recommendations

1. **For Future Development**
   - Always use full relative paths from vault root
   - Calculate paths at generation time using CWD
   - Never assume relative path behavior
   - Test path scoping with multiple directories

2. **For Code Review**
   - Check basePath uses full path, not short relative
   - Verify paths are calculated from vault root
   - Test in actual Obsidian installation
   - Verify file scoping with real data

3. **For Documentation**
   - Keep this postmortem as reference
   - Link from skill development guides
   - Review before any table.base modifications
   - Include in onboarding for new developers

---

## Technical Deep Dive

### Obsidian Base Path Resolution

**Reference Point**: Vault Root Directory
- The root of your Obsidian vault
- Where `.obsidian/` folder is located
- Base for all relative paths in Obsidian Base

**Path Resolution Rules**:

```yaml
# If vault root is /f/Project/my-skills/
# And .base file is at /f/Project/my-skills/outputs/20-阅读笔记/20260112-article/table.base

basePath: compare                    # Resolves to: /f/Project/my-skills/compare
basePath: outputs                    # Resolves to: /f/Project/my-skills/outputs
basePath: outputs/20-阅读笔记        # Resolves to: /f/Project/my-skills/outputs/20-阅读笔记
basePath: outputs/20-阅读笔记/20260112-article/compare  # Full correct path
```

### Common Pitfalls

❌ **Wrong**: Assuming relative to .base file
```yaml
basePath: compare  # Looks in vault_root/compare/, not ./compare/
```

❌ **Wrong**: Using absolute paths
```yaml
basePath: /f/Project/my-skills/outputs/.../compare  # Won't work across systems
```

✅ **Correct**: Full relative from vault root
```yaml
basePath: outputs/20-阅读笔记/20260112-article/compare
```

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
- Python pathlib Documentation: https://docs.python.org/3/library/pathlib.html

---

**Report Status**: ✅ Complete
**Next Review**: After next table.base generation in different directory depth
