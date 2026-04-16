# /hygiene.link-initiatives - Link Orphaned Epics to Initiatives

## Purpose

Find epics without initiative links and suggest appropriate initiatives from configured initiative projects, using semantic matching across projects.

## Prerequisites

- `/hygiene.setup` must be run first
- Initiative projects must be configured in config.json

## Arguments

Optional:
- `--dry-run` - Run steps 1-4 (Query, Analyze, Save, Display) only, skip confirmation and API modifications

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract base_jql and initiative_projects list
   - If initiative_projects is empty: prompt user to configure via `/hygiene.setup`

2. **Query orphaned epics WITH PAGINATION**:
   ```jql
   ({base_jql}) AND issuetype = Epic AND "Parent Link" is EMPTY
   ```
   
   **Pagination logic**:
   ```
   all_orphaned_epics = []
   start_at = 0
   max_results = 50
   
   Loop:
     response = GET /rest/api/3/search?jql={encoded_jql}&startAt={start_at}&maxResults={max_results}&fields=key,summary,description
     epics = response['issues']
     all_orphaned_epics.extend(epics)
     
     Print: "Fetched {start_at + len(epics)}/{response['total']} orphaned epics..."
     
     if start_at + len(epics) >= response['total']:
       break  # All results fetched
     
     start_at += max_results
     sleep(0.5)  # Rate limit
   ```
   
   - Fetch: key, summary, description
   - If none found: report success and exit

3. **For each orphaned epic**:
   
   a. **Extract keywords**:
      - Same process as `/hygiene.link-epics`
      - Combine summary + description, remove stopwords
   
   b. **Search for matching initiatives WITH PAGINATION** (cross-project):
      ```jql
      project in ({INIT1},{INIT2}) AND issuetype = Initiative AND resolution = Unresolved AND text ~ "keyword1 keyword2"
      ```
      
      **Note**: Initiative search uses different project list, so base_jql is NOT applied here
      
      **Pagination for cross-project search**:
      ```
      matching_initiatives = []
      start_at = 0
      max_results = 50
      
      Loop:
        response = GET /rest/api/3/search?jql={search_jql}&startAt={start_at}&maxResults={max_results}&fields=key,summary,project
        initiatives = response['issues']
        matching_initiatives.extend(initiatives)
        
        if start_at + len(initiatives) >= response['total']:
          break  # All results fetched
        
        start_at += max_results
        sleep(0.5)  # Rate limit
      ```
      
      - Search across all configured initiative projects
      - Fetch: key, summary, project
      - Calculate match scores for ALL initiatives returned (not just first 50)
   
   c. **Calculate match scores**:
      - Score = (matching_keywords / total_keywords) * 100
      - Sort by score descending
   
   d. **Determine suggestion**:
      - If best score ≥50%: suggest linking to top initiative
      - If best score <50%: note "No good match found"
      - Unlike epics, don't suggest creating initiatives (typically higher-level planning)

4. **Write candidates file**:
   - Save to `artifacts/jira-hygiene/candidates/link-initiatives.json`
   - Include: epic key, epic summary, suggested initiative (if any), match score

5. **Display summary with Jira links**:
   ```
   Found N orphaned epics:
   - M epics with good matches (≥50%)
   - P epics with no good match
   
   View orphaned epics: {JIRA_URL}/issues/?jql=project+%3D+{PROJECT}+AND+issuetype+%3D+Epic+AND+%22Parent+Link%22+is+EMPTY
   
   Top suggestions:
   • [{EPIC-45}]({JIRA_URL}/browse/EPIC-45) "Authentication System" 
     → [{INIT-12}]({JIRA_URL}/browse/INIT-12) "User Management Platform" (80% match)
   • [{EPIC-46}]({JIRA_URL}/browse/EPIC-46) "Payment Gateway" 
     → No good match found (20% best match)
   ```

6. **Ask for confirmation**:
   - If `--dry-run`: Display "DRY RUN - No changes made" and skip to step 8
   - Otherwise prompt: "Apply these suggestions? (yes/no/show-details)"
   - Only link epics with good matches (≥50%)

7. **Execute linking operations** (skip if --dry-run):
   - For each approved linking:
     - **TOCTOU check**: GET `/rest/api/3/issue/{epicKey}?fields=parent` to verify Parent Link is still empty
     - If Parent Link is not empty: skip and log "Epic already linked to {existing_initiative}"
     - Otherwise, update epic via PUT `/rest/api/3/issue/{epicKey}`
     - Set Parent Link field to initiative key
     - Rate limit: 0.5s between requests

8. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/link-initiatives-{timestamp}.log`

## Output

- `artifacts/jira-hygiene/candidates/link-initiatives.json`
- `artifacts/jira-hygiene/operations/link-initiatives-{timestamp}.log`

## Example Candidates JSON

```json
[
  {
    "epic_key": "EPIC-45",
    "epic_summary": "Authentication System",
    "keywords": ["authentication", "system", "user", "login"],
    "suggestion": "link",
    "initiative_key": "INIT-12",
    "initiative_summary": "User Management Platform",
    "initiative_project": "INIT1",
    "match_score": 80,
    "matching_keywords": ["authentication", "user", "management"]
  },
  {
    "epic_key": "EPIC-46",
    "epic_summary": "Payment Gateway Integration",
    "keywords": ["payment", "gateway", "integration"],
    "suggestion": "no_match",
    "best_match_score": 20,
    "reason": "No initiatives found with >50% keyword match"
  }
]
```

## Error Handling

- **No initiative projects configured**: Prompt to run `/hygiene.setup` and configure
- **Cross-project access denied**: Some initiatives may not be accessible; log and skip
- **Parent Link field not found**: Fetch field metadata dynamically
