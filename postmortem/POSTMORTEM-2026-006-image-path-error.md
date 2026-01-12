# Postmortem Report: wechat2md v2 Image Path Error

**Report ID**: POSTMORTEM-2026-006
**Date**: 2026-01-12
**Severity**: P1 - High
**Status**: Resolved
**Author**: Claude Code

## Executive Summary

A critical path error in `wechat2md_v2.py` caused generated article Markdown files to reference images with incorrect relative paths `../images/images/xxx.jpg` instead of the correct `images/xxx.jpg`. This was caused by v1 legacy code that didn't account for v2's unified directory structure.

**Impact**: All images in generated articles were broken, making articles unreadable in Markdown viewers and Obsidian.

**Root Cause**: Code used v1's path logic `image_prefix = f"../images/{images_dir.name}/"` which resulted in `../images/images/` when `images_dir.name` was `"images"`.

---

## Timeline

| Date | Time | Event |
|------|------|-------|
| 2026-01-11 | Initial release | wechat2md_v2.py created with unified directory structure |
| 2026-01-12 | 20:38 | First article successfully ingested (20 images) |
| 2026-01-12 | 21:00 | User noticed image links broken in Obsidian |
| 2026-01-12 | 21:05 | Investigation revealed path pattern: `../images/images/001.jpg` |
| 2026-01-12 | 21:10 | Root cause identified: line 209 in wechat2md_v2.py |
| 2026-01-12 | 21:15 | Fix applied: changed `image_prefix` to `"images/"` |
| 2026-01-12 | 21:20 | Fixed existing article.md with `sed` |
| 2026-01-12 | 21:25 | Verified all 20 images now correctly referenced |
| 2026-01-12 | 21:30 | Updated V2_UPGRADE.md with fix record |

---

## Incident Details

### Severity Assessment

**Severity Level**: P1 - High

**Rationale**:
- Major functionality broken - images don't display in articles
- Significant user impact - core feature of article archiving
- Data integrity issue - articles incomplete without images
- Manual workaround available but tedious (find/replace in each article)

**Affected Components**:
- `.claude/skills/wechat2md/tools/wechat2md_v2.py` (line 209)
- All generated `article.md` files with images
- Output directory: `outputs/20-阅读笔记/认知重建：Speckit 用了三个月，我放弃了——走出工具很强但用不好的困境/`

### Root Cause Analysis

#### Direct Cause

The `download_images()` function in `wechat2md_v2.py` used incorrect path logic:

```python
# ❌ INCORRECT - Line 209 (before fix)
images_dir = output_dir / "images"  # → outputs/.../slug/images
images_dir.name  # → "images"
image_prefix = f"../images/{images_dir.name}/"  # → "../images/images/"
```

When setting `img['src']` in the HTML:
```python
img['src'] = f"{image_prefix}{filename}"  # → "../images/images/001.jpg"
```

#### Underlying Causes

1. **v1 Legacy Code**
   - v1 structure: `outputs/<title>/<title>.md` + `images/<title>/` (separate directories)
   - v1 needed `../images/<title>/` to reference images from outputs/
   - v2 changed to unified structure but didn't update path calculation

2. **Missing Test Coverage**
   - No automated test for image path generation
   - Manual testing only verified images downloaded, not that Markdown references worked
   - Didn't test opening generated article.md in Obsidian or Markdown viewer

3. **Incomplete Migration Review**
   - V2_UPGRADE.md documented directory structure changes
   - But code review missed the image_prefix calculation
   - Assumed `images_dir.name` was the title, not "images"

### Contributing Factors

- **Complex Path Logic**: Using f-string with dynamic `images_dir.name` made error less obvious
- **Lack of Validation**: No assertion or check that generated paths exist
- **Testing Gap**: Only verified download success, not path correctness
- **Documentation-Code Mismatch**: V2_UPGRADE.md described correct structure but code didn't match

---

## Reproduction Steps

### How to Reproduce

1. Run wechat2md_v2.py on any article with images:
   ```bash
   python .claude/skills/wechat2md/tools/wechat2md_v2.py "https://mp.weixin.qq.com/s/..."
   ```

2. Open generated `article.md` in text editor

3. Observe image links:
   ```markdown
   ![Image 1](../images/images/001.jpg)  # ❌ Wrong
   ```

4. Expected:
   ```markdown
   ![Image 1](images/001.jpg)  # ✅ Correct
   ```

### Failure Mode

When rendering in Obsidian or Markdown viewer:
```
images/
└── images/
    └── 001.jpg  # File actually here
```

But Markdown looks for:
```
../../ (from outputs/20-阅读笔记/slug/article.md)
  └── images/
      └── images/
          └── 001.jpg  # Wrong path
```

---

## Resolution

### Immediate Fix

**File**: `.claude/skills/wechat2md/tools/wechat2md_v2.py`
**Line**: 209

```python
# ❌ BEFORE (incorrect)
image_prefix = f"../images/{images_dir.name}/"

# ✅ AFTER (correct)
image_prefix = "images/"  # v2: unified dir structure, images relative to article.md
```

### Affected Article Recovery

**File**: `outputs/20-阅读笔记/认知重建：Speckit 用了三个月，我放弃了——走出工具很强但用不好的困境/article.md`

**Command**:
```bash
sed -i 's|../images/images/|images/|g' "outputs/.../article.md"
```

