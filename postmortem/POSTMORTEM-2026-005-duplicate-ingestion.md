# Postmortem Report: Duplicate Article Ingestion Due to Slug Collision

**Report ID**: POSTMORTEM-2026-005
**Date**: 2026-01-12
**Severity**: P2 - Medium
**Status**: Partially Resolved
**Author**: Claude Code + User Review

## Executive Summary

The wechat-archiver skill generated duplicate asset directories for the same article when run multiple times on different dates. The slug format included date prefix (YYYYMMDD), causing the same article URL to create different directories on different days: `20260111-...` and `20260112-...`.

**Impact**: Duplicate content wasting disk space, user confusion about which version is current, inconsistency in asset organization.

**Root Cause**: Slug generation used date prefix instead of using asset_id alone for uniqueness, causing daily variations for same content.

---

## Timeline

| Date | Time | Event |
|------|------|-------|
| 2026-01-11 | Late evening | First ingestion of Cursor article (20260111-...) |
| 2026-01-12 | Morning | Second ingestion of same Cursor article (20260112-...) |
| 2026-01-12 | 07:50 | User noticed duplicate directories with same asset_id |
| 2026-01-12 | 07:55 | Investigation identified date prefix in slug format |
| 2026-01-12 | 08:00 | Deleted duplicate 20260112 directory |
| 2026-01-12 | 08:05 | Documented issue, added --simple-slug option as workaround |
| 2026-01-12 | 08:14 | Commit with documentation pushed (5eb3800) |

---

## Incident Details

### Severity Assessment

**Severity Level**: P2 - Medium

**Rationale**:
- Not a functional failure (both versions work correctly)
- User experience issue (confusion about which is current)
- Wasted disk space but not critical
- Manual cleanup required (annoying but not blocking)

**Affected Components**:
- `.claude/skills/wechat-archiver/tools/wechat_archiver.py`
- Slug generation logic
- Asset organization in outputs/

**Scope**:
- Affects all articles ingested on multiple days
- More likely to affect popular articles re-ingested
- Not a one-time issue - will recur

### Root Cause Analysis

#### Direct Cause

Slug generation format included date prefix:

```python
# ❌ PROBLEMATIC - Original format
date_prefix = datetime.now().strftime("%Y%m%d")  # Changes daily
title_slug = sanitize_title(article_title, max_len=50)
asset_id_short = asset_id[:6]
slug = f"{date_prefix}-{title_slug}-{asset_id_short}"
# Results in: 20260111-... vs 20260112-... for same article
```

**Example**:
- Day 1 (2026-01-11): `20260111-大道至简Cursor...-41f7f7/`
- Day 2 (2026-01-12): `20260112-大道至简Cursor...-41f7f7/`
- Same `asset_id[:6]` (41f7f7) because same URL
- Different date prefixes cause different directories

#### Underlying Causes

1. **Design Decision: Date Prefix**
   - Date prefix added for human readability
   - Helps identify when article was ingested
   - BUT causes duplicates when re-ingested on different days

2. **No Duplicate Detection**
   - Skill checks for existing directory by slug
   - Different slug → no match → creates new directory
   - Doesn't check by asset_id (which would match)

3. **Idempotency Not Implemented**
   - Documented idempotency using hash_content
   - BUT only checks if directory already exists
   - Different slug → directory doesn't exist → no check performed

### Contributing Factors

- **Daily Workflow**: User runs skill daily to ingest new articles
- **Re-ingestion**: Same article might be re-processed on different days
- **No Warning**: No alert that article already ingested with different slug
- **Manual Cleanup**: User had to manually identify and delete duplicates

---

## Impact Analysis

### Affected Files

**Duplicate Directories**:
```
outputs/20-阅读笔记/
├── 20260111-大道至简Cursor发表了一个长篇-悔改书--41f7f7/  # Original
└── 20260112-大道至简Cursor发表了一个长篇-悔改书--41f7f7/  # Duplicate
```

