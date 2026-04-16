# /hygiene.link-epics - Link Orphaned Stories to Epics

## Purpose

Find stories without epic links and suggest appropriate epics to link them to, using semantic matching. If no good match exists (score <50%), suggest creating a new epic.

## Prerequisites

- `/hygiene.setup` must be run first to create `artifacts/jira-hygiene/config.json`
- Project key must be configured

## Arguments

Optional:
- `--dry-run` - Run steps 1-4 (Query, Analyze, Save, Display) only, skip confirmation and API mutations

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract base_jql

2. **Query orphaned stories WITH PAGINATION**:
   ```jql
   ({base_jql}) AND issuetype = Story AND "Epic Link" is EMPTY
   ```
   
   **Pagination logic**:
   ```
   all_orphaned_stories = []
   start_at = 0
   max_results = 50
   
   Loop:
     response = GET /rest/api/3/search?jql={encoded_jql}&startAt={start_at}&maxResults={max_results}&fields=key,summary,description
     stories = response['issues']
     all_orphaned_stories.extend(stories)
     
     Print: "Fetched {start_at + len(stories)}/{response['total']} orphaned stories..."
     
     if start_at + len(stories) >= response['total']:
       break  # All results fetched
     
     start_at += max_results
     sleep(0.5)  # Rate limit
   ```
   
   - Fetch: key, summary, description
   - If none found: report success and exit

3. **For each orphaned story**:
   
   a. **Extract keywords**:
      - Combine summary + description
      - Remove stopwords (the, a, an, is, for, to, with, in, on, at, etc.)
      - Keep technical terms (API, auth, payment, database, etc.)
      - Lowercase and deduplicate
   
   b. **Search for matching epics WITH PAGINATION**:
      ```jql
      ({base_jql}) AND issuetype = Epic AND text ~ "keyword1 keyword2 keyword3"
      ```
      
      **Pagination for semantic search**:
      ```
      matching_epics = []
      start_at = 0
      max_results = 50
      
      Loop:
        response = GET /rest/api/3/search?jql={search_jql}&startAt={start_at}&maxResults={max_results}&fields=key,summary
        epics = response['issues']
        matching_epics.extend(epics)
        
        if start_at + len(epics) >= response['total']:
          break  # All results fetched
        
        start_at += max_results
        sleep(0.5)  # Rate limit
      ```
      
      - Start with all keywords; if no results, try top 3 keywords
      - Fetch: key, summary
      - Calculate match scores for ALL epics returned (not just first 50)
   
   c. **Calculate match scores**:
      - For each epic found, count keywords that appear in epic summary
      - Score = (matching_keywords / total_keywords) * 100
      - Sort by score descending
   
   d. **Determine suggestion**:
      - If best score ≥50%: suggest linking to top epic
      - If best score <50%: suggest creating new epic
      - If no epics found: suggest creating new epic

4. **Write candidates file**:
   - Save to `artifacts/jira-hygiene/candidates/link-epics.json`
   - Include: story key, story summary, suggested action, epic key (if linking), match score

5. **Display summary with Jira links**:
   ```
   Found N orphaned stories:
   - M stories with good matches (≥50%)
   - P stories need new epics (<50% match)
   
   View orphaned stories: {JIRA_URL}/issues/?jql=project+%3D+{PROJECT}+AND+issuetype+%3D+Story+AND+%22Epic+Link%22+is+EMPTY
   
   Top suggestions:
   • [{STORY-123}]({JIRA_URL}/browse/STORY-123) "Implement user login" 
     → [{EPIC-45}]({JIRA_URL}/browse/EPIC-45) "Authentication System" (75% match)
   • [{STORY-124}]({JIRA_URL}/browse/STORY-124) "Add payment gateway" 
     → Create new epic (0% match)
   ```

6. **Ask for confirmation**:
   - If `--dry-run`: Display "DRY RUN - No changes made" and skip to step 8
   - Otherwise prompt: "Apply these suggestions? (yes/no/show-details)"
   - If "show-details": display full candidate list with match details
   - If "no": exit without changes
   - If "yes": proceed to execution

7. **Execute linking operations** (skip if --dry-run):
   - For each approved linking suggestion:
     - **TOCTOU check**: GET `/rest/api/3/issue/{storyKey}?fields=customfield_epic_link` to verify Epic Link is still empty
     - If Epic Link is not empty: skip and log "Story already linked to {existing_epic}"
     - Otherwise, update story via PUT `/rest/api/3/issue/{storyKey}`
     - Set Epic Link field (typically using "update" operation)
     - Rate limit: 0.5s between requests
   - For "create epic" suggestions: skip for now, just log recommendation
   
8. **Log results**:
   - Write to `artifacts/jira-hygiene/operations/link-epics-{timestamp}.log`
   - Include: timestamp, story key, action taken, result

## Output

- `artifacts/jira-hygiene/candidates/link-epics.json`
- `artifacts/jira-hygiene/operations/link-epics-{timestamp}.log`

## Example Candidates JSON

```json
[
  {
    "story_key": "STORY-123",
    "story_summary": "Implement user login functionality",
    "keywords": ["implement", "user", "login", "functionality"],
    "suggestion": "link",
    "epic_key": "EPIC-45",
    "epic_summary": "Authentication System",
    "match_score": 75,
    "matching_keywords": ["user", "login", "authentication"]
  },
  {
    "story_key": "STORY-124",
    "story_summary": "Add payment gateway integration",
    "keywords": ["add", "payment", "gateway", "integration"],
    "suggestion": "create_epic",
    "match_score": 0,
    "reason": "No existing epics match these keywords"
  }
]
```

## Error Handling

- **Config not found**: Prompt user to run `/hygiene.setup` first
- **No Epic Link field**: Some Jira instances use different field names; fetch field ID dynamically
- **API errors**: Log error, continue with next story (don't fail entire batch)
- **Rate limit (429)**: Increase delay to 1s, retry
