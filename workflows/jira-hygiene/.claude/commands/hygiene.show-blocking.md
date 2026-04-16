# /hygiene.show-blocking - Show Blocking Tickets

## Purpose

Display all tickets that are blocking other tickets via "Blocks" issue links. This highlights items that are preventing other work from progressing.

## Prerequisites

- `/hygiene.setup` must be run first

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract base_jql

2. **Query blocking tickets WITH PAGINATION**:
   ```jql
   ({base_jql}) AND issueFunction in linkedIssuesOf("({base_jql})", "blocks")
   ```
   
   **Note**: Both outer query AND inner linkedIssuesOf query use base_jql for consistency
   
   **Pagination logic**:
   ```
   all_blocking_tickets = []
   start_at = 0
   max_results = 50
   
   Loop:
     response = GET /rest/api/3/search?jql={encoded_jql}&startAt={start_at}&maxResults={max_results}&fields=key,summary,assignee,status,created,updated,priority,issuelinks&orderBy=updated DESC
     tickets = response['issues']
     all_blocking_tickets.extend(tickets)
     
     Print: "Fetched {start_at + len(tickets)}/{response['total']} blocking tickets..."
     
     if start_at + len(tickets) >= response['total']:
       break  # All results fetched
     
     start_at += max_results
     sleep(0.5)  # Rate limit
   ```
   
   - This finds tickets that have outward "blocks" links to other tickets
   - Fetch: key, summary, assignee, status, created, updated, priority, issuelinks
   - Also fetch issue links to see what tickets are being blocked
   - Order by updated descending (most recent first)
   
   **Alternative approach** (if issueFunction not available):
   - Get all unresolved tickets
   - For each, fetch issue links via `/rest/api/3/issue/{key}?fields=issuelinks`
   - Filter tickets that have outward "blocks" type links

3. **Format as markdown table with Jira links**:
   ```markdown
   # Blocking Tickets in {PROJECT}
   
   **Total**: N tickets blocking M other tickets
   **Generated**: {timestamp}
   **[View in Jira]({JIRA_URL}/issues/?jql=project+%3D+{PROJECT}+AND+issueFunction+in+linkedIssuesOf%28%22project+%3D+{PROJECT}%22%2C+%22blocks%22%29+AND+resolution+%3D+Unresolved)**
   
   | Blocking Ticket | Summary | Blocks | Assignee | Status | Priority | Last Updated |
   |-----------------|---------|--------|----------|--------|----------|--------------|
   | [PROJ-123]({JIRA_URL}/browse/PROJ-123) | Database migration issue | [PROJ-145]({JIRA_URL}/browse/PROJ-145), [PROJ-167]({JIRA_URL}/browse/PROJ-167) | John Doe | In Progress | High | 2d ago |
   | [PROJ-456]({JIRA_URL}/browse/PROJ-456) | Security audit | [PROJ-500]({JIRA_URL}/browse/PROJ-500) | Unassigned | To Do | Medium | 3d ago |
   ```
   
   **Link format**:
   - Ticket links: `[{KEY}]({JIRA_URL}/browse/{KEY})`
   - Search link: `[View in Jira]({JIRA_URL}/issues/?jql={URL_ENCODED_JQL})`
   - URL-encode JQL: spaces → `+`, special chars → percent-encoded
   - List blocked tickets in "Blocks" column as comma-separated links

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

**Total**: 3 tickets blocking 5 other tickets  
**Generated**: 2026-04-07 10:30 UTC  
**[View in Jira](https://company.atlassian.net/issues/?jql=project+%3D+PROJ+AND+issueFunction+in+linkedIssuesOf%28%22project+%3D+PROJ%22%2C+%22blocks%22%29+AND+resolution+%3D+Unresolved)**

## Summary

- 2 tickets assigned
- 1 ticket unassigned ⚠️
- Oldest blocker: 12 days (PROJ-456)

## Tickets

| Blocking Ticket | Summary | Blocks | Assignee | Status | Priority | Last Updated |
|-----------------|---------|--------|----------|--------|----------|--------------|
| [PROJ-123](https://company.atlassian.net/browse/PROJ-123) | Critical API failure in auth endpoint | [PROJ-150](https://company.atlassian.net/browse/PROJ-150), [PROJ-151](https://company.atlassian.net/browse/PROJ-151) | John Doe | In Progress | High | 2d ago |
| [PROJ-456](https://company.atlassian.net/browse/PROJ-456) | Database migration blocked by schema lock | [PROJ-460](https://company.atlassian.net/browse/PROJ-460) | Unassigned | To Do | Medium | 3d ago |
| [PROJ-789](https://company.atlassian.net/browse/PROJ-789) | Production deployment failing | [PROJ-800](https://company.atlassian.net/browse/PROJ-800), [PROJ-801](https://company.atlassian.net/browse/PROJ-801) | Jane Smith | Code Review | High | 1d ago |

## Recommendations

- **[PROJ-456](https://company.atlassian.net/browse/PROJ-456)**: Assign to database team immediately (unassigned, blocking [PROJ-460](https://company.atlassian.net/browse/PROJ-460))
- **[PROJ-123](https://company.atlassian.net/browse/PROJ-123)**: Follow up on progress (blocking 2 tickets for 5 days)
- **[PROJ-789](https://company.atlassian.net/browse/PROJ-789)**: In code review, close to unblocking deployment work
```

## Error Handling

- **No blocking tickets found**: Report "No tickets are currently blocking other work in {PROJECT}" (good news!)
- **issueFunction not available**: Fall back to API approach (fetch all tickets, check issue links)
- **Query failed**: Check JQL syntax, validate project key
- **Issue links unavailable**: Some Jira instances may restrict issue link access; note in report
