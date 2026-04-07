# Jira Hygiene Workflow

Systematic Jira project hygiene through 10 specialized commands:

**Setup**: `/hygiene.setup`  
**Linking**: `/hygiene.link-epics`, `/hygiene.link-initiatives`  
**Activity**: `/hygiene.activity-summary`, `/hygiene.show-blocking`  
**Bulk Ops**: `/hygiene.close-stale`, `/hygiene.triage-new`  
**Data Quality**: `/hygiene.blocking-closed`, `/hygiene.unassigned-progress`, `/hygiene.activity-type`

All commands are defined in `.claude/commands/hygiene.*.md`.  
Artifacts written to `artifacts/jira-hygiene/`.

## Principles

- **Safety first**: All bulk operations use review-then-execute pattern
- **Transparency**: Show what will change before making changes
- **Auditability**: Log all operations with timestamps
- **Idempotency**: Safe to run commands multiple times
- **Semantic matching**: Use intelligent keyword-based matching for linking (50% threshold)
- **Priority-aware**: Different staleness thresholds by priority (High: 1w, Medium: 2w, Low: 1m)

## Hard Limits

### API Safety

- **No operations without environment variables** - Validate JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN before any API call
- **No API token logging** - Always redact tokens in logs, use `len(token)` if needed
- **Respect rate limits** - Minimum 0.5s delay between requests, retry on 429
- **No modification of closed tickets** - Only operate on `resolution = Unresolved`
- **Validate HTTP responses** - Check status codes, parse JSON safely

### Bulk Operations

- **No destructive operations without confirmation** - All bulk operations require explicit user approval
- **No cross-project operations without mapping** - Initiative linking requires configured project mapping
- **Maximum 50 tickets per confirmation** - Batch large operations for user review
- **Dry-run support required** - All bulk commands must support `--dry-run` flag
- **Log every operation** - Write timestamp, action, ticket key, result to operation logs

### Data Integrity

- **Validate JQL before execution** - Test queries return expected types/fields
- **No silent failures** - Report errors clearly, don't skip without notification
- **Preserve existing data** - Don't overwrite assignees, priorities, or custom fields without explicit intent
- **No duplicate links** - Check if link already exists before creating
- **Verify field IDs** - Fetch custom field metadata, don't hardcode field IDs

## Safety

### Review-then-Execute Pattern

Every bulk operation follows this flow:

1. **Query** - Execute JQL, fetch ticket data
2. **Analyze** - Extract keywords, calculate match scores, determine candidates
3. **Save** - Write candidates to `artifacts/jira-hygiene/candidates/{operation}.json`
4. **Display** - Show summary with ticket counts, match scores, or suggestions
5. **Confirm** - Ask user for explicit approval ("yes" to proceed)
6. **Execute** - Only if confirmed, make API calls with rate limiting
7. **Log** - Write results to `artifacts/jira-hygiene/operations/{operation}-{timestamp}.log`

### Dry-Run Mode

When user passes `--dry-run` flag:

- Execute steps 1-4 only
- Display "DRY RUN" header prominently
- Show what **would** happen without making changes
- Skip steps 5-7 entirely

### Error Handling

- **Connection errors**: Check network, validate JIRA_URL format
- **Auth errors (401)**: Validate email/token, suggest regenerating token
- **Rate limit (429)**: Wait and retry, increase delay to 1s
- **Not found (404)**: Ticket may have been deleted, log and continue
- **Bad request (400)**: JQL syntax error or invalid field, show error message
- **Server error (500)**: Jira issue, suggest trying again later

## Quality

### JQL Best Practices

- Always include `resolution = Unresolved` for active tickets
- Use `text ~` for keyword search, not exact match
- Escape quotes in JQL: use single quotes for values with spaces
- Test JQL in Jira UI before using in commands
- Use project key, not project name (e.g., `PROJ` not `"My Project"`)

### Semantic Matching

For linking orphaned tickets:

1. Extract keywords: Remove stopwords (the, a, an, is, for, to, etc.)
2. Keep technical terms: Preserve API, auth, payment, etc.
3. Search strategy: Start with all keywords, fallback to top 3 if no results
4. Score calculation: `(matching_keywords / total_keywords) * 100`
5. Thresholds:
   - ≥50%: Suggest linking with confidence
   - <50%: Suggest creating new epic/initiative
   - 0%: Always suggest creating new

### Activity Summary Quality

When generating weekly summaries:

- Focus on status changes (New → In Progress → Done)
- Highlight new assignments or reassignments
- Include comment count (not full text)
- Summarize in 2-4 sentences
- Use business language, not technical jargon
- Format: "This week, {X} stories were {action}. {Y} items are {status}. {Notable events}."

## Escalation

Stop and request human guidance when:

- **Environment variables missing** - Cannot proceed without credentials
- **Project key unknown** - User must specify which project to operate on
- **Initiative project mapping unclear** - Cross-project linking requires explicit configuration
- **Custom field name ambiguous** - Multiple fields match "Activity Type", need field ID
- **Bulk operation >100 tickets** - Confirm user wants to proceed with large batch
- **API errors persist** - After 3 retries, suggest checking Jira status

## Configuration

The workflow uses `artifacts/jira-hygiene/config.json` to cache:

```json
{
  "jira_url": "https://company.atlassian.net",
  "project_key": "PROJ",
  "initiative_projects": ["INIT1", "INIT2"],
  "activity_type_field_id": "customfield_10050",
  "activity_type_values": ["Development", "Bug Fix", "Documentation", "Research"],
  "staleness_thresholds": {
    "Highest": 7,
    "High": 7,
    "Medium": 14,
    "Low": 30,
    "Lowest": 30
  }
}
```

This file is created by `/hygiene.setup` and read by other commands. It avoids repeated API calls for field metadata.

## Testing

Before submitting PR, verify:

1. **Validate JSON**: `jq . .ambient/ambient.json` (no syntax errors)
2. **Check commands**: All 10 command files exist in `.claude/commands/`
3. **Test dry-run**: Run `/hygiene.close-stale --dry-run` without making changes
4. **Verify logging**: Operation logs contain timestamp, action, results
5. **Check rate limiting**: Monitor API call timing (≥0.5s gaps)

## Custom Workflow Testing

Test in ACP using Custom Workflow:

- **URL**: `https://github.com/YOUR-USERNAME/workflows.git` (your fork)
- **Branch**: `feature/jira_hygiene_workflows`
- **Path**: `workflows/jira-hygiene`
