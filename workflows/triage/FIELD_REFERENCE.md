# Triage Workflow Field Reference

This document describes all available fields and configuration options for the triage workflow.

## Workflow Configuration (.ambient/ambient.json)

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name of the workflow |
| `description` | string | Yes | Brief description of what the workflow does |
| `systemPrompt` | string | Yes | Instructions for the AI assistant on how to execute the workflow |
| `startupPrompt` | string | No | Welcome message shown when the workflow starts |
| `results` | object | No | Map of result categories to file path patterns |

### Results Configuration

The `results` object maps human-readable names to file path patterns where outputs will be generated:

```json
{
  "results": {
    "Triage Report": "artifacts/triage/triage-report.md",
    "Interactive Report": "artifacts/triage/report.html",
    "Operations Script": "artifacts/triage/operations.json"
  }
}
```

## Issue Data Model

Each triaged issue contains the following fields:

### Core Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `number` | integer | GitHub/Jira issue number | `1234` |
| `title` | string | Issue title | `Fix authentication bug` |
| `url` | string | Link to the issue | `https://github.com/owner/repo/issues/1234` |
| `status` | string | Current issue status | `open`, `closed` |

### Classification Fields

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `type` | string | Issue type | `bug`, `feature`, `enhancement`, `documentation` |
| `priority` | string | Priority level | `critical`, `high`, `medium`, `low` |
| `recommendation` | string | Triage recommendation | See Recommendations section |
| `reason` | string | Explanation for recommendation | Free text |

### Tracking Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `lastModifiedBy` | string | GitHub username who last updated | `octocat` |
| `lastModifiedDate` | string | ISO 8601 timestamp | `2026-01-19T12:34:56Z` |
| `waitingOn` | string | Who/what is blocking progress | `username`, `more info`, `-` |
| `nextAction` | string | Recommended next step | `Close as duplicate of #1234` |

## Recommendations

### Available Recommendation Types

| Recommendation | Badge Color | Description | Next Action |
|----------------|-------------|-------------|-------------|
| `CLOSE` | Red | Invalid, obsolete, or resolved | Close the issue with explanation |
| `FIX_NOW` | Yellow | Critical or quick win | Prioritize for immediate work |
| `BACKLOG` | Blue | Valid for future work | Add to backlog, deprioritize |
| `NEEDS_INFO` | Pink | Blocked on information | Request clarification from reporter |
| `DUPLICATE` | Gray | Duplicate of existing issue | Link to original and close |
| `AMBER_AUTO` | Green | Can be automated | Tag for Amber auto-fix |
| `ASSIGN` | Purple | Ready for assignment | Assign to developer |
| `WONT_FIX` | Gray | Valid but won't address | Close with explanation |

### Recommendation Logic

The AI considers:
- **Age**: How long has the issue been open?
- **Activity**: Recent comments or updates?
- **Labels**: Existing priority/type labels
- **Assignees**: Currently assigned?
- **Duplicates**: Similar to other issues?
- **Feasibility**: Can Amber automate it?
- **Impact**: How many users affected?
- **Complexity**: Simple fix vs major feature?

## HTML Template Placeholders

The HTML template (`templates/report.html`) supports these placeholders:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{REPO_URL}` | Repository URL | `https://github.com/owner/repo` |
| `{REPO_NAME}` | Repository name | `owner/repo` |
| `{DATE}` | Generation date | `2026-01-19` |
| `{TOTAL_ISSUES}` | Total issue count | `62` |
| `{CLOSE_COUNT}` | Issues recommended to close | `5` |
| `{FIX_NOW_COUNT}` | Issues to fix now | `28` |
| `{BACKLOG_COUNT}` | Issues for backlog | `25` |
| `{NEEDS_INFO_COUNT}` | Issues needing info | `4` |
| `{AMBER_AUTO_COUNT}` | Issues for automation | `0` |
| `{ASSIGN_COUNT}` | Issues to assign | `0` |
| `{ISSUES_JSON}` | JSON array of all issues | `[{...}, {...}]` |
| `{TABLE_ROWS}` | Pre-rendered table rows (optional) | `<tr>...</tr>` |

## Bulk Operations Format

Operations JSON format for `scripts/bulk-operations.sh`:

```json
[
  {
    "issue": 1234,
    "action": "CLOSE",
    "params": {
      "reason": "Duplicate of #5678"
    }
  },
  {
    "issue": 5678,
    "action": "ADD_LABEL",
    "params": {
      "labels": ["priority:high", "bug"]
    }
  }
]
```

### Available Actions

| Action | Params | Description |
|--------|--------|-------------|
| `CLOSE` | `reason` | Close issue with comment |
| `ADD_LABEL` | `labels` (array) | Add one or more labels |
| `REMOVE_LABEL` | `labels` (array) | Remove one or more labels |
| `ASSIGN` | `assignee` | Assign to user |
| `UNASSIGN` | `assignee` | Unassign from user |
| `COMMENT` | `body` | Add comment |
| `LINK_DUPLICATE` | `original` | Link as duplicate and close |

## GitHub Actions Configuration

### Workflow Triggers

```yaml
on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly on 1st at 00:00 UTC
  workflow_dispatch:      # Manual trigger
    inputs:
      repository:         # Optional: override repo
        description: 'Repository to triage (owner/repo format)'
        required: false
```

### Workflow Outputs

| Artifact | Description | Retention |
|----------|-------------|-----------|
| `triage-report-{run_number}` | ZIP with all reports | 90 days |

Contents:
- `report.html` - Interactive dashboard
- `triage-report.md` - Markdown report
- `triaged_issues.json` - Raw JSON data

## Customization Examples

### Add New Recommendation Type

1. Update `.ambient/ambient.json` systemPrompt
2. Add badge style to `templates/report.html`:
```css
.badge-my-new-type {
  background: #color;
  color: #text-color;
}
```
3. Add stat card (if needed)
4. Update operation generation logic

### Change Sort Order

Edit `templates/report.html`:
```javascript
// Default sort
let currentSort = { field: 'priority', direction: 'desc' };
```

### Add Custom Filter

Edit `templates/report.html`:
```html
<span class="filter-label">Custom:</span>
<select id="filter-custom">
  <option value="">All</option>
  <option value="value1">Value 1</option>
</select>
```

Then add filter logic in JavaScript.

## Best Practices

### Triage Recommendations
- Be specific in reason field
- Include issue numbers when referencing duplicates
- Provide actionable next steps
- Consider team capacity when recommending FIX_NOW

### Bulk Operations
- Always test with `--dry-run` first
- Review generated operations JSON before executing
- Use rate limiting (`--rate-limit`) for large batches
- Back up issue data before bulk changes

### Template Customization
- Keep templates self-contained (no external dependencies)
- Test UI changes in multiple browsers
- Maintain accessibility (keyboard navigation, screen readers)
- Document custom fields in this file

## Troubleshooting

### Common Issues

**Sorting doesn't work**
- Ensure field names match between data and sort handler
- Check for null/undefined values
- Verify JavaScript console for errors

**Simulation mode stuck**
- Clear `simulated` property: `issues.forEach(i => i.simulated = false)`
- Refresh the page
- Check browser console

**Operations fail**
- Verify GitHub token has correct permissions
- Check rate limiting
- Ensure issue numbers are valid
- Review operation JSON syntax

## Further Reading

- [GitHub Issues API](https://docs.github.com/en/rest/issues)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Ambient Workflows](https://github.com/ambient-code/workflows)
