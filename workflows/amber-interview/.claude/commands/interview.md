# /interview

Conduct a structured conversation to understand user needs.

## How It Works

1. **Consent** - Explain this will be saved and get permission
2. **Chat** - Ask exactly 3 questions about their experience (user can stop early - always accept partial info!)
3. **Check-in** - 4th question: "Are you good to send this feedback, or do you have any final thoughts?"
4. **Summarize** - Pull together what we learned
5. **Show** - Let them review what will be shared
6. **Destination** - Ask where to file it (Platform/Jira/GitHub)
7. **Validate** - Check credentials and project/repo exists
8. **Submit** - Create ticket/issue and return link

**Question Limit:** Keep interviews focused by asking exactly 3 open-ended questions, then checking if they're ready to proceed with a 4th confirmation question.

**Flexible Flow:** Users can indicate they've given enough info at any point - always accept partial information and proceed to summary.

## Privacy Notice (shown first)

"This conversation will be saved so we can learn from your feedback. Is that okay with you?"

## Example Flow

**After 3 questions:**
"Are you good to send this feedback, or do you have any final thoughts?"

If they share final thoughts → incorporate and continue to summary
If they're ready → proceed to summary

## What Users See Before Choosing Destination

```
Here's what we'll share:

About: Debugging takes too much time
Category: Idea

What we learned:
- You check 3-5 different places for one error
- Hard to connect the dots between logs

[Full conversation]

Looks good? (yes/no)
```

If yes → Ask where to file it

## Destination Selection

**Available integrations detected from environment:**
- Jira: `JIRA_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL` (optional: `JIRA_PROJECT` for default)
- GitHub: `GITHUB_TOKEN`
- Platform: Always available

**Prompt shown:**
```
Where should I file this?

1. Platform feedback (Ambient team)
2. Jira (detected)
3. GitHub (detected)
4. Multiple destinations

Choose [1-4]:
```

### Jira Submission Flow

1. **Ask for project key:**
   - If `JIRA_PROJECT` env var exists: "Use {JIRA_PROJECT}? (or specify different)"
   - Otherwise: "Which Jira project key? (e.g., PLAT, ENG, PROJ)"

2. **Validate project:**
   - Fast REST call: `GET /rest/api/3/project/{projectKey}`
   - If invalid: Ask for correct project key with example

3. **Ask for issue type:**
   - "Issue type? (Bug/Story/Task/Idea) [default: Task]"

4. **Create issue:**
   - REST API: `POST /rest/api/3/issue`
   - Fields: project key, summary (from feedback), description (conversation), issue type, labels

5. **Return link:**
   - "✓ Created PROJ-123: https://jira.example.com/browse/PROJ-123"

### GitHub Submission Flow

1. **Ask for repo:**
   - "Which repo? (format: owner/repo, e.g., acme/platform)"

2. **Validate repo:**
   - REST call: `GET /repos/{owner}/{repo}`
   - If invalid: Ask for correct repo with format example

3. **Create issue:**
   - REST API: `POST /repos/{owner}/{repo}/issues`
   - Fields: title (summary), body (conversation with category), labels

4. **Return link:**
   - "✓ Created issue #42: https://github.com/owner/repo/issues/42"

### Platform Submission Flow

- REST API: `POST /api/projects/{project}/agentic-sessions/{session}/agui/feedback`
- "✓ Sent to Ambient team"

### Multiple Destinations

- Collect metadata for each chosen destination
- Submit to all selected
- Return all created links

## What Gets Sent

### Platform Feedback (JSON)
```json
{
  "type": "interview",
  "content": {
    "transcript": "conversation",
    "summary": "main takeaway",
    "findings": ["what we learned"]
  },
  "metadata": {
    "tags": ["keywords"],
    "category": "idea"
  }
}
```

### Jira Issue (JSON)
```json
{
  "fields": {
    "project": {"key": "PROJ"},
    "summary": "[summary from feedback]",
    "description": "Category: [category]\n\n[conversation]",
    "issuetype": {"name": "Task"},
    "labels": ["amber-feedback", "[category]"]
  }
}
```

### GitHub Issue (JSON)
```json
{
  "title": "[summary from feedback]",
  "body": "**Category:** [category]\n\n[conversation]\n\n---\n*Filed via Amber Interview*",
  "labels": ["feedback", "[category]"]
}
```

Feedback is sent to chosen destination(s) and links are returned to user.
