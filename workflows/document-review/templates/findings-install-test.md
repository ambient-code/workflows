# Installation Test Findings

**Date:** [date]
**Repository:** [repository]
**Instruction:** [task and goal description]

---

**Cluster:** [cluster URL]
**Documents tested:** N
**Steps executed:** N
**Steps passed:** N
**Steps failed:** N

## Execution Summary

| Result | Count |
|--------|-------|
| Pass | N |
| Fail — doc error | N |
| Fail — missing step | N |
| Fail — wrong order | N |
| Corrected and continued | N |

## Flow Assessment

[Assessment of the logical ordering of installation steps. Note any ordering
issues, missing prerequisites, or implicit steps.]

## Findings by Document

### [path/to/install-doc.md]

#### Step N: [brief description]

- **Source:** Section "[heading]", line N
- **Command:** `oc apply -f config.yaml`
- **Expected result:** [what docs say should happen]
- **Actual result:** [what actually happened]
- **Severity:** Critical
- **Dimension:** Accuracy
- **Resolution:** [what the correct command/step is]

#### Step N: [brief description]

...

### [path/to/another-doc.md]

...

## Flow Issues

### Issue 1: [brief description]

- **Severity:** Critical | High
- **Dimension:** Structure | Completeness
- **Documents:** [which docs]
- **Description:** [what's wrong with the ordering or flow]
- **Correct order:** [what the order should be]

## Troubleshooting Guide

This section documents errors users are likely to encounter when following the
installation instructions, along with their solutions. `/fix` uses this to add
error-handling guidance to the documentation.

### Error 1: [error message or symptom]

- **When:** [which step triggers this]
- **Cause:** [why it happens]
- **Solution:** [how to fix it]
- **Prevention:** [what the docs should say to prevent this]

### Error 2: [error message or symptom]

...
