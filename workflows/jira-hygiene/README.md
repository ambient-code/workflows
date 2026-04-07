# Jira Hygiene Workflow

Systematic Jira project hygiene through automated detection, intelligent suggestions, and safe bulk operations.

## Overview

This workflow helps maintain clean and well-organized Jira projects by:

- **Linking orphaned tickets**: Connect stories to epics and epics to initiatives using semantic matching
- **Generating activity summaries**: Create weekly summaries for epics/initiatives by analyzing child item changes
- **Closing stale tickets**: Bulk-close inactive tickets based on priority-specific thresholds
- **Suggesting triage outcomes**: Recommend priority and status for untriaged items
- **Identifying data quality issues**: Find missing assignees, activity types, and broken blocking relationships

All bulk operations use a **review-then-execute pattern** for safety: you see what will change before any changes are made.

## Prerequisites

### Jira API Credentials

Set these environment variables before using the workflow:

```bash
export JIRA_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
```

**To generate a Jira API token**:
1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Name it (e.g., "Jira Hygiene Workflow")
4. Copy the token (you won't be able to see it again)

### Required Permissions

Your Jira account must have:
- Read access to the target project(s)
- Edit access to update issues
- Permission to add comments
- Permission to close issues

## Getting Started

1. **Run setup** to configure the workflow:
   ```
   /hygiene.setup
   ```
   This validates your Jira connection and configures project settings.

2. **Choose a hygiene task**:
   - Start with simple reports: `/hygiene.show-blocking` or `/hygiene.unassigned-progress`
   - Try bulk operations in dry-run mode: `/hygiene.close-stale --dry-run`
   - Use linking operations to organize your backlog: `/hygiene.link-epics`

3. **Review artifacts** in `artifacts/jira-hygiene/`:
   - Check candidate files before bulk operations
   - Review operation logs for audit trail
   - Read generated summaries before posting

## Commands

### Setup & Configuration

#### `/hygiene.setup`

Validate Jira connection and configure project settings.

**What it does**:
- Tests API credentials
- Prompts for project key and initiative project mapping
- Fetches Activity Type field metadata
- Creates `artifacts/jira-hygiene/config.json`

**When to use**: First command to run, or when changing projects

---

### Linking Operations

#### `/hygiene.link-epics`

Link orphaned stories to epics using semantic matching.

**What it does**:
- Finds stories without epic links
- Extracts keywords from story summary/description
- Searches for matching epics (50% keyword overlap threshold)
- Suggests creating new epic if no good match exists

**Review-then-execute**: Yes  
**Dry-run support**: Via manual review step

**Example output**:
```
Found 15 orphaned stories:
- 10 stories with good matches (≥50%)
- 5 stories need new epics (<50% match)

[STORY-123] "Implement user login" → [EPIC-45] "Authentication System" (75% match)
[STORY-124] "Add payment gateway" → Create new epic (0% match)
```

---

#### `/hygiene.link-initiatives`

Link orphaned epics to initiatives across projects.

**What it does**:
- Finds epics without parent initiative links
- Searches configured initiative projects for matches
- Suggests best matches based on keyword overlap

**Review-then-execute**: Yes  
**Dry-run support**: Via manual review step

**Note**: Requires initiative project mapping in config

---

### Activity & Reporting

#### `/hygiene.activity-summary`

Generate weekly activity summaries for epics/initiatives.

**What it does**:
- Analyzes child items for the past 7 days
- Tracks status transitions, assignments, comments
- Generates business-friendly summary paragraph
- Posts summary as comment on epic/initiative

**Review-then-execute**: Yes (shows summaries before posting)

**Example summary**:
> This week, 3 stories moved to In Progress and 2 were completed. The team made 4 new assignments. Discussion focused on OAuth implementation with 8 comments across 4 stories.

---

#### `/hygiene.show-blocking`

Show all blocking tickets in the project.

**What it does**:
- Queries tickets with "Blocker" priority
- Displays formatted table with status, assignee, age
- Highlights unassigned blockers

**Review-then-execute**: No (read-only report)

---

### Bulk Operations

#### `/hygiene.close-stale`

Close stale tickets based on priority-specific thresholds.

**Default thresholds**:
- Highest/High: 7 days
- Medium: 14 days
- Low/Lowest: 30 days

**Arguments**:
- `--highest <days>` - Override threshold for Highest priority
- `--high <days>` - Override for High priority
- `--medium <days>` - Override for Medium priority
- `--low <days>` - Override for Low priority
- `--lowest <days>` - Override for Lowest priority
- `--dry-run` - Show what would be closed without making changes

**What it does**:
- Finds tickets not updated within threshold
- Groups by priority for review
- Adds closure comment and closes tickets

**Closure message**:
> Due to lack of activity, this item has been closed. If you feel that it should be addressed, please reopen it.

**Review-then-execute**: Yes  
**Dry-run support**: Yes

**Example**:
```bash
# Close stale tickets using defaults
/hygiene.close-stale

# See what would be closed without making changes
/hygiene.close-stale --dry-run

# Use custom thresholds
/hygiene.close-stale --high 14 --medium 30 --low 60
```

---

#### `/hygiene.triage-new`

Suggest triage outcomes for untriaged items.

**What it does**:
- Finds items in "New" status for >1 week
- Analyzes similar triaged items to suggest priority
- Recommends moving to "Backlog" status
- Provides confidence level based on similar item count

**Arguments**:
- `--days <N>` - Override threshold (default: 7)
- `--dry-run` - Show suggestions without making changes

**Review-then-execute**: Yes  
**Dry-run support**: Yes

**Confidence levels**:
- High: ≥5 similar items found
- Medium: 2-4 similar items
- Low: 0-1 similar items (uses default: Medium)

---

### Data Quality

#### `/hygiene.blocking-closed`

Find blocking tickets where all blocked items are closed.

**What it does**:
- Finds tickets with "blocks" issue links
- Checks if all blocked tickets are resolved
- Suggests closing blocker or removing links

**Review-then-execute**: No (manual review required)

**Note**: This is a report-only command because each case requires human judgment.

---

#### `/hygiene.unassigned-progress`

Show tickets in progress without assignee.

**What it does**:
- Finds "In Progress" tickets with no assignee
- Displays formatted table by age
- Groups by reporter for follow-up

**Review-then-execute**: No (read-only report)

---

#### `/hygiene.activity-type`

Suggest Activity Type for tickets missing this field.

**What it does**:
- Finds tickets with empty Activity Type field
- Analyzes summary/description for keywords
- Matches against available Activity Type values
- Suggests best match with confidence level

**Arguments**:
- `--dry-run` - Show suggestions without making changes

**Review-then-execute**: Yes  
**Dry-run support**: Yes

**Keyword mappings**:
- Development: implement, create, add, build, feature
- Bug Fix: fix, bug, error, broken, defect
- Documentation: document, guide, wiki, manual
- Research: investigate, explore, spike, POC
- Testing: test, QA, verify, validate

---

## Output Structure

All artifacts are written to `artifacts/jira-hygiene/`:

```
artifacts/jira-hygiene/
├── config.json                           # Project configuration
├── candidates/                           # Review before bulk ops
│   ├── link-epics.json
│   ├── link-initiatives.json
│   ├── close-stale.json
│   ├── triage-new.json
│   └── activity-type.json
├── summaries/                            # Generated summaries
│   └── {epic-key}-{date}.md
├── reports/                              # Read-only reports
│   ├── blocking-tickets.md
│   ├── blocking-closed-mismatch.md
│   └── unassigned-progress.md
└── operations/                           # Audit logs
    ├── link-epics-{timestamp}.log
    ├── close-stale-{timestamp}.log
    └── ...
```

## Safety Features

### Review-then-Execute Pattern

All bulk operations follow this flow:

1. **Query**: Execute JQL to find candidates
2. **Analyze**: Apply semantic matching or rules
3. **Save**: Write candidates to JSON file
4. **Display**: Show summary of what will change
5. **Confirm**: Ask for explicit approval
6. **Execute**: Make changes only if confirmed
7. **Log**: Write audit log with results

### Dry-Run Mode

Commands that support `--dry-run`:
- `/hygiene.close-stale`
- `/hygiene.triage-new`
- `/hygiene.activity-type`

Dry-run mode shows what **would** happen without making any changes.

### Rate Limiting

All API calls include:
- 0.5s delay between requests (minimum)
- Automatic retry on 429 (rate limit) errors
- Increased delay to 1s after rate limit hit

### Operation Logging

Every bulk operation writes a timestamped log:

```
2026-04-07 10:30:15 - START: Close stale tickets
2026-04-07 10:30:16 - CLOSED: PROJ-100 (Highest priority, 12 days stale)
2026-04-07 10:30:17 - CLOSED: PROJ-101 (High priority, 9 days stale)
2026-04-07 10:30:18 - ERROR: PROJ-102 - Transition failed (permission denied)
2026-04-07 10:30:19 - END: 2 closed, 1 error
```

## Best Practices

### Regular Hygiene Routine

**Weekly**:
- Generate activity summaries for key epics: `/hygiene.activity-summary`
- Check for untriaged items: `/hygiene.triage-new`
- Review blocking tickets: `/hygiene.show-blocking`

**Monthly**:
- Close stale tickets: `/hygiene.close-stale`
- Link orphaned stories: `/hygiene.link-epics`
- Check in-progress items: `/hygiene.unassigned-progress`

**Quarterly**:
- Link orphaned epics to initiatives: `/hygiene.link-initiatives`
- Review blocking-closed mismatches: `/hygiene.blocking-closed`
- Fill in missing activity types: `/hygiene.activity-type`

### Using with Multiple Projects

Run `/hygiene.setup` each time you switch projects. The config file stores the current project context.

### Customizing Thresholds

Adjust staleness thresholds based on your team's velocity:

**Fast-moving team** (releases weekly):
```bash
/hygiene.close-stale --high 3 --medium 7 --low 14
```

**Slower cadence** (releases monthly):
```bash
/hygiene.close-stale --high 14 --medium 30 --low 60
```

## Troubleshooting

### "Authentication failed (401)"

**Cause**: Invalid credentials  
**Solution**:
1. Verify `JIRA_EMAIL` matches your Atlassian account email
2. Regenerate API token at id.atlassian.com
3. Check `JIRA_URL` format (must start with https://)

### "Field not found" errors

**Cause**: Custom field names vary by project  
**Solution**:
1. Run `/hygiene.setup` to fetch field metadata
2. Check field names in Jira (Admin → Issues → Custom Fields)
3. If "Epic Link" or "Parent Link" are named differently, update JQL

### "Rate limit exceeded (429)"

**Cause**: Too many requests  
**Solution**:
- Workflow automatically retries with increased delay
- For large operations, work in smaller batches
- Jira Cloud typically allows 10 requests/second

### "No transition available"

**Cause**: Status workflow restrictions  
**Solution**:
- Check Jira workflow for allowed transitions
- Some tickets may require intermediate states
- Logs will note which tickets couldn't be transitioned

## Contributing

To modify or extend this workflow:

1. Read `CLAUDE.md` for safety rules and principles
2. Update command files in `.claude/commands/`
3. Test with `--dry-run` flags before live operations
4. Update this README with any new commands or features

## Support

For issues or feature requests:
- File an issue in the repository
- Include operation logs from `artifacts/jira-hygiene/operations/`
- Provide example JQL queries that aren't working

## License

Part of the Ambient Code Workflows repository. See main repository LICENSE.
