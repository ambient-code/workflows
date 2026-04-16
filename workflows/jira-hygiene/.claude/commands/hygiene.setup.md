# /hygiene.setup - Initial Configuration and Validation

## Purpose

Validate Jira API connection and configure project settings for all hygiene operations.

## Prerequisites

Environment variables must be set:
- `JIRA_URL` - Your Jira instance URL (e.g., https://company.atlassian.net)
- `JIRA_EMAIL` - Your Jira email address
- `JIRA_API_TOKEN` - Your Jira API token (generate at id.atlassian.com)

## Process

1. **Check environment variables**:
   ```bash
   if [ -z "$JIRA_URL" ] || [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
     echo "Error: Missing required environment variables"
     exit 1
   fi
   ```

2. **Test API connection**:
   - Call `/rest/api/3/myself` to validate credentials
   - Display authenticated user information
   - If fails: provide troubleshooting guidance

3. **Prompt for project configuration**:
   - **Target project key**: The Jira project to operate on (e.g., "PROJ")
   - **Initiative project keys**: Comma-separated list of projects containing initiatives (e.g., "INIT1,INIT2")
   - User must provide the exact project keys they want to use

4. **Prompt for base JQL filter (optional)**:
   - **Base JQL filter**: Custom JQL to scope all operations
   - If empty/skipped: Use default `"project = {PROJECT} AND resolution = Unresolved"`
   - Examples:
     - `"project = MYPROJ AND resolution = Unresolved AND labels = backend"`
     - `"project in (PROJ1, PROJ2) AND resolution = Unresolved AND team = Platform"`
     - `"project = MYPROJ AND resolution = Unresolved AND component = API"`
   - Explain: This filter will be combined with each command's specific conditions

4a. **Validate base JQL (if provided)**:
   - Test query via `GET /rest/api/3/search?jql={encoded_jql}&maxResults=1`
   - If 400 error: Show JQL syntax error, ask user to correct and retry
   - If 200: Proceed with valid JQL
   - If empty/skipped: Use default `"project = {PROJECT} AND resolution = Unresolved"`

5. **Fetch Activity Type field metadata**:
   - Call `/rest/api/3/field` to get all custom fields
   - Search for field with name matching "Activity Type" (case-insensitive)
   - Extract field ID (e.g., "customfield_10050")
   - Fetch allowed values for this field
   - If not found: note in config, skip this feature

6. **Create config file**:
   - Write all settings to `artifacts/jira-hygiene/config.json`
   - Include base_jql (either user-provided or default)
   - Include default staleness thresholds
   - Format as pretty JSON for readability

7. **Display summary**:
   - Show configured project key
   - Show base JQL filter
   - Show initiative project keys
   - Show Activity Type field ID and available values
   - Confirm setup is complete

## Output

- `artifacts/jira-hygiene/config.json`

## Example Config Structure

```json
{
  "jira_url": "https://company.atlassian.net",
  "project_key": "PROJ",
  "base_jql": "project = PROJ AND resolution = Unresolved",
  "initiative_projects": ["INIT1", "INIT2"],
  "activity_type_field_id": "customfield_10050",
  "activity_type_values": ["Development", "Bug Fix", "Documentation", "Research", "Testing"],
  "staleness_thresholds": {
    "Highest": 7,
    "High": 7,
    "Medium": 14,
    "Low": 30,
    "Lowest": 30
  },
  "configured_at": "2026-04-08T10:30:00Z"
}
```

## Error Handling

- **Missing env vars**: Provide setup instructions with links to Jira API token generation
- **Auth failed (401)**: Suggest checking email/token, regenerating token
- **Network error**: Check JIRA_URL format (must start with https://)
- **Field not found**: Activity Type feature will be disabled, note in config

