# Code Verification Findings

**Date:** [date]
**Repository:** [repository]
**Instruction:** [task and goal description]

---

**Source files checked:** N

## Verification Summary

| Result | Count |
|--------|-------|
| Match | N |
| Mismatch (Critical) | N |
| Partial (Low) | N |
| Undocumented (High) | N |

## Findings by Document

### [path/to/document.md]

#### Verification Finding 1

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

- **Dimension:** Completeness
- **Code location:** src/cli.py:120
- **Issue:** The `--dry-run` flag exists in code but is not documented
- **Evidence:**

  ```python
  parser.add_argument('--dry-run', help='Preview changes without applying')
  ```