**Disk Space**:
- Each directory: ~30KB (article.md + note.md + diagram.canvas + meta.json + run.jsonl)
- Duplicate waste: ~30KB
- Not critical but accumulates over time

**Content Hash Verification**:
```bash
# Both directories have identical hash_content
20260111/.../meta.json: "hash_content": "8b06d71a..."
20260112/.../meta.json: "hash_content": "8b06d71a..."
# Confirms same article content
```

### User Impact

**Confusion**:
> "为什么同一个文章被抓取了2次？"

**Questions Raised**:
- Which directory is current/authoritative?
- Should I keep both or delete one?
- Will this happen every time I re-ingest?
- Which one should I use for reference?

**Manual Actions Required**:
- Identify duplicates (compare asset_id)
- Decide which version to keep
- Delete older version manually
- Update any references/links

### System Impact

**Asset Organization**:
- outputs/ directory becomes cluttered
- Harder to find "current" version
- Inconsistent naming

**Backward Compatibility**:
- Existing references to date-prefixed slugs break
- Need to decide: keep date prefix or remove entirely?

---

## Reproduction Steps

### How to Reproduce

1. **Day 1 (2026-01-11)**:
   ```bash
   /wechat-archiver article_url=https://mp.weixin.qq.com/s/xIwf2-12ef-5KeLPbvFZAQ
   # Creates: 20260111-大道至简Cursor...-41f7f7/
   ```

2. **Day 2 (2026-01-12)**:
   ```bash
   /wechat-archiver article_url=https://mp.weixin.qq.com/s/xIwf2-12ef-5KeLPbvFZAQ
   # Creates: 20260112-大道至简Cursor...-41f7f7/
   # NOT detected as duplicate (different slug)
   ```

3. **Result**: Two directories for same article

### Current Behavior

**Duplicate Detection Logic**:
```python
slug = f"{date_prefix}-{title_slug}-{asset_id_short}"
asset_dir = Path(cwd) / "outputs" / folder / slug

if asset_dir.exists():
    print("Directory exists, skipping...")
else:
    create_directory(asset_dir)  # Runs because slug different
```

**Problem**:
- Checks if `20260111-...` exists → NO (day 2)
- Checks if `20260112-...` exists → NO (day 1)
- Both pass check, both created

### Expected Behavior

**With Idempotency**:
```python
# Check by asset_id, not just slug
existing = find_existing_asset(asset_id)
if existing:
    if hash_match(existing.hash_content, new_hash):
        skip("Content unchanged")
    else:
        update(existing)
else:
    create_new(asset_id)
```

---

## Resolution

### Immediate Actions

**Status**: Partially Resolved

**Actions Taken**:
1. ✅ Identified duplicate directories
2. ✅ Verified content identical via hash_content
3. ✅ Deleted duplicate (20260112) directory
4. ✅ Kept original (20260111) directory
5. ✅ Documented issue in BUGFIXES.md

**Not Fixed**:
- ❌ Slug generation still uses date prefix
- ❌ Will create duplicates if run again tomorrow (20260113)
- ❌ No automatic duplicate detection by asset_id

### Workaround Added

**Option**: `--simple-slug` flag added to wechat_archiver.py

```bash
# Without date prefix (no daily duplicates)
/wechat-archiver article_url=... --simple-slug
# Creates: 大道至简Cursor...-41f7f7/ (no date)
```

**Trade-offs**:
- ✅ No daily duplicates for same article
- ✅ Simpler, shorter directory names
- ❌ Lose ingestion date information
- ❌ Harder to identify when article was ingested

### Recommended Fix

**Option 1**: Use asset_id as primary identifier
```python
slug = f"{asset_id[:6]}-{title_slug}"  # No date prefix
# OR
slug = asset_id  # Just use asset_id
```

