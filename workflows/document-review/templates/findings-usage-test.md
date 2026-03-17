# Usage Test Findings

**Date:** [date]
**Repository:** [repository] @ [commit SHA]
**Instruction:** [task and goal description]

---

**Cluster:** [cluster URL]
**Documents tested:** N
**Interactions executed:** N
**Interactions passed:** N
**Interactions failed:** N

## Execution Summary

| Result | Count |
|--------|-------|
| Pass | N |
| Fail — doc error | N |
| Fail — missing docs | N |
| Fail — unexpected behavior | N |
| Undocumented (no expected output) | N |

## User Journey Assessment

[Assessment of the overall documented user experience after installation.
Can a user discover, follow, and succeed with the documented interactions?]

## Findings by Document

### [path/to/usage-doc.md]

#### Interaction N: [brief description]

- **Source:** Section "[heading]", line N
- **Interaction:** `oc get myresource -n my-namespace`
- **Expected result:** [what docs say should happen]
- **Actual result:** [what actually happened]
- **Dimension:** Accuracy
- **Resolution:** [what the correct interaction or output is]
- **Fix:** [corrected interaction or output, if known with high confidence]

#### Interaction N: [brief description]

...

### [path/to/another-doc.md]

...

## User Experience Issues

### Issue 1: [brief description]

- **Dimension:** Completeness | Structure | Examples
- **Files:** [which docs]
- **Issue:** [what's missing or could be better]

## Troubleshooting Guide

This section documents errors users are likely to encounter when following
the usage documentation, along with their solutions. `/fix` uses this to add
error-handling guidance to the documentation.

### Error 1: [error message or symptom]

- **When:** [which interaction triggers this]
- **Cause:** [why it happens]
- **Solution:** [how to fix it]
- **Prevention:** [what the docs should say to prevent this]

### Error 2: [error message or symptom]

...
