# Release Notes Generator Workflow

Automatically generate professional, structured release notes from git commit history.

## Overview

This workflow helps you create comprehensive release notes by analyzing git commits between version tags. It automatically categorizes changes into features, bug fixes, breaking changes, and enhancements, making it easy to communicate updates to your users.

## Features

✨ **Automatic Categorization**
- Features (feat:, feature:, add:)
- Bug Fixes (fix:, bugfix:)
- Breaking Changes (BREAKING CHANGE:, breaking:)
- Enhancements (enhance:, improve:, update:)

🔍 **Smart Parsing**
- Extracts PR numbers from commit messages
- Identifies commit hashes
- Categorizes by component (API, UI/UX, Database, CLI, etc.)

📝 **Professional Output**
- Markdown-formatted release notes
- Emoji indicators for visual scanning
- Clickable PR and commit links
- Statistics summary

📊 **Detailed Analytics**
- Total commit count
- Breakdown by category
- Component-level statistics

## Usage

### Conversational Mode

Simply describe what you need:

```
Generate release notes for v1.0.0 compared to v0.9.0
```

```
I need release notes for version v2.0.0 from the repository at /path/to/my/repo
```

```
Create release notes for v1.5.0 vs v1.4.0 with links to https://github.com/myorg/myrepo
```

### What You'll Be Asked

The workflow will guide you to provide:

1. **Current version tag** (required)
   - Example: `v1.0.0`, `2.0.0`, `v1.5.0-beta`

2. **Previous version tag** (recommended)
   - Example: `v0.9.0`
   - Omit to get all commits up to current version

3. **Repository path** (optional)
   - Defaults to current directory
   - Example: `/path/to/repository`

4. **Repository URL** (optional)
   - For generating clickable links
   - Example: `https://github.com/owner/repo`

## Output

All generated files are saved to `artifacts/release-notes/`:

```
artifacts/release-notes/
├── RELEASE_NOTES_v1.0.0.md    # Formatted release notes
├── stats_v1.0.0.json          # Statistics in JSON format
└── generate_v1.0.0.py         # Generation script (for reference)
```

## Example Output

```markdown
# v1.0.0 Release Notes

**Release Date:** April 10, 2026
**Previous Version:** v0.9.0
**Repository:** [https://github.com/org/repo](https://github.com/org/repo)

---

## 🎉 Major Features

### API
API enhancements and new endpoints.

| Feature | Description | PR |
|---------|-------------|-----|
| **Add OAuth2 authentication** | Add OAuth2 authentication support | [#123](https://github.com/org/repo/pull/123) |

## 🐛 Bug Fixes

### Database
- **Fix connection pool timeout** [#130](https://github.com/org/repo/pull/130)

## ⚠️ Breaking Changes

- **Remove deprecated v1 API endpoints**
  - **Impact**: HIGH - Review breaking changes before upgrading

## 📊 Release Statistics

- **Total Commits**: 45
- **New Features**: 12
- **Bug Fixes**: 8
- **Breaking Changes**: 2
- **Enhancements**: 23
```

## Commit Message Best Practices

For optimal results, use conventional commit format:

### Features
```
feat: Add user authentication
feat(api): Implement GraphQL endpoint
feature: Add dark mode support
```

### Bug Fixes
```
fix: Resolve login timeout issue
fix(db): Correct connection pool configuration
bugfix: Fix memory leak in cache
```

### Breaking Changes
```
BREAKING CHANGE: Remove legacy API v1
feat!: Redesign authentication flow
breaking: Drop support for Node.js 14
```

### Enhancements
```
enhance: Improve database query performance
improve(ui): Better error messages
update: Upgrade dependencies
```

### Include PR Numbers
```
feat: Add feature (#123)
fix: Resolve bug (#456)
```

## Technical Details

### Tool Used

This workflow uses the [utility-mcp-server](https://github.com/realmcpservers/utility-mcp-server) Python package, which provides:

- Git commit parsing and analysis
- Conventional commit pattern recognition
- Category and component detection
- Markdown formatting
- Statistics generation

### Requirements

- Git repository with tags
- Python 3.12 or higher
- Git CLI available
- Internet connection (for package installation on first use)

### Automatic Installation

The workflow automatically installs the required `utility-mcp-server` package if not already present. No manual setup required!

## Tips for Better Release Notes

1. **Use Consistent Tagging**
   - Semantic versioning: `v1.0.0`, `v1.1.0`, `v2.0.0`
   - Or simple versions: `1.0.0`, `2.0.0`

2. **Write Descriptive Commits**
   - Clear, concise commit messages
   - Include context about why, not just what
   - Reference issues/PRs when applicable

3. **Categorize Appropriately**
   - Use conventional commit prefixes
   - Be consistent across your team
   - Document your conventions

4. **Provide Repository URL**
   - Enables clickable PR and commit links
   - Makes release notes more interactive
   - Easier for users to investigate changes

## Troubleshooting

### No Commits Found

**Problem**: "No commits found between v1.0.0 and v0.9.0"

**Solutions**:
- Verify tags exist: `git tag -l`
- Check tag order (current should be newer than previous)
- Ensure you're in the correct repository

### Tags Don't Exist

**Problem**: "Tag v1.0.0 not found"

**Solutions**:
- List available tags: `git tag -l`
- Create tag if needed: `git tag v1.0.0`
- Verify tag name matches exactly (including `v` prefix)

### Sparse or Poorly Categorized Notes

**Problem**: Most commits appear as "General" or uncategorized

**Solutions**:
- Start using conventional commit format going forward
- Consider editing commit messages for important releases
- Document commit conventions for your team

### Installation Issues

**Problem**: "Failed to install utility-mcp-server"

**Solutions**:
- Verify Python 3.12+ is available: `python3 --version`
- Check pip works: `pip --version`
- Ensure internet connectivity

## Examples

### Example 1: Basic Release Notes
```
User: Generate release notes for v1.0.0 compared to v0.9.0

Workflow: 
1. Verifies tags exist
2. Analyzes commits between tags
3. Generates categorized release notes
4. Saves to artifacts/release-notes/RELEASE_NOTES_v1.0.0.md
5. Shows statistics
```

### Example 2: With Custom Repository
```
User: Create release notes for v2.0.0 from /home/user/projects/myapp

Workflow:
1. Navigates to specified path
2. Verifies it's a git repository
3. Checks for v2.0.0 tag
4. Generates notes
5. Saves output
```

### Example 3: With GitHub Links
```
User: Generate notes for v1.5.0 vs v1.4.0 for https://github.com/myorg/myrepo

Workflow:
1. Analyzes commits
2. Generates release notes WITH clickable links
3. PR numbers link to actual PRs
4. Commit hashes link to commits
5. Full changelog link included
```

## Support

- Report issues with the workflow to the workflows repository
- Report issues with the generation tool to [utility-mcp-server](https://github.com/realmcpservers/utility-mcp-server)
- Check existing workflows in the [workflows repository](https://github.com/ambient-code/workflows) for examples

## License

This workflow is part of the Ambient Code Platform workflows collection.
