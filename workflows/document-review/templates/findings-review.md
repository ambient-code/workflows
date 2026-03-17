# Documentation Review Findings

**Date:** [date]
**Repository:** [repository]
**Instruction:** [task and goal description]

---

## Summary

| Dimension | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| Accuracy | N | N | N | N | N |
| Completeness | N | N | N | N | N |
| Consistency | N | N | N | N | N |
| Clarity | N | N | N | N | N |
| Currency | N | N | N | N | N |
| Structure | N | N | N | N | N |
| Examples | N | N | N | N | N |
| **Total** | **N** | **N** | **N** | **N** | **N** |

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
