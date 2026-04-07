# /hygiene.activity-summary - Generate Weekly Activity Summaries

## Purpose

Generate weekly activity summaries for selected epics and initiatives by analyzing changes and comments on child items from the past 7 days, then post summaries as comments.

## Prerequisites

- `/hygiene.setup` must be run first
- User should specify which epics/initiatives to summarize

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key

2. **Prompt for selection**:
   - Ask user which epics/initiatives to summarize
   - Options:
     - Provide specific issue keys (comma-separated)
     - Provide JQL filter (e.g., "project = PROJ AND issuetype = Epic")
     - Use "all active epics" (default: all unresolved epics in project)

3. **Fetch selected epics/initiatives**:
   - Execute JQL query to get target issues
   - Fetch: key, summary, issuetype

4. **For each epic/initiative**:
   
   a. **Fetch child issues**:
      ```jql
      parent = {EPIC_KEY} AND resolution = Unresolved
      ```
      - Get all child stories/tasks
   
   b. **Analyze activity for each child** (past 7 days):
      - Fetch changelog: GET `/rest/api/3/issue/{childKey}/changelog`
      - Filter changes where created >= (now - 7 days)
      - Extract:
        - Status transitions (e.g., "New" → "In Progress")
        - Assignee changes
        - Priority changes
      - Fetch comments: GET `/rest/api/3/issue/{childKey}/comment`
      - Count comments from past 7 days
   
   c. **Generate summary paragraph**:
      - Template: "This week, {status_summary}. {assignment_summary}. {activity_summary}."
      - Status summary: "X stories moved to In Progress, Y completed"
      - Assignment summary: "Z new assignments" (if any)
      - Activity summary: "N comments across M stories" (if significant)
      - Keep to 2-4 sentences, business-friendly language
   
   d. **Write summary to file**:
      - Save to `artifacts/jira-hygiene/summaries/{epic-key}-{date}.md`
      - Include metadata: epic key, date range, child count

5. **Display all summaries**:
   - Show generated summaries for review
   - Format as markdown with epic key as header

6. **Ask for confirmation**:
   - Prompt: "Post these summaries as comments? (yes/no)"
   - Allow user to edit summaries before posting

7. **Post summaries**:
   - For each epic/initiative:
     - POST `/rest/api/3/issue/{epicKey}/comment`
     - Body: `{"body": "Weekly Activity Summary (YYYY-MM-DD):\n\n{summary_text}"}`
     - Rate limit: 0.5s between requests

8. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/activity-summary-{timestamp}.log`

## Output

- `artifacts/jira-hygiene/summaries/{epic-key}-{date}.md` (one file per epic)
- `artifacts/jira-hygiene/operations/activity-summary-{timestamp}.log`

## Example Summary

**EPIC-45-2026-04-07.md**:
```markdown
# Weekly Activity Summary: EPIC-45 Authentication System
**Date Range**: 2026-03-31 to 2026-04-07  
**Child Issues**: 8 stories

## Summary

This week, 3 stories moved to In Progress and 2 were completed. The team made 4 new assignments across the authentication work. There were 12 comments discussing API integration challenges and OAuth implementation details.

## Activity Breakdown

- Status transitions: 5 changes
  - New → In Progress: STORY-101, STORY-102, STORY-103
  - In Progress → Done: STORY-98, STORY-99
- Assignments: 4 new
- Comments: 12 across 6 stories
```

## Summary Generation Guidelines

**Good summary**:
> "This week, 3 stories moved to In Progress and 2 were completed. The team made 4 new assignments. Discussion focused on OAuth implementation with 8 comments across 4 stories."

**Bad summary** (too technical):
> "This week, STORY-101 transitioned from status ID 10001 to 10002. User john.doe was assigned to STORY-102..."

**Focus on**:
- High-level progress (stories moved, completed)
- Team activity (assignments, discussions)
- Notable trends (if detectable)

**Avoid**:
- Listing every ticket key
- Technical jargon
- Implementation details

## Error Handling

- **No child issues**: Note "No active child issues" in summary
- **No activity**: "No significant activity this week"
- **Changelog unavailable**: Fall back to issue update dates
- **Comment fetch failed**: Skip comment count, note in log