**Option 2**: Implement proper duplicate detection
```python
# Check by asset_id, not slug
existing_dirs = search_by_asset_id(asset_id)
if existing_dirs:
    # Use existing, update if changed
    use_existing(existing_dirs[0])
```

**Option 3**: Keep date prefix but add symlink
```python
# Always use latest: 20260113-... (current date)
# Create symlink: latest → 20260113-...
# Old versions: 20260111-..., 20260112-... (archived)
```

---

## Lessons Learned

### Technical Lessons

1. **Uniqueness vs Readability Trade-off**
   - Date prefix: readable but causes duplicates
   - Asset ID only: unique but not human-friendly
   - Need to decide primary goal

2. **Idempotency Requires Multiple Checks**
   - Slug check not sufficient
   - Must check by content hash (asset_id)
   - Must check by actual article URL

3. **Date in Filename is Anti-pattern**
   - Dates change, causing duplicates
   - Better to store date in metadata, not filename
   - Filename should be stable identifier

4. **Slug Design Considerations**
   - Must be unique for same content
   - Should be reproducible (same input → same slug)
   - Should not contain temporal data

### Process Lessons

1. **Test Re-runs Early**
   - Should have tested running skill twice on same article
   - Would have caught duplicate immediately
   - Important for idempotent workflows

2. **User Feedback Loop**
   - User noticed duplicates quickly
   - Good signal that design needs revision
   - Should incorporate feedback into design

3. **Documentation is Key**
   - Issue documented in BUGFIXES.md
   - Workaround (--simple-slug) clearly explained
   - Helps users while proper fix pending

4. **Design Review Process**
   - Slug format wasn't reviewed for duplicate scenario
   - Should consider edge cases in design phase
   - Need design review checklist

---

## Prevention Measures

### Immediate Actions

1. ✅ **Document Issue**
   - Created BUGFIXES.md explaining duplicate problem
   - Documented --simple-slug workaround
   - Added to wechat-archiver documentation

2. ✅ **Manual Cleanup**
   - Delete duplicate directories when found
   - Verify via hash_content comparison
   - Keep earliest/ingested version

3. ✅ **User Education**
   - Explain slug format to users
   - Warn about re-ingestion on different days
   - Provide guidance on handling duplicates

### Long-term Actions

1. **Implement Proper Duplicate Detection**
   ```python
   def find_existing_asset(asset_id: str) -> Optional[Path]:
       """Find existing directory by asset_id, not slug."""
       outputs_dir = Path("outputs")
       for existing_dir in outputs_dir.rglob("meta.json"):
           meta = json.load(open(existing_dir))
           if meta.get("asset_id") == asset_id:
               return existing_dir.parent
       return None
   ```

2. **Change Slug Format**
   - [ ] Remove date prefix from slug
   - [ ] Use only asset_id or asset_id+title
   - [ ] Update documentation
   - [ ] Migration guide for existing slugs

3. **Add Idempotency Enforcement**
   - [ ] Check by asset_id before creating directory
   - [ ] If exists: check hash_content
   - [ ] If hash matches: skip entirely
   - [ ] If hash differs: update existing

4. **Create Asset Index**
   - [ ] Maintain index of all ingested assets
   - [ ] Map asset_id → directory path
   - [ ] Quick lookup for duplicate detection
   - [ ] Store in JSON database

5. **Add Warning System**
   - [ ] Detect duplicate by asset_id
   - [ ] Warn user: "Article already ingested on [date]"
   - [ ] Ask user: "Update existing or skip?"
   - [ ] Provide clear options

---

## Follow-up Actions

### Completed ✅

1. Identified duplicate issue
2. Cleaned up duplicate directories
3. Documented in BUGFIXES.md
4. Added --simple-slug workaround
5. Commit pushed to GitHub

### Pending ⏳

