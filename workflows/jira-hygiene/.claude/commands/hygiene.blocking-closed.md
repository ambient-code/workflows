# /hygiene.blocking-closed - Find Blocking Tickets with Closed Dependencies

## Purpose

Highlight tickets marked as "Blocking" where all of the blocked tickets are already closed. Suggests either closing the blocking ticket or removing the link.

## Prerequisites

- `/hygiene.setup` must be run first

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key

2. **Query tickets with "blocks" links**:
   ```jql
   project = {PROJECT} AND issueFunction in linkedIssuesOf("project = {PROJECT}", "blocks") AND resolution = Unresolved
   ```
   - This finds all unresolved tickets that block other tickets
   - Fetch: key, summary, status

3. **For each blocking ticket**:
   
   a. **Fetch issue links**:
      - GET `/rest/api/3/issue/{key}?fields=issuelinks`
      - Extract all "outward" links of type "blocks"
      - Get blocked ticket keys
   
   b. **Check resolution status of blocked tickets**:
      - For each blocked ticket, GET `/rest/api/3/issue/{blockedKey}?fields=resolution`
      - Check if resolution is not null (ticket is closed)
   
   c. **Determine if mismatch exists**:
      - If ALL blocked tickets are closed: flag for review
      - If at least one blocked ticket is open: skip (still validly blocking)

4. **Write report**:
   - Save to `artifacts/jira-hygiene/reports/blocking-closed-mismatch.md`
   - Include: blocking ticket key, summary, list of closed blocked tickets

5. **Display report**:
   ```
   Found N blocking tickets where all dependencies are closed:
   
   PROJ-123 "Fix database migration issue"
     Blocks (all closed):
     - PROJ-145 "Deploy new schema" (Closed 5 days ago)
     - PROJ-167 "Update migration scripts" (Closed 3 days ago)
     
     Suggested action: Close PROJ-123 or remove blocking links
   
   PROJ-456 "Security audit blocker"
     Blocks (all closed):
     - PROJ-500 "Implement OAuth" (Closed 2 weeks ago)
     
     Suggested action: Close PROJ-456 or remove blocking link
   ```

6. **No bulk operation**:
   - This command is **report-only** (no automatic changes)
   - User must manually review each case
   - Closing or unlinking requires human judgment

## Output

- `artifacts/jira-hygiene/reports/blocking-closed-mismatch.md`

## Example Report

```markdown
# Blocking Tickets with Closed Dependencies

**Project**: PROJ  
**Generated**: 2026-04-07 10:30 UTC  
**Total Mismatches**: 3 tickets

## Summary

Found 3 tickets that are still marked as blocking, but all blocked items are already closed. These may be ready to close or the blocking links should be removed.

## Tickets Requiring Review

### PROJ-123 "Fix database migration issue"

**Status**: In Progress  
**Last Updated**: 2026-03-25

**Blocks** (all closed):
- PROJ-145 "Deploy new schema" (Closed: 2026-04-02, 5 days ago)
- PROJ-167 "Update migration scripts" (Closed: 2026-04-04, 3 days ago)

**Suggested Actions**:
1. If migration issue is resolved: Close PROJ-123
2. If new blockers emerged: Update links to reflect current blockers
3. If no longer blocking: Remove the "blocks" links

---

### PROJ-456 "Security audit blocker"

**Status**: To Do  
**Last Updated**: 2026-03-15

**Blocks** (all closed):
- PROJ-500 "Implement OAuth" (Closed: 2026-03-24, 14 days ago)

**Suggested Actions**:
1. If audit is complete: Close PROJ-456
2. If audit revealed new work: Create new tickets and update links
3. If audit was cancelled: Close PROJ-456

---

## Recommendations

These tickets require manual review because:
- The blocking ticket may represent ongoing work not yet tracked
- New dependencies may have emerged
- The ticket may have served its purpose and should be closed

**Action Required**: Review each ticket and either close it or update its blocking relationships.
```

## Link Type Detection

Jira uses different link types for blocking relationships:
- "Blocks" / "is blocked by"
- "Blocker" (custom link type in some instances)

This command checks for the standard "Blocks" link type. If your project uses custom link types, the field ID may need adjustment.

## Why No Bulk Operation?

Unlike other hygiene commands, this one doesn't offer bulk closure because:

1. **Context required**: Need to understand why the blocker exists
2. **May still be valid**: Blocker work may not be tracked in Jira
3. **Risk of data loss**: Automatically removing links could lose important context
4. **Manual judgment needed**: Each case is unique

## Error Handling

- **Issue links unavailable**: Some tickets may have restricted access; skip and log
- **Blocked ticket not found (404)**: Ticket may have been deleted; note in report
- **No blocking links found**: Report "No blocking relationships found in {PROJECT}"
