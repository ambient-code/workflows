# Deployment Guide - Release Notes Generator Workflow

This guide explains how to deploy your release notes generator workflow to the Ambient Code Platform.

## Quick Start

### Option 1: Test with Custom Workflow (Recommended First)

1. **Create a GitHub repository** (or use existing fork of ambient-code/workflows)

2. **Push this workflow**:
   ```bash
   cd /workspace/artifacts/release-notes-workflow
   
   # Initialize git if needed
   git init
   
   # Or copy to your workflows repo
   cp -r . /path/to/workflows-repo/workflows/release-notes-generator/
   
   cd /path/to/workflows-repo
   git add workflows/release-notes-generator
   git commit -m "feat: Add release notes generator workflow"
   git push origin main  # or your feature branch
   ```

3. **Test in ACP**:
   - Go to Ambient Code Platform UI
   - Click "Custom Workflow..."
   - Enter:
     - **Git URL**: `https://github.com/YOUR_USERNAME/workflows` (or your repo URL)
     - **Branch**: `main` (or your feature branch)
     - **Path**: `workflows/release-notes-generator`
   - Click "Load Workflow"

4. **Test it out**:
   - The workflow should start with a greeting
   - Try: "Generate release notes for v1.0.0 compared to v0.9.0"
   - Verify it works as expected

### Option 2: Contribute to Official Workflows

To make this available to ALL ACP users:

1. **Fork the official repository**:
   ```bash
   # Visit https://github.com/ambient-code/workflows
   # Click "Fork"
   
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/workflows.git
   cd workflows
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/release-notes-generator
   ```

3. **Add your workflow**:
   ```bash
   cp -r /workspace/artifacts/release-notes-workflow workflows/release-notes-generator
   
   git add workflows/release-notes-generator
   git commit -m "feat: Add release notes generator workflow

   Adds a new workflow for generating structured release notes from git commits.
   
   Features:
   - Automatic categorization (features, bugs, breaking changes, enhancements)
   - PR number extraction
   - Markdown formatting
   - Statistics generation
   "
   
   git push origin feature/release-notes-generator
   ```

4. **Create Pull Request**:
   - Go to https://github.com/ambient-code/workflows
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe the workflow and its benefits
   - Submit for review

5. **Once merged**:
   - Workflow appears in ACP UI automatically (~5 min cache)
   - Available to all users!

## File Structure

Your workflow should have:

```
release-notes-generator/
├── .ambient/
│   └── ambient.json          ✅ REQUIRED - Workflow config
├── .claude/
│   └── commands/             ⚠️  Optional - If you can create it
│       └── generate.md
├── CLAUDE.md                 ✅ REQUIRED - Persistent context
├── README.md                 ✅ REQUIRED - User documentation
└── DEPLOYMENT.md             ℹ️  Optional - This file
```

## Verification Checklist

Before deploying, verify:

- [ ] `.ambient/ambient.json` exists with required fields:
  - [ ] `name`
  - [ ] `description`
  - [ ] `systemPrompt`
  - [ ] `startupPrompt`
- [ ] `README.md` exists with usage instructions
- [ ] `CLAUDE.md` exists with workflow guidelines
- [ ] All JSON files are valid (check with `python -m json.tool ambient.json`)
- [ ] Tested with Custom Workflow feature
- [ ] Works for at least one test case

## Testing Checklist

Test these scenarios:

- [ ] Basic: `v1.0.0` vs `v0.9.0` in current directory
- [ ] With repo path: Specify different repository location
- [ ] With repo URL: Generate clickable links
- [ ] Error handling: Non-existent tags
- [ ] Error handling: Not a git repository
- [ ] First release: No previous version
- [ ] Edge case: Same tag twice

## Troubleshooting

### Workflow doesn't appear in Custom Workflow

**Check**:
- Git URL is correct and accessible
- Branch name is correct
- Path is correct (should be `workflows/release-notes-generator` not just `release-notes-generator`)
- Repository is public (or you have access)

### Workflow loads but doesn't work

**Check**:
- `ambient.json` is valid JSON
- All required fields are present
- `systemPrompt` has proper escaped quotes
- Test locally with `python -m json.tool .ambient/ambient.json`

### Tool installation fails

**Check**:
- Python 3.12+ is available in ACP session
- pip works and has internet access
- Package name is correct: `utility-mcp-server`

### Generated notes are empty or sparse

**Check**:
- Git tags exist: `git tag -l`
- Commits exist between tags: `git log v0.9.0..v1.0.0`
- Repository path is correct
- Not using same tag twice

## Maintenance

### Updating Your Workflow

After deployment, to make changes:

1. **Update local files**
2. **Commit and push**:
   ```bash
   git add .
   git commit -m "fix: Update workflow description"
   git push
   ```
3. **Test with Custom Workflow** pointing to your branch
4. **Merge to main** when satisfied

### Official Workflow Updates

If your workflow is in `ambient-code/workflows`:

1. Create feature branch
2. Make changes
3. Test with Custom Workflow
4. Create PR
5. Get reviewed and merged
6. Changes automatically available after cache refresh (~5 min)

## Advanced Configuration

### Adding Commands

To add the `/generate` command, you need to create:

`.claude/commands/generate.md`

Content should follow the command format (see the attempted file in the creation process).

**Note**: The `.claude/commands/` directory may require special permissions. If you can't create it programmatically, create it manually in your git repository.

### Adding Skills

Create `.claude/skills/skill-name/SKILL.md` for reusable knowledge or complex workflows.

### Adding MCP Integration

Create `.claude/settings.json`:

```json
{
  "mcpServers": {
    "utility-mcp-server": {
      "command": "python3",
      "args": ["-m", "utility_mcp_server.src.stdio_main"]
    }
  }
}
```

This makes the tool available via MCP protocol instead of direct Python calls.

## Support

- **Issues with workflow**: Open issue in the workflows repository
- **Issues with generation tool**: Open issue in [utility-mcp-server](https://github.com/realmcpservers/utility-mcp-server)
- **Questions about ACP**: Check ACP documentation or ask in community channels

## Next Steps

1. ✅ **Test locally** - Verify all files are correct
2. ✅ **Test with Custom Workflow** - Make sure it works in ACP
3. ✅ **Iterate** - Fix any issues
4. ✅ **Deploy** - Push to your repo or create PR
5. ✅ **Share** - Let others know about the workflow!

---

**Ready to deploy?** Follow Option 1 to test, then Option 2 to contribute to the official workflows! 🚀
