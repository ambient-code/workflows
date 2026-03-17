# Cluster Cleanup Report

**Date:** [date]
**Repository:** [repository] @ [commit SHA]
**Instruction:** [task and goal description]

---

**Cluster:** [url]
**Changes to revert:** N
**Successfully reverted:** N
**Failed to revert:** N

## Summary

| Result | Count |
|--------|-------|
| Reverted | N |
| Already gone (cascade) | N |
| Failed | N |

## Reverted Changes

### Change N: [description]

- **Action:** `[revert command]`
- **Result:** Success

### Change N: [description]

- **Action:** `[revert command]`
- **Result:** Already gone (cascade-deleted with namespace)

## Failed Reverts

### Change N: [description]

- **Action:** `[revert command]`
- **Error:** [error message]
- **Manual cleanup required:** [what the user needs to do]

## Manual Cleanup Required

[If any reverts failed or shell script effects could not be fully reverted,
list the manual steps the user must take here. Remove this section if all
reverts succeeded.]

- [ ] [manual step 1]
- [ ] [manual step 2]
