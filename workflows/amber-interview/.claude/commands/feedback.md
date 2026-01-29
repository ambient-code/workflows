# /feedback

Collect casual feedback from users.

## How It Works

1. **Chat** - Have a natural conversation about what's on their mind
2. **Summarize** - Create a simple summary
3. **Show** - Let them review what will be shared
4. **Send** - They choose to send it or go back

## What Users See Before Sending

```
Here's what we'll share with the team:

About: Error messages are confusing
Category: Bug
Tags: errors, jira

[Full conversation]

Want to send this? (yes/no)
```

## What Gets Sent

```json
{
  "type": "feedback",
  "content": {
    "transcript": "conversation",
    "summary": "what this is about"
  },
  "metadata": {
    "tags": ["keywords"],
    "category": "bug"
  }
}
```

Sent to the team via API for review and action.
