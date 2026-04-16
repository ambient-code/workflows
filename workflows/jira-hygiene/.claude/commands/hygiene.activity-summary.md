# /hygiene.activity-summary - Generate Weekly Activity Summaries

## Purpose

Generate weekly activity summaries for selected epics and initiatives by analyzing changes and comments on child items from the past 7 days, then post summaries as comments.

## Prerequisites

- `/hygiene.setup` must be run first
- User should specify which epics/initiatives to summarize

**Optional** (for enhanced PR/MR summaries):
- `GITHUB_TOKEN` - For direct GitHub API access if Jira integration unavailable
- `GITLAB_TOKEN` - For direct GitLab API access if Jira integration unavailable

## Arguments

Optional:
- `--dry-run` - Show summaries without posting them as comments (runs steps 1-4 only)

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
   - **Always enforce unresolved scope**: Append "AND resolution = Unresolved" to any user-provided JQL

3. **Fetch selected epics/initiatives WITH PAGINATION**:
   - Execute JQL query to get target issues
   - **If user provided specific keys**: Fetch each key and filter to only include issues where `fields.resolution == null`
   - **If user provided JQL**: Already enforced "AND resolution = Unresolved" in step 2
   
   **Pagination logic** (if using JQL filter):
   ```
   all_epics = []
   start_at = 0
   max_results = 50
   
   Loop:
     response = GET /rest/api/3/search?jql={user_jql}&startAt={start_at}&maxResults={max_results}&fields=key,summary,issuetype
     epics = response['issues']
     all_epics.extend(epics)
     
     Print: "Fetched {start_at + len(epics)}/{response['total']} epics/initiatives..."
     
     if start_at + len(epics) >= response['total']:
       break  # All results fetched
     
     start_at += max_results
     sleep(0.5)  # Rate limit
   ```
   
   - Fetch: key, summary, issuetype

4. **For each epic/initiative**:
   
   a. **Fetch child issues WITH PAGINATION** (logic varies by issue type):
      
      **If issue type is Initiative**:
      1. First fetch child Epics:
         ```jql
         parent = {INITIATIVE_KEY} AND resolution = Unresolved
         ```
         Use pagination (max 50 per page) to fetch all child epics
      
      2. Then for each child Epic, fetch its child issues:
         ```jql
         parent = {EPIC_KEY} AND resolution = Unresolved
         ```
         Use pagination for each epic's children
      
      **If issue type is Epic**:
      - Directly fetch child issues:
        ```jql
        parent = {EPIC_KEY} AND resolution = Unresolved
        ```
        Use pagination to fetch all children
      
      **Note**: Child queries do NOT use base_jql (children can cross project boundaries)
      
      **Pagination logic** (apply to both Initiative→Epics and Epic→Children):
      ```
      all_children = []
      start_at = 0
      max_results = 50
      
      Loop:
        response = GET /rest/api/3/search?jql={child_jql}&startAt={start_at}&maxResults={max_results}
        children = response['issues']
        all_children.extend(children)
        
        Print: "Fetched {len(all_children)}/{response['total']} children for {PARENT_KEY}..."
        
        if start_at + len(children) >= response['total']:
          break
        
        start_at += max_results
        sleep(0.5)  # Rate limit
      ```
      
      - Get all child items (not limited to 50)
      - Then analyze activity for ALL children across all levels
   
   b. **Analyze activity for each child** (past 7 days):
      - Fetch changelog: GET `/rest/api/3/issue/{childKey}/changelog`
      - Filter changes where created >= (now - 7 days)
      - Extract:
        - Status transitions (e.g., "New" → "In Progress")
        - Assignee changes
        - Priority changes
      - Fetch comments: GET `/rest/api/3/issue/{childKey}/comment`
      - Count comments from past 7 days
      
      **Also check for linked MRs/PRs**:
      - Fetch development info: GET `/rest/dev-status/1.0/issue/detail?issueId={issueId}&applicationType=github&dataType=pullrequest`
      - Also check GitLab: `applicationType=gitlab&dataType=mergerequest`
      - Parse PR/MR URLs from comments and description
      - For each linked PR/MR with activity in past 7 days:
        - Fetch PR details from GitHub/GitLab API
        - Extract: status (open/merged/closed), commits added, reviews, last updated
        - Note: PR/MR must have `updated_at` within past 7 days to include
   
   c. **Generate summary paragraph**:
      - Template: "This week, {status_summary}. {pr_summary}. {assignment_summary}. {activity_summary}."
      - Status summary: "X stories moved to In Progress, Y completed"
      - PR/MR summary: "Z pull requests merged, N in review" (if any PR/MR activity)
      - Assignment summary: "M new assignments" (if any)
      - Activity summary: "P comments across Q stories" (if significant)
      - Keep to 3-5 sentences, business-friendly language
      - Prioritize PR/MR activity in summary (shows concrete progress)
   
   d. **Write summary to file**:
      - Save to `artifacts/jira-hygiene/summaries/{epic-key}-{date}.md`
      - Include metadata: epic key, date range, child count

