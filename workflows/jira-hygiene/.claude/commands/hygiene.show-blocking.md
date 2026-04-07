# /hygiene.show-blocking - Show Blocking Tickets

## Purpose

Simple query to display all tickets marked with "Blocker" priority in the project. This highlights critical items that may be blocking other work.

## Prerequisites

- `/hygiene.setup` must be run first

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key

2. **Query blocking tickets**:
   ```jql
   project = {PROJECT} AND priority = Blocker AND resolution = Unresolved
   ```
   - Fetch: key, summary, assignee, status, created, updated
   - Order by updated descending (most recent first)

3. **Format as markdown table**:
   ```markdown
   # Blocking Tickets in {PROJECT}
   
   **Total**: N tickets
   **Generated**: {timestamp}
   
   | Key | Summary | Assignee | Status | Age | Last Updated |
   |-----|---------|----------|--------|-----|--------------|
   | PROJ-123 | Critical API failure | John Doe | In Progress | 5d | 2d ago |
   | PROJ-456 | Database migration blocked | Unassigned | To Do | 12d | 3d ago |
   ```

4. **Write report**:
   - Save to `artifacts/jira-hygiene/reports/blocking-tickets.md`

5. **Display summary**:
   - Show table in output
   - Highlight unassigned blockers (if any)
   - Note oldest blocker

## Output

- `artifacts/jira-hygiene/reports/blocking-tickets.md`

## Example Report

```markdown
# Blocking Tickets in PROJ

**Total**: 3 tickets  
**Generated**: 2026-04-07 10:30 UTC

## Summary

- 2 tickets assigned
- 1 ticket unassigned ⚠️
- Oldest blocker: 12 days (PROJ-456)

## Tickets

| Key | Summary | Assignee | Status | Age | Last Updated |
|-----|---------|----------|--------|-----|--------------|
| PROJ-123 | Critical API failure in auth endpoint | John Doe | In Progress | 5d | 2d ago |
| PROJ-456 | Database migration blocked by schema lock | Unassigned | To Do | 12d | 3d ago |
| PROJ-789 | Production deployment failing | Jane Smith | Code Review | 3d | 1d ago |

## Recommendations

- **PROJ-456**: Assign to database team immediately (unassigned for 12 days)
- **PROJ-123**: Follow up on progress (blocker for 5 days)
```

## Error Handling

- **No blocking tickets found**: Report "No blocking tickets in {PROJECT}" (good news!)
- **Query failed**: Check JQL syntax, validate project key
