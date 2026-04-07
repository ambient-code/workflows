# /hygiene.unassigned-progress - Show In-Progress Tickets Without Assignee

## Purpose

Simple query to find tickets that are marked as "In Progress" but have no assignee. This highlights potential ownership issues.

## Prerequisites

- `/hygiene.setup` must be run first

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key

2. **Query unassigned in-progress tickets**:
   ```jql
   project = {PROJECT} AND status = "In Progress" AND assignee is EMPTY AND resolution = Unresolved
   ```
   - Fetch: key, summary, status, created, updated, reporter
   - Order by updated descending

3. **Format as markdown table**:
   ```markdown
   # In-Progress Tickets Without Assignee
   
   **Total**: N tickets
   **Generated**: {timestamp}
   
   | Key | Summary | Status | Reporter | Age | Last Updated |
   |-----|---------|--------|----------|-----|--------------|
   | PROJ-123 | Implement new API | In Progress | John Doe | 8d | 2d ago |
   | PROJ-456 | Fix login bug | In Progress | Jane Smith | 5d | 1d ago |
   ```

4. **Write report**:
   - Save to `artifacts/jira-hygiene/reports/unassigned-progress.md`

5. **Display summary**:
   - Show table in output
   - Highlight oldest ticket
   - Group by reporter if helpful

## Output

- `artifacts/jira-hygiene/reports/unassigned-progress.md`

## Example Report

```markdown
# In-Progress Tickets Without Assignee

**Project**: PROJ  
**Generated**: 2026-04-07 10:30 UTC  
**Total**: 4 tickets

## Summary

Found 4 tickets marked as "In Progress" but with no assignee. These tickets may be orphaned or forgotten.

- Oldest: 12 days (PROJ-789)
- Most recent update: 1 day ago (PROJ-456)

## Tickets

| Key | Summary | Status | Reporter | Age | Last Updated |
|-----|---------|--------|----------|-----|--------------|
| PROJ-789 | Refactor authentication module | In Progress | John Doe | 12d | 5d ago |
| PROJ-123 | Implement new API endpoint | In Progress | John Doe | 8d | 2d ago |
| PROJ-456 | Fix login bug on mobile | In Progress | Jane Smith | 5d | 1d ago |
| PROJ-234 | Update documentation | In Progress | Bob Johnson | 3d | 6h ago |

## Recommendations

**Immediate Action Needed**:
- **PROJ-789**: No updates in 5 days, assign or move back to backlog
- **PROJ-123**: Assign to team member actively working on API

**By Reporter**:
- John Doe (2 tickets): Follow up on PROJ-789 and PROJ-123
- Jane Smith (1 ticket): Assign PROJ-456 or update status
- Bob Johnson (1 ticket): Recent activity on PROJ-234, verify assignment needed

## Common Causes

Tickets end up "In Progress" without assignee when:
1. Assignee was removed but status not updated
2. Ticket was started but never formally assigned
3. Team member left and tickets weren't reassigned
4. Workflow allows status change without assignment

## Suggested Actions

For each ticket:
1. **Assign to owner**: If work is ongoing, assign to current owner
2. **Move to backlog**: If work was abandoned, revert to "To Do" or "Backlog"
3. **Close if duplicate**: Check for duplicate tickets that may have superseded this one
```

## Status Variations

Different Jira projects may use different status names for "in progress":
- "In Progress"
- "In Development"
- "Work In Progress"
- "Doing"

This command checks for "In Progress" by default. If your project uses a different name, the JQL will need adjustment or the workflow can be enhanced to detect all "in progress category" statuses.

## Why This Matters

Unassigned in-progress tickets indicate:
- **Lost ownership**: Work may be forgotten
- **Stale work**: Previous assignee moved on
- **Process gaps**: Status changed without assignment
- **Coordination issues**: Team doesn't know who's working on what

Regular checks help maintain accountability and prevent work from falling through cracks.

## Error Handling

- **No tickets found**: Report "No in-progress tickets without assignee" (good news!)
- **Status name mismatch**: If query returns empty but you expect results, check project's status names
- **Query failed**: Verify project key is correct
