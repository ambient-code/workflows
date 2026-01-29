# Feedback Schema v1

Simple format for feedback and interview data.

## What Gets Saved

```json
{
  "type": "feedback" | "interview",
  "id": "unique-id",
  "timestamp": "when this happened",
  "user": {
    "user_id": "your id",
    "email": "your email",
    "session_id": "this session"
  },
  "content": {
    "transcript": "our conversation",
    "summary": "what this was about"
  },
  "metadata": {
    "tags": ["keywords"],
    "category": "bug | feature | idea | other"
  }
}
```

## Examples

**Quick Feedback:**
```json
{
  "type": "feedback",
  "content": {
    "summary": "Error messages are confusing"
  },
  "metadata": {
    "tags": ["errors", "jira"],
    "category": "bug"
  }
}
```

**Interview:**
```json
{
  "type": "interview",
  "content": {
    "summary": "Debugging takes too much time switching between tools",
    "findings": [
      "Check 3-5 different places for one error",
      "Hard to connect the dots between logs"
    ]
  },
  "metadata": {
    "tags": ["debugging", "workflow"],
    "category": "idea"
  }
}
```

## Internal Use (not shown to users)

The team can add:
- `priority` - How urgent this is
- `status` - What we're doing about it
- `assignee` - Who's working on it
