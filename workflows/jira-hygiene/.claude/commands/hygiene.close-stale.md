# /hygiene.close-stale - Close Stale Tickets

## Purpose

Find and close stale tickets in bulk based on priority-specific thresholds. Groups candidates by priority for user review before closing.

## Prerequisites

- `/hygiene.setup` must be run first

## Arguments

Optional: Override default thresholds
- `--highest <days>` - Threshold for Highest priority (default: 7)
- `--high <days>` - Threshold for High priority (default: 7)
- `--medium <days>` - Threshold for Medium priority (default: 14)
- `--low <days>` - Threshold for Low priority (default: 30)
- `--lowest <days>` - Threshold for Lowest priority (default: 30)
- `--dry-run` - Show what would be closed without making changes

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key and staleness_thresholds
   - Apply any command-line overrides

2. **Query stale tickets by priority**:
   For each priority level (Highest, High, Medium, Low, Lowest):
   ```jql
   project = {PROJECT} AND priority = {PRIORITY} AND updated < -{DAYS}d AND resolution = Unresolved
   ```
   - Fetch: key, summary, assignee, status, updated, priority
   - Group results by priority

3. **Write candidates file**:
   - Save to `artifacts/jira-hygiene/candidates/close-stale.json`
   - Include: key, summary, priority, days since update, assignee

4. **Display summary by priority**:
   ```
   Found N stale tickets to close:
   
   Highest/High (>7 days): 3 tickets
     PROJ-100 "Old critical bug" (12 days, assigned to John)
     PROJ-101 "High priority feature" (9 days, unassigned)
     PROJ-102 "Urgent fix needed" (8 days, assigned to Jane)
   
   Medium (>14 days): 5 tickets
     ...
   
   Low/Lowest (>30 days): 12 tickets
     ...
   
   Total: 20 tickets will be closed
   ```

5. **Ask for confirmation**:
   - If `--dry-run`: Skip this step, display "DRY RUN - No changes made"
   - Otherwise prompt: "Close these stale tickets? (yes/no/by-priority)"
   - "by-priority": Let user approve each priority group separately

6. **Execute closure**:
   - For each approved ticket:
     - Add comment: "Due to lack of activity, this item has been closed. If you feel that it should be addressed, please reopen it."
     - Transition to "Closed" or "Done" status (use project's closed status)
     - POST `/rest/api/3/issue/{key}/comment` then PUT `/rest/api/3/issue/{key}/transitions`
     - Rate limit: 0.5s between tickets

7. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/close-stale-{timestamp}.log`
   - Include: timestamp, key, priority, days stale, result (success/error)

## Output

- `artifacts/jira-hygiene/candidates/close-stale.json`
- `artifacts/jira-hygiene/operations/close-stale-{timestamp}.log`

## Example Candidates JSON

```json
{
  "thresholds": {
    "Highest": 7,
    "High": 7,
    "Medium": 14,
    "Low": 30,
    "Lowest": 30
  },
  "candidates_by_priority": {
    "Highest": [
      {
        "key": "PROJ-100",
        "summary": "Old critical bug in payment flow",
        "priority": "Highest",
        "days_stale": 12,
        "last_updated": "2026-03-26",
        "assignee": "John Doe",
        "status": "In Progress"
      }
    ],
    "Medium": [...],
    "Low": [...]
  },
  "total_count": 20
}
```

## Staleness Calculation

**Days stale** = Days since last update (not created date)

Last update includes:
- Status changes
- Comments
- Field updates
- Assignee changes

If a ticket has recent activity, it's not stale (even if created long ago).

## Closure Message

Standard message posted as comment before closing:

> Due to lack of activity, this item has been closed. If you feel that it should be addressed, please reopen it.

This message:
- Is polite and non-judgmental
- Acknowledges the ticket may still be valid
- Provides clear action (reopen if needed)
- Doesn't assign blame

## Error Handling

- **Transition failed**: Some tickets may not have "Close" transition; try "Done", then "Resolved"
- **No permission**: Log error, skip ticket, continue with others
- **Ticket already closed**: Skip silently (idempotent)
- **Rate limit**: Increase delay to 1s, retry
