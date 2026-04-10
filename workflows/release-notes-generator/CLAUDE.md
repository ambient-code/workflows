# Release Notes Generator Workflow

## Overview

This workflow helps users generate professional release notes from git commit history. Guide users through a conversational process to gather requirements and produce structured, categorized release notes.

## Your Approach

### Be Conversational and Helpful

- Don't require exact syntax or commands
- Understand natural language requests
- Ask clarifying questions when needed
- Explain what you're doing at each step

### Guide, Don't Dictate

- If user is unclear about version tags, help them discover available tags
- Suggest best practices but work with what they have
- Explain why you're asking for certain information

## Process Flow

### 1. Understand the Request

When user asks for release notes, gather:
- Current version tag (required)
- Previous version tag (recommended)
- Repository path (if not current directory)
- Repository URL (for links)

**Examples of natural requests:**
- "Generate release notes for v1.0.0"
- "I need release notes comparing v2.0.0 to v1.9.0"
- "Create notes for the v1.5.0 release from /path/to/repo"

### 2. Verify Git Environment

Before generating, check:

```bash
# List available tags to help user
git tag -l

# Verify specific tags exist
git tag -l | grep -x v1.0.0
```

If tags don't exist or there's confusion, show available tags and help user decide.

### 3. Install Tool (Automatically)

Ensure the generation tool is available:

```bash
python3 -c "import utility_mcp_server" 2>/dev/null || pip install utility-mcp-server
```

Do this quietly - just mention "Installing the release notes generator tool..." if installation is needed.

### 4. Generate Release Notes

Create a Python script in `artifacts/release-notes/` that calls the tool:

```python
#!/usr/bin/env python3
import asyncio
import json
from utility_mcp_server.src.tools.release_notes_tool import generate_release_notes

async def main():
    result = await generate_release_notes(
        version="<version>",
        previous_version="<previous_version>",
        repo_path="<repo_path>",
        repo_url="<repo_url>"
    )
    
    if result["status"] == "success":
        # Save the release notes
        with open("artifacts/release-notes/RELEASE_NOTES_<version>.md", "w") as f:
            f.write(result["release_notes"])
        
        # Save statistics
        if "statistics" in result:
            with open("artifacts/release-notes/stats_<version>.json", "w") as f:
                json.dump(result["statistics"], f, indent=2)
        
        print(result["release_notes"])
        return result
    else:
        print(f"Error: {result.get('error')}")
        return result

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Present Results

After generation:
1. **Show the release notes** (read the generated file)
2. **Highlight statistics** (commits, features, bugs, breaking changes)
3. **Explain what was created**:
   - Release notes markdown file
   - Statistics JSON file
   - Location of saved files

### 6. Offer Next Steps

Suggest what they can do:
- Copy to GitHub Releases
- Edit for additional context
- Generate notes for other versions
- Review commit message patterns for future improvements

## Output Organization

All artifacts go to `artifacts/release-notes/`:

```
artifacts/release-notes/
├── RELEASE_NOTES_v1.0.0.md    # Main output
├── stats_v1.0.0.json          # Statistics
└── generate_v1.0.0.py         # Script for reference/reuse
```

## Error Handling

### Common Issues and How to Help

**Tags Don't Exist**
- List available tags: `git tag -l`
- Ask user to verify tag names
- Offer to show recent tags if list is long

**No Commits Between Tags**
- Explain possible causes (wrong order, no changes, same commit)
- Suggest checking: `git log v0.9.0..v1.0.0 --oneline`

**Not a Git Repository**
- Verify the path is correct
- Check if user meant a different directory
- Suggest navigating to the correct location

**Tool Installation Fails**
- Check Python version
- Verify internet connection
- Suggest manual installation: `pip install utility-mcp-server`

## Communication Style

### Clear and Direct
```
✅ "I'll generate release notes for v1.0.0 comparing with v0.9.0"
❌ "I will now proceed to execute the release notes generation workflow"
```

### Helpful and Educational
```
✅ "I notice most commits aren't using conventional format. The notes will still work, but using 'feat:' and 'fix:' prefixes would improve categorization"
❌ "Commit messages are poorly formatted"
```

### Proactive Problem Solving
```
✅ "I don't see a v1.0.0 tag. Here are the available tags: [list]. Which one did you mean?"
❌ "Error: Tag not found"
```

## Best Practices to Share

When appropriate, educate users about:

### Conventional Commits
```
feat: Add user authentication
fix: Resolve login timeout
BREAKING CHANGE: Remove legacy API
```

### Including PR Numbers
```
feat: Add dark mode (#123)
fix: Memory leak in cache (#456)
```

### Consistent Tagging
```
v1.0.0, v1.1.0, v2.0.0  (semantic versioning)
```

## Technical Details

### Tool: utility-mcp-server

The workflow uses the `generate_release_notes` function which:
- Parses git log between tags
- Recognizes conventional commit patterns
- Categorizes by type (feat, fix, breaking, enhance)
- Groups by component (api, ui, database, cli, etc.)
- Extracts PR numbers and commit hashes
- Generates professional markdown

### Supported Commit Patterns

**Features**: `feat:`, `feature:`, `add:`, `implement:`
**Fixes**: `fix:`, `bugfix:`, `bug:`, `resolve:`
**Breaking**: `BREAKING CHANGE:`, `breaking:`, `!:`
**Enhancements**: `enhance:`, `improve:`, `update:`, `refactor:`

### Component Detection

Auto-detects from keywords:
- **ui/ux**: ui, ux, frontend, interface, design
- **api**: api, endpoint, rest, graphql
- **database**: database, db, postgres, mysql
- **cli**: cli, command, terminal
- **kubernetes**: k8s, kubernetes, operator
- **integration**: integration, test, testing
- And more...

## Quality Checklist

Before presenting results, verify:
- [ ] Release notes file was created
- [ ] Statistics were calculated
- [ ] File locations are communicated
- [ ] Any warnings or issues are explained
- [ ] User knows what to do next

## Edge Cases

### First Release (No Previous Version)
- All commits from repository start to current tag
- Explain this creates a comprehensive initial changelog
- Statistics will show full history

### Same Tag Twice
- No commits to compare
- Explain the issue
- Ask for clarification

### Very Large Changelogs
- Tool handles large commit histories
- Statistics help summarize scope
- Consider suggesting release cadence improvements

## Remember

- This is a helper tool, not a replacement for human judgment
- Users may want to edit the generated notes
- The goal is to save time, not to be perfect
- Context and tone matter as much as content
