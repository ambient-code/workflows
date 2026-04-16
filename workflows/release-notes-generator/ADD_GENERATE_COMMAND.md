# How to Add the /generate Command

The system has security restrictions that prevent automatic creation of files in `.claude/commands/`. 

You'll need to add the command file manually. Here's how:

## Quick Method

I've created the command content for you at:
```
/workspace/artifacts/release-notes-workflow/generate_command_temp.md
```

**Simply rename and move it:**

```bash
cd /workspace/artifacts/release-notes-workflow
mv generate_command_temp.md .claude/commands/generate.md
```

## Alternative: Create Directly in Git

If you've already pushed to GitHub and are working in a clone:

```bash
cd /path/to/your/workflows-repo/workflows/release-notes-generator

# Create the file directly
cat > .claude/commands/generate.md << 'EOF'
# /generate - Generate Release Notes

Generate structured release notes from git commits between two version tags with automatic categorization.

## Usage

\`\`\`
/generate [current_version] [previous_version] [repo_path] [repo_url]
\`\`\`

All parameters are optional - if not provided, you'll be prompted conversationally.

## Examples

\`\`\`
/generate v1.0.0 v0.9.0
/generate v2.0.0 v1.9.0 /path/to/repo
/generate v1.5.0 v1.4.0 /path/to/repo https://github.com/org/repo
\`\`\`

## Process

### 1. Gather Information

Collect from user (if not in command):
- Current version tag (required)
- Previous version tag (optional)
- Repository path (optional, defaults to current directory)
- Repository URL (optional, for clickable links)

### 2. Validate Environment

\`\`\`bash
# Verify git repository
git -C <repo_path> status

# List and verify tags
git -C <repo_path> tag -l
git -C <repo_path> tag -l | grep -x <version>
\`\`\`

### 3. Install Tool

\`\`\`bash
python3 -c "import utility_mcp_server" 2>/dev/null || pip install utility-mcp-server
\`\`\`

### 4. Create Generation Script

Save to \`artifacts/release-notes/generate_<version>.py\`:

\`\`\`python
#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from utility_mcp_server.src.tools.release_notes_tool import generate_release_notes

async def main():
    # Ensure output directory exists
    Path("artifacts/release-notes").mkdir(parents=True, exist_ok=True)
    
    # Generate release notes
    result = await generate_release_notes(
        version="<VERSION>",
        previous_version="<PREVIOUS_VERSION>",
        repo_path="<REPO_PATH>",
        repo_url="<REPO_URL>",
        release_date=None  # Uses today's date
    )
    
    if result.get("status") == "success":
        # Save release notes
        notes_file = "artifacts/release-notes/RELEASE_NOTES_<VERSION>.md"
        with open(notes_file, "w") as f:
            f.write(result["release_notes"])
        print(f"✅ Release notes saved to: {notes_file}")
        
        # Save statistics
        if "statistics" in result:
            stats_file = "artifacts/release-notes/stats_<VERSION>.json"
            with open(stats_file, "w") as f:
                json.dump(result["statistics"], f, indent=2)
            print(f"✅ Statistics saved to: {stats_file}")
        
        # Display release notes
        print("\n" + "="*80)
        print(result["release_notes"])
        print("="*80 + "\n")
        
        # Display statistics
        if "statistics" in result:
            print("📊 Statistics:")
            for key, value in result["statistics"].items():
                print(f"   {key}: {value}")
        
        return result
    else:
        error_msg = result.get("error", "Unknown error")
        print(f"❌ Error: {error_msg}")
        return result

if __name__ == "__main__":
    asyncio.run(main())
\`\`\`

### 5. Execute

\`\`\`bash
cd artifacts/release-notes && python3 generate_<version>.py
\`\`\`

### 6. Present Results

Show the user:
1. Generated release notes (formatted)
2. Statistics summary
3. File locations
4. Next steps

## Output

Files created in \`artifacts/release-notes/\`:
- \`RELEASE_NOTES_<version>.md\` - Main release notes
- \`stats_<version>.json\` - Statistics
- \`generate_<version>.py\` - Generation script

## Error Handling

Handle gracefully:
- Tags don't exist → List available tags
- No commits → Explain possible causes
- Not a git repo → Verify path
- Installation fails → Check Python/pip

## Tips

Suggest to users:
- Use conventional commits (\`feat:\`, \`fix:\`, etc.)
- Include PR numbers in commits
- Provide repository URL for links
- Tag releases consistently
EOF

# Commit it
git add .claude/commands/generate.md
git commit -m "feat: Add /generate command"
```

## Verify

Check that the file was created:

```bash
ls -la .claude/commands/
cat .claude/commands/generate.md
```

## Why is this file important?

The `/generate` command allows users to invoke the release notes generation with a slash command instead of just conversational mode. It's optional but provides a nice shortcut.

**Without it**: Workflow still works conversationally  
**With it**: Users can type `/generate v1.0.0 v0.9.0` for quick invocation

## Next Steps

Once you've added the command file:

1. Commit all changes
2. Push to GitHub
3. Test with Custom Workflow in ACP
4. Verify `/generate` command appears and works
