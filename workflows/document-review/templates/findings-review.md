# Documentation Review Findings

**Project:** [name]
**Reviewed:** [date]
**Documents reviewed:** N of M

## Summary

| Severity | Count |
|----------|-------|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |
| **Total** | **N** |

| Dimension | Issues |
|-----------|--------|
| Accuracy | N |
| Completeness | N |
| Consistency | N |
| Clarity | N |
| Currency | N |
| Structure | N |
| Examples | N |

## Findings by Document

### [path/to/document.md]

**Audience:** [end user | developer | operator | general]
**Audience fit:** [appropriate | needs adjustment — explanation]

#### Finding 1

- **Severity:** Critical
- **Dimension:** Accuracy
- **Location:** Section "Installation", line 42
- **Description:** The documented command uses a flag that doesn't exist.
- **Evidence:** `pip install --global mypackage`
  (`--global` is not a valid pip flag)

#### Finding 2

...

### [path/to/another-doc.md]

...

## Cross-Document Issues

### Issue 1

- **Severity:** Medium
- **Documents:** doc-a.md, doc-b.md
- **Description:** ...
- **Evidence:** ...
