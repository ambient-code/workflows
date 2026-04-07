# /hygiene.triage-new - Suggest Triage for Untriaged Items

## Purpose

Find items in "New" status for more than 1 week and suggest triage outcomes (priority and move to backlog) based on analysis of similar items in the project.

## Prerequisites

- `/hygiene.setup` must be run first

## Arguments

Optional:
- `--days <N>` - Threshold for untriaged items (default: 7 days)
- `--dry-run` - Show suggestions without making changes

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key

2. **Query untriaged items**:
   ```jql
   project = {PROJECT} AND status = New AND created < -{DAYS}d AND resolution = Unresolved
   ```
   - Fetch: key, summary, description, issuetype, created
   - If none found: report success and exit

3. **For each untriaged item**:
   
   a. **Extract keywords**:
      - Combine summary + description
      - Remove stopwords
   
   b. **Find similar items**:
      ```jql
      project = {PROJECT} AND resolution = Unresolved AND text ~ "keyword1 keyword2" AND status != New
      ```
      - Find items that have been triaged (not in New status)
      - Fetch: priority, status
   
   c. **Analyze priority distribution**:
      - Count priorities of similar items: {High: 5, Medium: 8, Low: 2}
      - Suggest most common priority (Medium in this case)
      - If no similar items found: suggest "Medium" as default
   
   d. **Suggest triage outcome**:
      - Recommended priority: Most common among similar items
      - Recommended action: Move to "Backlog" status
      - Confidence: High if ≥5 similar items, Medium if 2-4, Low if 0-1

4. **Write candidates file**:
   - Save to `artifacts/jira-hygiene/candidates/triage-new.json`
   - Include: key, summary, suggested priority, confidence, similar item count

5. **Display summary**:
   ```
   Found N untriaged items (>7 days):
   
   High confidence (≥5 similar items): 8 items
     PROJ-200 "Add export feature" → Priority: Medium (based on 8 similar items)
     PROJ-201 "Fix broken link" → Priority: Low (based on 6 similar items)
   
   Medium confidence (2-4 similar): 3 items
     PROJ-202 "Improve performance" → Priority: High (based on 3 similar items)
   
   Low confidence (0-1 similar): 2 items
     PROJ-203 "New integration request" → Priority: Medium (default, no similar items)
   ```

6. **Ask for confirmation**:
   - If `--dry-run`: Skip, display "DRY RUN - No changes made"
   - Otherwise prompt: "Apply triage suggestions? (yes/no/high-confidence-only)"
   - "high-confidence-only": Only apply suggestions with ≥5 similar items

7. **Execute triage**:
   - For each approved item:
     - Update priority via PUT `/rest/api/3/issue/{key}`
     - Transition to "Backlog" status
     - Add comment: "Auto-triaged based on similar items. Priority set to {PRIORITY}."
     - Rate limit: 0.5s between items

8. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/triage-new-{timestamp}.log`

## Output

- `artifacts/jira-hygiene/candidates/triage-new.json`
- `artifacts/jira-hygiene/operations/triage-new-{timestamp}.log`

## Example Candidates JSON

```json
[
  {
    "key": "PROJ-200",
    "summary": "Add CSV export feature for reports",
    "keywords": ["export", "csv", "reports", "feature"],
    "suggested_priority": "Medium",
    "confidence": "high",
    "similar_items_found": 8,
    "priority_distribution": {
      "High": 2,
      "Medium": 5,
      "Low": 1
    },
    "days_untriaged": 10,
    "current_status": "New"
  },
  {
    "key": "PROJ-203",
    "summary": "Integration with new CRM system",
    "keywords": ["integration", "crm", "system"],
    "suggested_priority": "Medium",
    "confidence": "low",
    "similar_items_found": 0,
    "priority_distribution": {},
    "days_untriaged": 15,
    "current_status": "New",
    "note": "No similar items found, using default priority"
  }
]
```

## Priority Suggestion Logic

1. **Find similar items**: Search by keywords, exclude items still in "New"
2. **Count priority distribution**: Tally priorities of similar items
3. **Suggest most common**: Pick priority with highest count
4. **Confidence levels**:
   - High: ≥5 similar items found
   - Medium: 2-4 similar items
   - Low: 0-1 similar items (use default: Medium)

## Default Backlog Status

Most Jira projects use "Backlog" status, but some may use:
- "To Do"
- "Open"
- "Ready for Development"

The workflow will:
1. Try "Backlog" first
2. If transition fails, try "To Do"
3. If still fails, log warning and skip status change (only update priority)

## Error Handling

- **No "Backlog" status**: Try alternative statuses, log which was used
- **Priority update failed**: Some projects have restricted priority changes; log error
- **Similar items query too broad**: If >100 results, limit to top 50 by updated date