1. [ ] Implement find_existing_asset() function
2. [ ] Add duplicate detection to wechat_archiver.py
3. [ ] Decide on final slug format (date or no date)
4. [ ] Update all documentation with slug format decision
5. [ ] Create migration guide for existing assets
6. [ ] Add idempotency tests

### Recommendations

1. **Short-term**: Use --simple-slug
   ```bash
   /wechat-archiver article_url=... --simple-slug
   ```
   - Avoids duplicates
   - Simpler slugs
   - Good enough for now

2. **Long-term**: Implement proper duplicate detection
   - Check by asset_id before creating
   - Re-use existing directory if found
   - Update content if hash differs
   - Skip if hash matches

3. **Slug Format Decision**
   - **Option A**: Remove date entirely
     - Pros: No duplicates, simpler
     - Cons: Lose temporal info

   - **Option B**: Keep date in subdirectory
     - `outputs/20-阅读笔记/2026/01/11/slug/`
     - Pros: Temporal structure, no duplicates
     - Cons: More complex directory structure

   - **Option C**: Date in metadata only
     - Pros: Filename stable, all benefits
     - Cons: Must open meta.json to see date

   **Recommendation**: Option C - Date in metadata only

4. **For Users**
   - Use --simple-slug flag to avoid duplicates
   - Keep one copy of article
   - Delete old versions manually for now
   - Watch for future fix announcement

---

## Technical Appendix: Slug Analysis

### Current Slug Format

```python
slug = f"{date_prefix}-{title_slug}-{asset_id_short}"
# Example: 20260112-大道至简Cursor发表了一个长篇悔改书-41f7f7
```

**Components**:
- `date_prefix`: YYYYMMDD (8 bytes) - Changes daily
- `title_slug`: Sanitized title (up to 50 chars) - Stable for same article
- `asset_id_short`: First 6 chars of SHA1(URL) - Stable for same URL

**Uniqueness**:
- Same URL → Same asset_id_short
- Different day → Different date_prefix
- Result: Different slug, different directory

**Collisions**:
- Same title on different day → Same title_slug
- Same URL → Same asset_id_short
- Different day → Different slug (not a collision, just duplicate)

### Alternative Slug Formats

**Format A**: No date prefix
```python
slug = f"{title_slug}-{asset_id_short}"
# Example: 大道至简Cursor发表了一个长篇悔改书-41f7f7
# Pros: Stable, no duplicates
# Cons: Can't tell ingestion date from directory name
```

**Format B**: Date in subdirectory
```python
date_dir = datetime.now().strftime("%Y/%m/%d")
slug = f"{title_slug}-{asset_id_short}"
path = f"outputs/{folder}/{date_dir}/{slug}/"
# Example: outputs/20-阅读笔记/2026/01/11/大道至简Cursor...-41f7f7/
# Pros: Temporal organization, no duplicates
# Cons: Deep nesting, complex
```

**Format C**: Asset ID only
```python
slug = asset_id  # Full SHA1 hash
# Example: 41f7f7018d7d08cddd3d7509f691bb9bb27518f4
# Pros: Guaranteed unique, stable
# Cons: Not human-friendly, no title
```

**Recommendation**: Format A (no date prefix) with date in meta.json

---

## References

**Related Files**:
- `.claude/skills/wechat-archiver/BUGFIXES.md`
- `.claude/skills/wechat-archiver/tools/wechat_archiver.py`
- `.claude/skills/wechat-archiver/rules/idempotency.md`

**Related Commits**:
- 5eb3800 - feat: add wechat-archiver skill and improve base table generation

**Duplicate Directories** (Before Cleanup):
- `outputs/20-阅读笔记/20260111-大道至简Cursor发表了一个长篇-悔改书--41f7f7/` ✅ Kept
- `outputs/20-阅读笔记/20260112-大道至简Cursor发表了一个长篇-悔改书--41f7f7/` ❌ Deleted

---

**Report Status**: ✅ Documented, ⏳ Fix Pending
**Next Review**: After implementing proper duplicate detection