**Verification**:
```bash
# Check bad links remain (should be 0)
grep -c "../images/images/" article.md
# Output: 0

# Check correct links (should be 20)
grep -c "images/[0-9]" article.md
# Output: 20
```

### Documentation Updates

Updated `.claude/skills/wechat2md/V2_UPGRADE.md` with fix record.

---

## Impact Analysis

### Affected Content

**Single Confirmed Case**:
- Article: "认知重建：Speckit 用了三个月，我放弃了——走出工具很强但用不好的困境"
- Images: 20 total
- Status: ✅ Fixed

**Potential Scope**:
- Any article ingested between v2 release (2026-01-11) and fix (2026-01-12)
- Recommendation: Audit all articles in `outputs/` for path pattern

### User Impact

**Symptoms**:
- Images not displaying in Obsidian
- Broken image icons in Markdown viewers
- Articles appear incomplete

**Workarounds** (before fix):
1. Manual find/replace in each article
2. Manually move images to match expected path
3. Read articles with images ignored

---

## Prevention Measures

### Immediate Actions

1. ✅ Fix Root Cause: Updated path calculation in wechat2md_v2.py
2. ✅ Fix Existing Data: Corrected all bad links in affected article
3. ✅ Document Fix: Added to V2_UPGRADE.md
4. ⏳ Audit Other Articles: Check for similar issues (pending)

### Long-term Prevention

#### 1. Add Automated Tests

Create `.claude/skills/wechat2md/tests/test_image_paths.py`:

```python
def test_image_relative_paths():
    """Test that generated article.md uses correct relative image paths"""
    # Generate test article
    result = run_wechat2md_v2(test_url)

    # Read article.md
    article_content = read_file(result['article_md'])

    # Check image paths
    assert '../images/images/' not in article_content
    assert 'images/001.jpg' in article_content or 'images/001.png' in article_content

    # Verify files exist at referenced paths
    assert Path(result['asset_dir'] / 'images' / '001.jpg').exists()
```

#### 2. Add Post-Generation Validation

In `wechat2md_v2.py`, add after Markdown generation:

```python
# Validate image paths
if images_count > 0:
    import re
    bad_pattern = r'\.\./images/images/'
    if re.search(bad_pattern, markdown_content):
        raise ValueError(
            f"Generated bad image paths! Found pattern: {bad_pattern}\n"
            f"This indicates a bug in image_prefix calculation."
        )
```

#### 3. Improve Testing Checklist

Update `.claude/skills/wechat2md/V2_UPGRADE.md` verification section:

```markdown
### 验证清单

- [ ] Markdown 格式正确（标题、列表、粗体等）
- [ ] 图片下载成功
- [ ] **图片引用正确（相对路径）** ← NEW
- [ ] **在 Obsidian 中打开 article.md 验证图片显示** ← NEW
- [ ] meta.json 包含所有字段
- [ ] 重复抓取不会创建新目录
- [ ] 空 images/ 目录被删除
```

#### 4. Code Review Checklist

Add to code review guidelines:

- [ ] Path calculations verified for new directory structure
- [ ] Image references tested in Obsidian/Markdown viewer
- [ ] Any f-string with `.name` or `.parent` carefully reviewed

---

## Lessons Learned

### Technical Lessons

1. **Path Calculations Are Tricky**
   - Relative paths must account for actual file locations
   - Using `pathlib.Path.name` in f-strings can be error-prone
   - Test paths by attempting to open referenced files

2. **Structure Changes Require Comprehensive Review**
   - Changing from v1's dual-directory to v2's unified structure
   - All path-related code needs review, not just directory creation
   - Legacy assumptions hide in unexpected places

3. **Testing Must Cover User Experience**
   - Verifying files download ≠ verifying files are accessible
   - Must test end-to-end: generate → view in Obsidian
   - Automated tests should check path validity

### Process Lessons

1. **Documentation Should Match Code**
   - V2_UPGRADE.md described correct structure
   - But code implementation had bugs
   - Lesson: Documented design is not enough, need verification

2. **Manual Testing is Insufficient**
   - Only checked that images downloaded
   - Didn't verify Markdown references worked
   - Lesson: Create automated validation tests

3. **User Feedback is Fastest Detection**
   - User noticed issue immediately when opening in Obsidian
   - Should have tested in Obsidian before declaring "done"
   - Lesson: Test in actual user environment

---

## Related Incidents

See also:
- **POSTMORTEM-2026-005**: Duplicate Article Ingestion - Also related to slug/path issues
- **POSTMORTEM-2026-002**: basePath Resolution Error - Path calculation complexity

Common theme: Path and directory structure changes require comprehensive testing and validation.

---

## References

**Fixed Files**:
- `.claude/skills/wechat2md/tools/wechat2md_v2.py` (line 209)
- `.claude/skills/wechat2md/V2_UPGRADE.md` (added fix record)
- `outputs/20-阅读笔记/认知重建：Speckit 用了三个月，我放弃了——走出工具很强但用不好的困境/article.md`

**Documentation**:
- `WECHAT2MD_OPTIMIZATION.md` - v2 optimization summary
- `.claude/skills/wechat2md/V2_UPGRADE.md` - v2 upgrade guide

**Commits**:
- Fix not yet committed (pending review)

---

**Report Created**: 2026-01-12 21:30
**Status**: ✅ Resolved
**Reviewed By**: Pending
**Next Review**: After next article ingestion to verify fix holds
