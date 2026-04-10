# Jira Query Patterns for Sprint Reports

## Sprint Discovery

### Step 1: Find the Board

```
jira_get_agile_boards(project_key="PROJ")
jira_get_agile_boards(board_name="Team Name")
```

If the user provides a component name instead of a project, search boards by
the project that contains that component.

### Step 2: Find the Active Sprint

```
jira_get_sprints_from_board(board_id=BOARD_ID, state="active")
```

This returns sprint objects with `id`, `name`, `startDate`, `endDate`, `goal`.

- If multiple active sprints: ask the user which one
- If no active sprints: offer the most recently closed sprint instead

### Step 3: Get Sprint Issues

**Use `jira_get_sprint_issues` with an explicit field list:**

```
jira_get_sprint_issues(
    sprint_id=SPRINT_ID,
    fields="summary,status,issuetype,priority,assignee,created,updated,resolutiondate,components,description,customfield_XXXXX,customfield_YYYYY"
)
```

Replace `customfield_XXXXX` and `customfield_YYYYY` with the story points and
sprint field IDs discovered from `references/jira-fields.md`.

**DO NOT use `fields=*all`.** This returns 100+ custom fields per issue and
can produce 500k+ characters for a typical sprint, exceeding tool output
limits. Explicit field lists keep responses under 50k characters.

### Alternative: JQL-Based Query

If sprint-specific APIs aren't available, use JQL:

```
jira_search(
    jql='sprint = SPRINT_ID ORDER BY status ASC',
    fields="summary,status,issuetype,priority,assignee,created,updated,resolutiondate,description,customfield_XXXXX",
    maxResults=100
)
```

Or query by component for teams that don't use sprint boards:

```
jira_search(
    jql='component = "Team Component" AND sprint in openSprints() ORDER BY status ASC',
    fields="...",
    maxResults=100
)
```

## Cycle Time & Status Transitions

Use specialized tools instead of computing cycle time from raw dates:

### jira_get_issue_sla

Returns pre-computed cycle time, lead time, and time-in-status breakdowns.

```
jira_get_issue_sla(issue_key="KEY-1")
```

Best for resolved items where you need accurate cycle time.

### jira_get_issue_dates

Returns status transition history (timestamps for each status change).

```
jira_get_issue_dates(issue_key="KEY-1")
```

Use this for WIP aging (how long an item has been in its current status)
and for computing cycle time manually when SLA data isn't available.

Batch calls for the top 10–15 items rather than every sprint item.

## Changelog Data

Changelogs add significant payload. Do NOT include `expand=changelog` on
the main sprint query — fetch changelogs separately for targeted items.

### Preferred: jira_batch_get_changelogs

Fetches changelogs for multiple issues in one call (Cloud only):

```
jira_batch_get_changelogs(issue_keys=["KEY-1", "KEY-2", "KEY-3"])
```

Use this for the top 10–15 highest-risk items (oldest, blocked, carryover).

### Fallback: jira_search with expand

If the batch tool is unavailable:

```
jira_search(
    jql='key in (KEY-1, KEY-2, KEY-3, ...)',
    fields="summary,status",
    expand="changelog"
)
```

### What to Extract from Changelogs

| Pattern | What to Look For |
| --- | --- |
| Item repurposing | `summary` or `description` field changed mid-sprint |
| Reassignment | `assignee` field changed |
| Status churn | Item moved backward (e.g., Review → In Progress) |
| Sprint hopping | `Sprint` field changed (item added/removed mid-sprint) |
| Hidden work | No status transitions since item was added to sprint |

## Historical Sprint Data

For trend analysis across multiple sprints:

```
jira_get_sprints_from_board(board_id=BOARD_ID, state="closed")
```

This returns recent closed sprints. For each, query issues the same way as
the active sprint. Calculate per-sprint metrics to build trend data:

- Velocity (points or items completed)
- Completion rate
- Carryover count
- Scope change percentage

Limit to 3-5 previous sprints to keep the analysis manageable.

## Common JQL Patterns

```sql
-- Active sprint items for a project
project = PROJ AND sprint in openSprints()

-- Active sprint items for a specific component
component = "Component Name" AND sprint in openSprints()

-- Items carried over from previous sprints (still open, assigned to closed sprints)
project = PROJ AND sprint in closedSprints() AND statusCategory != Done

-- Unestimated items in current sprint
sprint = SPRINT_ID AND cf[STORY_POINTS_ID] is EMPTY

-- Items without acceptance criteria (approximate — checks description length)
sprint = SPRINT_ID AND description is EMPTY
```

## Tools to Avoid

| Tool | Why |
| --- | --- |
| `jira_get_all_projects` | Returns 1.9M+ chars. Never needed — use `jira_get_agile_boards` with the board/project/component name the user gave you. |
| `fields=*all` on sprint queries | Returns 100+ custom fields per issue. Use explicit field lists. |
| `expand=changelog` on sprint queries | Bloats responses. Use `jira_batch_get_changelogs` separately for targeted items. |

## Data Volume Guidelines

| Query Type | Typical Size | Notes |
| --- | --- | --- |
| 20 issues, explicit fields | 10-30k chars | Ideal |
| 20 issues, `fields=*all` | 300-600k chars | Avoid |
| `jira_batch_get_changelogs` (10 items) | 20-50k chars | Targeted |
| `jira_get_issue_sla` (10 items) | 5-15k chars | Lightweight |
| 20 issues, `fields=*all` + changelog | 500k-1M chars | Never do this |
| `jira_get_all_projects` | 1.9M chars | Never do this |

If the response exceeds tool output limits (~25k tokens), save to a file and
parse with `jq` or read in chunks.