5. **Display all summaries**:
   - Show generated summaries for review
   - Format as markdown with epic key as header

6. **Ask for confirmation**:
   - If `--dry-run`: Display "DRY RUN - Summaries generated but not posted" and skip to step 8
   - Otherwise prompt: "Post these summaries as comments? (yes/no)"
   - Allow user to edit summaries before posting

7. **Post summaries** (skip if --dry-run):
   - For each epic/initiative:
     - POST `/rest/api/3/issue/{epicKey}/comment`
     - Body: `{"body": "Weekly Activity Summary (YYYY-MM-DD):\n\n{summary_text}"}`
     - Rate limit: 0.5s between requests

8. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/activity-summary-{timestamp}.log`
   - In --dry-run mode, log "DRY RUN - no comments posted"

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

This week, 3 stories moved to In Progress and 2 were completed. The team merged 2 pull requests and has 3 PRs in active review. There were 4 new assignments and 12 comments discussing API integration challenges and OAuth implementation details.

## Activity Breakdown

- Status transitions: 5 changes
  - New → In Progress: STORY-101, STORY-102, STORY-103
  - In Progress → Done: STORY-98, STORY-99
- Pull Requests: 5 active
  - Merged: PR#145 (OAuth integration), PR#148 (Token refresh)
  - In Review: PR#150 (SSO support), PR#151 (Session management), PR#152 (Password reset)
  - Commits this week: 18 commits across 5 PRs
- Assignments: 4 new
- Comments: 12 across 6 stories
```

## Summary Generation Guidelines

**Good summary**:
> "This week, 3 stories moved to In Progress and 2 were completed. The team merged 2 pull requests for OAuth integration and has 3 PRs in active review. There were 4 new assignments and 8 comments focused on implementation details."

**Bad summary** (too technical):
> "This week, STORY-101 transitioned from status ID 10001 to 10002. User john.doe was assigned to STORY-102. Commit SHA abc123 was pushed to PR #145..."

**Focus on**:
- High-level progress (stories moved, completed)
- PR/MR activity (merged, in review, commit volume)
- Team activity (assignments, discussions)
- Notable trends (if detectable)

**Avoid**:
- Listing every ticket key
- Commit SHAs or technical identifiers
- Implementation details
- Individual developer names (use "the team")

**PR/MR Details to Include**:
- Number merged vs in review
- PR titles (if descriptive, e.g., "OAuth integration")
- Significant milestones (e.g., "first PR merged this epic")
- Overall commit volume (e.g., "18 commits this week")

**PR/MR Details to Exclude**:
- Commit messages
- Code review comments
- Individual file changes
- Specific reviewers

## Error Handling

- **No child issues**: Note "No active child issues" in summary
- **No activity**: "No significant activity this week"
- **Changelog unavailable**: Fall back to issue update dates
- **Comment fetch failed**: Skip comment count, note in log
- **Development info unavailable**: Not all Jira instances have GitHub/GitLab integration; skip PR/MR section
- **PR/MR API access denied**: May need GitHub/GitLab tokens; proceed without PR/MR data

## GitHub/GitLab Integration

### Jira Development Panel API

**Endpoint**: `/rest/dev-status/1.0/issue/detail?issueId={issueId}&applicationType={type}&dataType={dataType}`

**Supported integrations**:
- GitHub: `applicationType=github&dataType=pullrequest`
- GitLab: `applicationType=gitlab&dataType=mergerequest`
- Bitbucket: `applicationType=bitbucket&dataType=pullrequest`

**Response includes**:
- PR/MR URLs
- Status (open, merged, closed)
- Last updated timestamp
- Review status

### GitHub API (if direct access needed)

**Environment variables** (optional):
- `GITHUB_TOKEN` - GitHub personal access token
- `GITHUB_API_URL` - Default: https://api.github.com

**Endpoint**: `GET /repos/{owner}/{repo}/pulls/{number}`

**Fetch**:
- `state` (open, closed)
- `merged_at` (if merged)
- `updated_at` (filter by this)
- `commits` count
- `additions`, `deletions` (code churn)
- `reviews` count

### GitLab API (if direct access needed)

**Environment variables** (optional):
- `GITLAB_TOKEN` - GitLab personal access token
- `GITLAB_API_URL` - Default: https://gitlab.com/api/v4

**Endpoint**: `GET /projects/{id}/merge_requests/{iid}`

**Fetch**:
- `state` (opened, merged, closed)
- `merged_at` (if merged)
- `updated_at` (filter by this)
- `user_notes_count` (comments)

### Date Filtering

Only include PR/MR in summary if:
- `updated_at` >= (now - 7 days)
- OR `merged_at` >= (now - 7 days)

This ensures only recent PR/MR activity is included in weekly summary.

### Fallback: Parse URLs from Comments

If Jira development panel is unavailable:
1. Search issue comments for GitHub/GitLab URLs
2. Extract PR/MR numbers from URLs (e.g., `/pull/123`, `/merge_requests/456`)
3. Fetch details directly from GitHub/GitLab API
4. Filter by update date
