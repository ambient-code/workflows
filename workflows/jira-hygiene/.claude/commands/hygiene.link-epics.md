# /hygiene.link-epics - Link Orphaned Stories to Epics

## Purpose

Find stories without epic links and suggest appropriate epics to link them to, using semantic matching. If no good match exists (score <50%), suggest creating a new epic.

## Prerequisites

- `/hygiene.setup` must be run first to create `artifacts/jira-hygiene/config.json`
- Project key must be configured

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract project key

2. **Query orphaned stories**:
   ```jql
   project = {PROJECT} AND issuetype = Story AND "Epic Link" is EMPTY AND resolution = Unresolved
   ```
   - Fetch: key, summary, description
   - If none found: report success and exit

3. **For each orphaned story**:
   
   a. **Extract keywords**:
      - Combine summary + description
      - Remove stopwords (the, a, an, is, for, to, with, in, on, at, etc.)
      - Keep technical terms (API, auth, payment, database, etc.)
      - Lowercase and deduplicate
   
   b. **Search for matching epics**:
      ```jql
      project = {PROJECT} AND issuetype = Epic AND resolution = Unresolved AND text ~ "keyword1 keyword2 keyword3"
      ```
      - Start with all keywords; if no results, try top 3 keywords
      - Fetch: key, summary
   
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

5. **Display summary**:
   ```
   Found N orphaned stories:
   - M stories with good matches (≥50%)
   - P stories need new epics (<50% match)
   
   Top suggestions:
   [STORY-123] "Implement user login" → [EPIC-45] "Authentication System" (75% match)
   [STORY-124] "Add payment gateway" → Create new epic (0% match)
   ```

6. **Ask for confirmation**:
   - Prompt: "Apply these suggestions? (yes/no/show-details)"
   - If "show-details": display full candidate list with match details
   - If "no": exit without changes
   - If "yes": proceed to execution

7. **Execute linking operations**:
   - For each approved linking suggestion:
     - Update story via PUT `/rest/api/3/issue/{storyKey}`
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
