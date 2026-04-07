# /hygiene.activity-type - Suggest Activity Type for Tickets

## Purpose

Find tickets missing the "Activity Type" custom field value and suggest appropriate values based on semantic analysis of the ticket content.

## Prerequisites

- `/hygiene.setup` must be run first
- Activity Type field must be configured in config.json

## Arguments

Optional:
- `--dry-run` - Show suggestions without making changes

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key, Activity Type field ID, and available values
   - If Activity Type field is not configured: prompt user to run `/hygiene.setup`

2. **Query tickets missing Activity Type**:
   ```jql
   project = {PROJECT} AND "{ACTIVITY_TYPE_FIELD_NAME}" is EMPTY AND resolution = Unresolved
   ```
   - Fetch: key, summary, description, issuetype
   - If none found: report success and exit

3. **For each ticket**:
   
   a. **Analyze ticket content**:
      - Combine summary + description + issuetype
      - Extract key terms and phrases
   
   b. **Match against available Activity Type values**:
      - For each available value (e.g., "Development", "Bug Fix", "Documentation", "Research", "Testing")
      - Define keyword mappings:
        - **Development**: implement, create, add, build, develop, feature, enhance
        - **Bug Fix**: fix, bug, error, issue, broken, crash, defect
        - **Documentation**: document, doc, readme, guide, wiki, manual
        - **Research**: research, investigate, explore, spike, POC, prototype, feasibility
        - **Testing**: test, QA, quality, verify, validate, automation
      - Count keyword matches for each activity type
      - Suggest activity type with highest match count
   
   c. **Consider issue type**:
      - If issuetype = "Bug" → increase "Bug Fix" score
      - If issuetype = "Task" and keywords unclear → default to "Development"
      - If issuetype = "Story" → likely "Development" unless keywords suggest otherwise
   
   d. **Assign confidence**:
      - High: Clear keywords match (≥3 keyword hits)
      - Medium: Some keywords match (1-2 keyword hits)
      - Low: No keywords, using issuetype heuristic

4. **Write candidates file**:
   - Save to `artifacts/jira-hygiene/candidates/activity-type.json`
   - Include: key, summary, suggested activity type, confidence, matching keywords

5. **Display summary**:
   ```
   Found N tickets missing Activity Type:
   
   High confidence (≥3 keyword matches): 12 tickets
     PROJ-100 "Fix broken login flow" → Bug Fix (keywords: fix, broken, bug)
     PROJ-101 "Document API endpoints" → Documentation (keywords: document, API, guide)
   
   Medium confidence (1-2 matches): 5 tickets
     PROJ-102 "Improve performance" → Development (keywords: improve)
   
   Low confidence (issuetype heuristic): 3 tickets
     PROJ-103 "Update system" → Development (Bug issuetype suggests bug fix, but no clear keywords)
   ```

6. **Ask for confirmation**:
   - If `--dry-run`: Skip, display "DRY RUN - No changes made"
   - Otherwise prompt: "Apply Activity Type suggestions? (yes/no/high-confidence-only)"

7. **Execute updates**:
   - For each approved ticket:
     - Update custom field via PUT `/rest/api/3/issue/{key}`
     - Payload: `{"fields": {"{FIELD_ID}": {"value": "{ACTIVITY_TYPE}"}}}`
     - Rate limit: 0.5s between tickets

8. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/activity-type-{timestamp}.log`

## Output

- `artifacts/jira-hygiene/candidates/activity-type.json`
- `artifacts/jira-hygiene/operations/activity-type-{timestamp}.log`

## Example Candidates JSON

```json
[
  {
    "key": "PROJ-100",
    "summary": "Fix broken login flow after OAuth upgrade",
    "description_snippet": "Users cannot log in after OAuth upgrade...",
    "issuetype": "Bug",
    "suggested_activity_type": "Bug Fix",
    "confidence": "high",
    "matching_keywords": ["fix", "broken", "bug", "login"],
    "keyword_scores": {
      "Bug Fix": 4,
      "Development": 1,
      "Testing": 0,
      "Documentation": 0,
      "Research": 0
    }
  },
  {
    "key": "PROJ-101",
    "summary": "Document new API endpoints for partner integration",
    "description_snippet": "Need to create documentation for...",
    "issuetype": "Task",
    "suggested_activity_type": "Documentation",
    "confidence": "high",
    "matching_keywords": ["document", "documentation", "api", "create"],
    "keyword_scores": {
      "Documentation": 4,
      "Development": 1,
      "Bug Fix": 0,
      "Testing": 0,
      "Research": 0
    }
  },
  {
    "key": "PROJ-103",
    "summary": "Update user permissions",
    "description_snippet": "",
    "issuetype": "Task",
    "suggested_activity_type": "Development",
    "confidence": "low",
    "matching_keywords": [],
    "keyword_scores": {
      "Development": 0,
      "Bug Fix": 0,
      "Documentation": 0,
      "Testing": 0,
      "Research": 0
    },
    "note": "No clear keywords, defaulting to Development based on Task issuetype"
  }
]
```

## Keyword Mapping

Default keyword mappings (can be customized based on your available Activity Type values):

**Development**:
- implement, create, add, build, develop, feature, enhance, new, update, upgrade, refactor

**Bug Fix**:
- fix, bug, error, issue, broken, crash, defect, problem, failure, incorrect

**Documentation**:
- document, doc, readme, guide, wiki, manual, write, specification, help

**Research**:
- research, investigate, explore, spike, POC, proof of concept, prototype, feasibility, study

**Testing**:
- test, QA, quality, verify, validate, automation, check, coverage, suite

**Custom Values**:
If your project has custom Activity Type values, you'll need to define keyword mappings for them or update the semantic matching logic.

## Custom Field Update Payload

Activity Type is typically a **select** custom field. The update payload varies by field type:

**Single select**:
```json
{
  "fields": {
    "customfield_10050": {
      "value": "Bug Fix"
    }
  }
}
```

**Multi-select** (if configured to allow multiple):
```json
{
  "fields": {
    "customfield_10050": [
      {"value": "Bug Fix"},
      {"value": "Testing"}
    ]
  }
}
```

This workflow assumes single-select by default.

## Error Handling

- **Activity Type field not configured**: Prompt to run `/hygiene.setup`
- **Field ID changed**: Re-fetch field metadata if update fails with 400
- **Invalid value**: If suggested value is not in allowed values list, log error and skip
- **Permission denied**: User may not have permission to edit custom fields; log and continue
