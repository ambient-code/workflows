# Code Verification Findings

**Date:** [date]
**Repository:** [repository] @ [commit SHA]
**Instruction:** [task and goal description]

---

**Source files checked:** N

## Verification Summary

| Result | Count |
|--------|-------|
| Match | N |
| Mismatch | N |
| Partial | N |
| Undocumented | N |
| Stale | N |

| Severity | Count |
|----------|-------|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |

## Findings by Document

### [path/to/document.md]

#### Verification Finding 1

- **Severity:** Critical
- **Dimension:** Accuracy
- **Doc location:** README.md, "Configuration" section, line 85
- **Code location:** src/config.py:42
- **Documented claim:** "Set `MAX_RETRIES` to configure retry count (default: 3)"
- **Actual behavior:** Default is 5, not 3. See `DEFAULT_MAX_RETRIES = 5`
- **Evidence:**

  ```python
  DEFAULT_MAX_RETRIES = 5  # src/config.py:42
  ```

- **Fix:** Change "default: 3" to "default: 5".

## Undocumented Features

### Feature 1

- **Severity:** High
- **Dimension:** Completeness
- **Code location:** src/cli.py:120
- **Issue:** The `--dry-run` flag exists in code but is not documented
- **Evidence:**

  ```python
  parser.add_argument('--dry-run', help='Preview changes without applying')
  ```

## Stale References

### Stale 1

- **Severity:** High
- **Dimension:** Accuracy
- **Doc location:** docs/guide.md:45
- **Issue:** References `--legacy-mode` flag which no longer exists in code
- **Evidence:** Grep for `legacy-mode` across codebase returns no matches
- **Fix:** Remove the `--legacy-mode` reference.

## Low-Confidence Findings

- "Found `DB_HOST` in docs and `MAAS_DB_HOST` in code — possible match but
  names differ enough to be uncertain"
- "Config key `timeout` appears in example but may be dynamically constructed"

## Inventory Coverage

| Category | Status | Items Found |
|----------|--------|-------------|
| Env vars | completed | N |
| CLI args | completed | N |
| Config schema | skipped (no config libraries) | - |
| API schema | completed | N |
| Data models | completed | N |
| File I/O | skipped (no file operations) | - |
| External deps | completed | N |
| Build/deploy | completed | N |

[Note any agents that failed and why]

## Code Inventory

[The complete merged inventory from Stage 2, organized by workflow and
category]
