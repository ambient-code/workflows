# /hygiene.link-initiatives - Link Orphaned Epics to Initiatives

## Purpose

Find epics without initiative links and suggest appropriate initiatives from configured initiative projects, using semantic matching across projects.

## Prerequisites

- `/hygiene.setup` must be run first
- Initiative projects must be configured in config.json

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key and initiative_projects list
   - If initiative_projects is empty: prompt user to configure via `/hygiene.setup`

2. **Query orphaned epics**:
   ```jql
   project = {PROJECT} AND issuetype = Epic AND "Parent Link" is EMPTY AND resolution = Unresolved
   ```
   - Fetch: key, summary, description
   - If none found: report success and exit

3. **For each orphaned epic**:
   
   a. **Extract keywords**:
      - Same process as `/hygiene.link-epics`
      - Combine summary + description, remove stopwords
   
   b. **Search for matching initiatives** (cross-project):
      ```jql
      project in ({INIT1},{INIT2}) AND issuetype = Initiative AND resolution = Unresolved AND text ~ "keyword1 keyword2"
      ```
      - Search across all configured initiative projects
      - Fetch: key, summary, project
   
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

5. **Display summary**:
   ```
   Found N orphaned epics:
   - M epics with good matches (≥50%)
   - P epics with no good match
   
   Top suggestions:
   [EPIC-45] "Authentication System" → [INIT-12] "User Management Platform" (80% match)
   [EPIC-46] "Payment Gateway" → No good match found (20% best match)
   ```

6. **Ask for confirmation**:
   - Prompt: "Apply these suggestions? (yes/no/show-details)"
   - Only link epics with good matches (≥50%)

7. **Execute linking operations**:
   - For each approved linking:
     - Update epic via PUT `/rest/api/3/issue/{epicKey}`
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
