# Quick Start - Release Notes Generator Workflow

Your complete ACP workflow is ready to deploy! 🎉

## What You Have

A production-ready Ambient Code Platform workflow that generates structured release notes from git commits.

### Files Created

```
release-notes-workflow/
├── .ambient/
│   └── ambient.json          ✅ Workflow configuration (REQUIRED)
├── .gitignore                ✅ Git ignore rules
├── CLAUDE.md                 ✅ Persistent context and guidelines (REQUIRED)
├── README.md                 ✅ User documentation (REQUIRED)
├── DEPLOYMENT.md             📘 Deployment instructions
├── COMMAND_TEMPLATE.md       📘 Reference for /generate command
└── QUICKSTART.md             📘 This file
```

### What's Missing (Optional)

The `.claude/commands/generate.md` file couldn't be created automatically due to security permissions. You can:
- **Option A**: Add it manually using `COMMAND_TEMPLATE.md` as reference
- **Option B**: Skip it - the workflow works conversationally without it

## Deploy in 3 Steps

### Step 1: Push to GitHub

```bash
cd /workspace/artifacts/release-notes-workflow

# Option A: Create new repository
git init
git add .
git commit -m "feat: Initial release notes generator workflow"
git remote add origin https://github.com/YOUR_USERNAME/acp-workflows.git
git push -u origin main

# Option B: Add to existing workflows repository
cp -r . /path/to/workflows-repo/workflows/release-notes-generator/
cd /path/to/workflows-repo
git add workflows/release-notes-generator
git commit -m "feat: Add release notes generator workflow"
git push
```

### Step 2: Test with Custom Workflow

1. Open **Ambient Code Platform**
2. Click **"Custom Workflow..."**
3. Enter:
   - **Git URL**: `https://github.com/YOUR_USERNAME/acp-workflows`
   - **Branch**: `main` (or your feature branch)
   - **Path**: `workflows/release-notes-generator` (or `release-notes-workflow` if at root)
4. Click **"Load Workflow"**
5. Test with: _"Generate release notes for v1.0.0 compared to v0.9.0"_

### Step 3: Make It Official (Optional)

To contribute to the official workflows repository:

1. **Fork**: https://github.com/ambient-code/workflows
2. **Add workflow**: Copy your files to `workflows/release-notes-generator/`
3. **Test**: Use Custom Workflow pointing to your fork
4. **Create PR**: Submit for review
5. **Celebrate**: Once merged, it's available to all ACP users! 🎉

## Quick Test

Want to test locally first?

```bash
# 1. Install the tool
pip install utility-mcp-server

# 2. Test generation
python3 << 'EOF'
import asyncio
from utility_mcp_server.src.tools.release_notes_tool import generate_release_notes

async def test():
    result = await generate_release_notes(
        version="v1.0.0",
        previous_version="v0.9.0",
        repo_path="/path/to/test/repo",
        repo_url="https://github.com/test/repo"
    )
    print(result["release_notes"] if result["status"] == "success" else result["error"])

asyncio.run(test())
EOF
```

## Customization

### Update Workflow Name

Edit `.ambient/ambient.json`:
```json
{
  "name": "Your Custom Name",
  "description": "Your description"
}
```

### Modify Behavior

Edit `CLAUDE.md` to change:
- How Claude interacts with users
- Error handling approach
- Output formatting preferences
- Best practice suggestions

### Add Commands

Create `.claude/commands/yourcommand.md` for custom commands.

## Troubleshooting

### "Workflow not found"
- Check Git URL is correct and accessible
- Verify path matches your directory structure
- Ensure repository is public or you have access

### "ambient.json invalid"
```bash
# Validate JSON
python3 -m json.tool .ambient/ambient.json
```

### "Tool installation fails"
- Verify Python 3.12+ is available
- Check internet connectivity
- Try manual install: `pip install utility-mcp-server`

## What This Workflow Does

When users load your workflow in ACP:

1. **Greeting**: Claude introduces itself as a release notes generator
2. **Conversation**: User describes what they need
3. **Gathering**: Claude asks for version tags, repo path, etc.
4. **Installation**: Automatically installs utility-mcp-server if needed
5. **Generation**: Creates release notes from git commits
6. **Categorization**: Sorts into features, bugs, breaking changes, enhancements
7. **Output**: Saves to `artifacts/release-notes/`
8. **Presentation**: Shows results and statistics

## Example User Experience

```
User: Generate release notes for v1.0.0

Claude: I'll help you generate release notes for v1.0.0. 
        What's the previous version you want to compare with?

User: v0.9.0

Claude: Perfect! I'll compare v1.0.0 with v0.9.0. 
        Would you like me to include a repository URL for clickable links?

User: https://github.com/myorg/myrepo

Claude: Great! Generating release notes...
        [Shows installation if needed]
        [Analyzes commits]
        [Presents release notes]
        
        📊 Statistics:
           Total commits: 45
           Features: 12
           Bug fixes: 8
           Breaking changes: 2
           Enhancements: 23
        
        ✅ Saved to artifacts/release-notes/RELEASE_NOTES_v1.0.0.md
```

## Next Steps

1. ✅ **Review files** - Make sure everything looks good
2. ✅ **Push to GitHub** - Use Step 1 above
3. ✅ **Test in ACP** - Use Custom Workflow feature
4. ✅ **Iterate** - Fix any issues, update, test again
5. ✅ **Deploy** - Keep private or contribute to official workflows
6. ✅ **Share** - Tell your team about it!

## Support

- **Workflow issues**: Check `DEPLOYMENT.md` troubleshooting section
- **Tool issues**: https://github.com/realmcpservers/utility-mcp-server/issues
- **ACP questions**: Check ACP documentation

## Resources

- **ACP Workflows Repository**: https://github.com/ambient-code/workflows
- **Workflow Development Guide**: See workflows repo
- **Utility MCP Server**: https://github.com/realmcpservers/utility-mcp-server
- **Example Workflows**: bugfix, dev-team, triage in workflows repo

---

**You're all set!** 🚀

Your release notes generator workflow is complete and ready to deploy. Follow the 3 steps above to get it running in ACP.

**Questions?** Check the other documentation files in this directory.
