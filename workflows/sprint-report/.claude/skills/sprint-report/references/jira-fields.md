# Jira Fields for Sprint Reports

Custom field IDs vary by Jira instance. This document describes the fields
the sprint report needs, how to discover their IDs, and provides known
examples from Red Hat's Jira (redhat.atlassian.net).

## Discovery Process

Custom fields have opaque IDs like `customfield_10028` that differ across
instances. You must discover the correct IDs at runtime.

### Option A: Search by Name

```
jira_search_fields("story point")
jira_search_fields("sprint")
jira_search_fields("epic")
```

Look at the `name` and `description` in results to match the right field.

### Option B: Inspect a Real Issue

Fetch one issue with all fields and look for recognizable values:

```
jira_search("project = X AND sprint in openSprints() ORDER BY created DESC", maxResults=1, fields="*all")
```

Scan the response for:

- A **float** value (e.g., `3.0`, `5.0`) — that's likely story points
- A **JSON object** with `name`, `state`, `startDate` — that's the sprint field
- A **key reference** like `PROJ-123` — that's likely an epic link

Record the `customfield_XXXXX` key for each and use it in all subsequent queries.

## Custom Fields Needed

### Story Points

- **What to search for:** "story point", "story points", "points"
- **Type:** Float (e.g., `1.0`, `3.0`, `8.0`). Found on Stories, Tasks,
  Bugs, sometimes Epics.
- **Variants:** Some organizations split estimates by role (DEV points, QE
  points, DOC points). If the primary story points field is empty, search for
  role-specific variants.

### Sprint

- **What to search for:** "sprint"
- **Type:** Array of JSON objects with `name`, `state` (active/closed/future),
  `startDate`, `endDate`, `completeDate`

### Epic Link

- **What to search for:** "epic link"
- **Type:** Key reference (e.g., `PROJ-123`)

### Epic Name

- **What to search for:** "epic name", "epic label"
- **Type:** String. Short display name shown on boards.

### Team

- **What to search for:** "team"
- **Type:** Team object with `name`, `id`, `isShared`. Identifies the
  Atlassian team assigned to the issue.

### Target Version

- **What to search for:** "target version"
- **Type:** Multi-version array (e.g., `["rhoai-3.4"]`). Tracks which
  product release the work targets.

## Known Fields: Red Hat Jira (redhat.atlassian.net)

These are the confirmed custom field IDs on the Red Hat Jira instance. Other
instances will have different IDs — always verify via discovery.

| Field | ID | Type | Notes |
| --- | --- | --- | --- |
| Story Points | `customfield_10028` | Float | Primary story points field |
| Story point estimate | `customfield_10016` | Float | GreenHopper/JSW native estimate field |
| DEV Story Points | `customfield_10506` | Float | Developer-specific estimate |
| QE Story Points | `customfield_10572` | Float | QA-specific estimate |
| DOC Story Points | `customfield_10510` | Float | Documentation-specific estimate |
| Original story points | `customfield_10977` | Float | Snapshot of initial estimate |
| Sprint | `customfield_10020` | Sprint JSON array | GreenHopper sprint field |
| sprint_count | `customfield_10975` | Float | Number of sprints an item has been in |
| Epic Link | `customfield_10014` | Key reference | Links issue to parent epic |
| Epic Name | `customfield_10011` | String | Short epic label for boards |
| Epic Status | `customfield_10012` | String | "To Do", "In Progress", "Done" |
| Team | `customfield_10001` | Team object | Atlassian team (e.g., `"AgentOps [RAG + Vector DB]"`) |
| Target Version | `customfield_10855` | Multi-version | Product release (e.g., `["rhoai-3.4"]`) |
| Target end | `customfield_10024` | Date | Roadmap target end date |
| Rank | `customfield_10019` | Lexo-rank | Board ordering (internal use) |
| Epic Type | `customfield_10573` | Select | Classification of epic |
| Cross Team Epic | `customfield_10549` | Radio | Whether epic spans teams |

### Story Points Strategy for Red Hat Jira

Check fields in this order:

1. `customfield_10028` ("Story Points") — most commonly used
2. `customfield_10016` ("Story point estimate") — GreenHopper native
3. If both are null, check role-specific fields:
   `customfield_10506` (DEV), `customfield_10572` (QE), `customfield_10510` (DOC)
4. If all are null, the item is unestimated — use item-count fallback metrics

### Issue Hierarchy on Red Hat Jira

```
Feature (hierarchy level 2)  — RHAISTRAT project, via parent field
  └── Epic (hierarchy level 1)  — via parent field or Epic Link
        └── Story / Task / Bug (hierarchy level 0)
```

Items reference their parent via the `parent` field (preferred) or
`customfield_10014` (Epic Link, legacy). The `parent` response includes
the parent's summary, status, priority, and issue type.

## Standard Fields (Always Available)

These don't require custom field discovery:

| Field | Jira Key | Type |
| --- | --- | --- |
| Summary | `summary` | String |
| Status | `status` | Workflow status object |
| Assignee | `assignee` | User object |
| Priority | `priority` | Select (Blocker, Critical, Major, Normal, Minor) |
| Issue Type | `issuetype` | Select (Epic, Story, Task, Bug, etc.) |
| Created | `created` | Datetime |
| Updated | `updated` | Datetime |
| Resolution Date | `resolutiondate` | Datetime (null if unresolved) |
| Components | `components` | Multi-select |
| Fix Version | `fixVersions` | Multi-version |
| Description | `description` | Text (check here for acceptance criteria) |
| Comments | `comment` | Comment list |

## Workflow Statuses

Status names and classifications vary by project. Common patterns:

### Engineering Projects (Stories/Tasks/Bugs)

```
New → Backlog → To Do → In Progress → Review → Done / Closed
```

| Classification | Typical Statuses |
| --- | --- |
| Not Started | New, Backlog, To Do, Open |
| In Progress | In Progress, In Development, Coding |
| In Review | Review, Code Review, In Review, QA |
| Done | Done, Closed, Resolved, Release Pending |

### What "Review" Means

"Review" can mean different things depending on the team:

- **Code review** — PR is open, waiting for reviewer
- **QA review** — testing in progress
- **Stakeholder review** — waiting for approval

If >40% of items are in Review, flag it as a flow bottleneck and recommend
the team investigate which type of review is the queue.

## Acceptance Criteria Detection

There is no standard Jira field for acceptance criteria. Teams typically put
them in the `description` field. Look for patterns:

- Heading: `## Acceptance Criteria`, `### AC`, `**Acceptance Criteria**`
- Checkbox lists: `- [ ] ...` or `* [ ] ...`
- Numbered criteria: `AC1:`, `AC2:`, etc.

If none of these patterns are found in the description, count the item as
having no acceptance criteria.
