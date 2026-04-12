# Release Notes Generator Workflow

Generate professional, structured release notes with **AI-powered intelligent categorization** that understands your commits better than regex patterns ever could.

## Overview

This workflow uses Claude's intelligence to create comprehensive release notes by analyzing git commits between version tags. Unlike traditional tools that rely on pattern matching, Claude **actually understands** your commits and creates relevant categories dynamically based on what changed.

## 🧠 How It Works

### Two-Part Architecture

The MCP tool provides **two modes** of operation:

**Mode 1: AI-Powered (Default - Recommended for this workflow)**
- **MCP Tool**: Fetches raw commit data + provides AI instructions
- **Claude AI**: Analyzes commits, creates dynamic categories, formats intelligently
- **Best for**: Context-aware release notes with custom categories

**Mode 2: Pre-Formatted (For direct IDE usage)**
- **MCP Tool**: Fetches commits + automatically categorizes into 10 predefined categories
- **Output**: Ready-to-use markdown with emojis and statistics
- **Best for**: Quick testing in Cursor/VS Code, no AI analysis needed

**This Workflow Uses Mode 1:**
1. **MCP Tool (Data Fetching)**
   - Fetches raw commit data from GitHub/GitLab/local repos
   - Extracts: commit hash, message, author, date, PR/MR numbers
   - Provides AI instructions for intelligent categorization
   - **Does NOT categorize** - just returns structured data + instructions

2. **Claude AI (Intelligence)**
   - **Analyzes** commit messages to understand actual changes
   - **Creates dynamic categories** that fit your release (not predefined templates)
   - **Groups related changes** intelligently
   - **Formats professional release notes** with context and clarity

This separation means you get **smarter categorization** than regex-based tools can provide.

## Features

🧠 **AI-Powered Categorization**
- Understands context (e.g., "refactor auth" might be a breaking change)
- Creates dynamic categories based on actual changes
- Groups related commits together intelligently
- Highlights important changes (breaking, security, critical fixes)

🌐 **Remote Repository Support**
- **GitHub**: Fetch commits via API (no clone needed)
- **GitLab**: Fetch commits via API (no clone needed)  
- **Local**: Works with local git repositories
- Auto-detects previous version tag if not provided

🔍 **Smart Data Extraction**
- Extracts PR/MR numbers from commits
- Links to pull requests and commits
- Generates compare URLs
- Returns "Not Found" for commits without PR references

📝 **Professional Output**
- Markdown-formatted release notes
- Context-aware sections
- Clickable PR and commit links
- Statistics summary

## Usage

### Conversational Mode

Simply describe what you need:

```
Generate release notes for v1.0.0
```

```
Create release notes for v2.0.0 from https://github.com/myorg/myrepo
```

```
I need release notes comparing v1.5.0 to v1.4.0 from https://gitlab.com/mygroup/myproject
```

### What You'll Be Asked

The workflow will guide you to provide:

1. **Current version tag** (required)
   - Example: `v1.0.0`, `2.0.0`, `v1.5.0-beta`

2. **Previous version tag** (optional - auto-detected if omitted)
   - Example: `v0.9.0`
   - If not provided, automatically finds the tag before current version

3. **Repository** (choose one):
   - **Remote URL**: `repo_url="https://github.com/owner/repo"` (GitHub/GitLab)
   - **Local path**: `repo_path="/path/to/repository"` (local repos)

4. **Authentication** (optional but recommended):
   - `github_token` for GitHub repos (increases rate limits, required for private repos)
   - `gitlab_token` for GitLab repos (required for private repos)

## Output

All generated files are saved to `artifacts/release-notes/`:

```
artifacts/release-notes/
├── RELEASE_NOTES_v1.0.0.md    # AI-generated release notes
└── commits_v1.0.0.json        # Raw commit data for reference
```

## Example Output

Unlike pattern-based tools that force changes into predefined categories, Claude creates categories that actually make sense for your release:

```markdown
# v1.0.0 Release Notes

**Release Date:** April 12, 2026
**Previous Version:** v0.9.0
**Repository:** https://github.com/owner/repo

[View Full Changelog](https://github.com/owner/repo/compare/v0.9.0...v1.0.0)

---

## ⚠️ Breaking Changes

**Authentication System Redesign**
- Complete rewrite of authentication architecture (#156)
- JWT tokens now expire after 1 hour (previously 24 hours) (#178)
- Removed deprecated `/auth/login` endpoint - use `/v2/auth/login` (#189)

**Impact:** Review authentication flows before upgrading. Migration guide: [link]

## 🔒 Security Updates

- Fixed SQL injection vulnerability in search (#145) - **Critical**
- Updated dependencies with known CVEs (#167)
- Implemented rate limiting on auth endpoints (#178)

## 🎉 New Features

### Real-time Collaboration
- WebSocket support for live updates (#123)
- Presence indicators showing active users (#134)
- Conflict resolution for concurrent edits (#145)

### Developer Experience
- Hot module reloading in development (#156)
- Improved error messages with stack traces (#167)
- Interactive API documentation (#189)

## 🐛 Bug Fixes

### Critical
- **Memory leak**: Fixed WebSocket connection leak in long-running servers (#134)
- **Race condition**: Resolved auth middleware concurrency issue (#178)

### Minor
- Corrected timezone handling in date picker (#142)
- Fixed typo in welcome email template (#155)

## ⚡ Performance Improvements

- Optimized database queries (40% faster on large datasets) (#167)
- Implemented caching layer for API responses (#178)
- Reduced bundle size by 30% through code splitting (#189)

## 📊 Release Statistics

- **Total Commits:** 42
- **Contributors:** 8
- **Pull Requests:** 35
- **Breaking Changes:** 3
- **Security Fixes:** 3
```

## Why AI Categorization is Better

### Pattern Matching (Old Way)
```python
if "feat:" in message:
    category = "Features"
elif "fix:" in message:
    category = "Bug Fixes"
```

**Problems:**
- Misses commits without conventional format
- Can't understand context
- Forces everything into predefined buckets
- "refactor: auth" → "Enhancements" (even if it's breaking)

### AI Analysis (Our Way)
```
Claude reads: "refactor: complete authentication system rewrite"
Claude thinks: Major architectural change, likely breaking
Claude creates: ⚠️ Breaking Changes > Authentication System Redesign
Claude explains: Why this is breaking and what users need to know
```

**Benefits:**
- Understands ALL commits (conventional format not required)
- Recognizes context and importance
- Creates relevant categories per release
- Groups related changes intelligently

## Commit Message Best Practices

While Claude can understand any commit format, conventional commits make categorization even better:

### Recommended Format
```
feat: Add user authentication
fix: Resolve login timeout
BREAKING CHANGE: Remove legacy API
feat(api): Add GraphQL endpoint
```

### Claude Also Understands
```
Add user authentication feature
Resolve login timeout issue
Remove legacy API (breaking)
Implement new GraphQL endpoint
```

### Include PR Numbers
```
feat: Add dark mode (#123)
fix: Memory leak in cache (#456)
```

## Technical Details

### Tools Used

**MCP Tool:** [utility-mcp-server](https://github.com/realmcpservers/utility-mcp-server) v0.2.0+
- Fetches commits from GitHub/GitLab/local repos
- Validates tags exist
- Auto-detects previous version tag
- Extracts PR/MR numbers

**AI Agent:** Claude (running in Ambient Code Platform)
- Analyzes commit context
- Creates dynamic categories
- Formats professional release notes

### Requirements

- **For Remote Repos:**
  - Repository URL (GitHub or GitLab)
  - Optional: API token (recommended for private repos)
  - No local clone needed!

- **For Local Repos:**
  - Git repository with tags
  - Git CLI available
  - Path to repository

### Automatic Installation

The workflow automatically installs the required `utility-mcp-server` package if not already present. No manual setup required!

## Troubleshooting

### Tag Not Found

**Problem**: "Tag 'v1.0.0' does not exist in repository"

**Solutions**:
- List available tags: `git tag -l` (local) or check GitHub/GitLab releases
- Verify tag name matches exactly (including `v` prefix)
- Create tag if needed: `git tag v1.0.0`

### Auto-detection Failed

**Problem**: "Could not auto-detect previous tag"

**Solutions**:
- Provide `previous_version` explicitly
- Check if repository has at least 2 tags
- For first release, there's no previous tag (expected)

### Private Repository Access

**Problem**: "Permission denied" or "Not found"

**Solutions**:
- Provide `github_token` or `gitlab_token`
- Verify token has repo read permissions
- For GitHub: set `GITHUB_TOKEN` environment variable
- For GitLab: set `GITLAB_TOKEN` environment variable

### No Commits Found

**Problem**: "No commits found between tags"

**Solutions**:
- Verify tag order (current should be newer than previous)
- Check tags exist: `git log v0.9.0..v1.0.0 --oneline`
- Ensure you're using the correct repository

## Examples

### Example 1: GitHub Repository
```
User: Generate release notes for v1.0.0 from https://github.com/owner/repo

Workflow:
1. Fetches commits from GitHub API (no clone)
2. Auto-detects previous version (v0.9.0)
3. Claude analyzes all commits
4. Creates dynamic categories based on changes
5. Formats professional release notes
6. Saves to artifacts/release-notes/
```

### Example 2: GitLab Private Repository
```
User: Create notes for v2.0.0 from https://gitlab.com/group/private-repo

Workflow:
1. Uses GITLAB_TOKEN for authentication
2. Fetches commits via GitLab API
3. Extracts MR numbers (!123 format)
4. Claude categorizes intelligently
5. Generates notes with GitLab links
```

### Example 3: Local Repository
```
User: Generate release notes for v1.5.0 from /path/to/repo

Workflow:
1. Uses local git commands
2. Auto-detects v1.4.0 as previous tag
3. Extracts commits between tags
4. Claude analyzes and categorizes
5. Creates professional output
```

## Advanced Features

### Two Output Modes (formatted_output parameter)

**AI-Powered Mode (formatted_output=False - Default)**

Best for this workflow - AI analyzes and categorizes intelligently:

```python
generate_release_notes(
    version="v1.0.0",
    repo_url="https://github.com/owner/repo",
    formatted_output=False  # Default - AI-powered categorization
)
```

**Result**: Raw commits + AI instructions → Claude creates dynamic categories

**Pre-Formatted Mode (formatted_output=True - For IDE testing)**

For quick testing in Cursor or VS Code:

```python
generate_release_notes(
    version="v1.0.0",
    repo_url="https://github.com/owner/repo",
    formatted_output=True  # Pre-formatted output
)
```

**Result**: Pre-formatted markdown with 10 automatic categories:
- ⚠️ Breaking Changes, 🔒 Security Updates, 🎉 New Features, 🐛 Bug Fixes
- ⚡ Performance, 📚 Documentation, 🔄 Refactoring, 🧪 Testing
- 🔧 Chores, 📦 Other Changes

**When to use each mode:**

| Use Case | Mode | Why |
|----------|------|-----|
| This AI workflow | formatted_output=False | Intelligent, context-aware categorization |
| Direct IDE testing | formatted_output=True | Quick output, no AI analysis needed |
| Custom categories | formatted_output=False | Dynamic categories based on actual changes |
| Standard categories | formatted_output=True | Fixed 10 categories, automatic |

**Note**: This workflow always uses `formatted_output=False` for AI-powered categorization. Only use `formatted_output=True` if explicitly testing the tool directly in an IDE.

### Auto-detect Previous Tag

Don't remember the previous version? No problem:

```python
# Just provide current version
generate_release_notes(
    version="v1.0.0",
    repo_url="https://github.com/owner/repo"
)

# Tool automatically finds v0.9.0 (or whatever comes before v1.0.0)
```

### Remote Repository (No Clone)

Work with any GitHub/GitLab repo without cloning:

```python
# GitHub
generate_release_notes(
    version="v1.0.0",
    repo_url="https://github.com/owner/repo",
    github_token=os.getenv('GITHUB_TOKEN')
)

# GitLab
generate_release_notes(
    version="v2.0.0",
    repo_url="https://gitlab.com/group/project",
    gitlab_token=os.getenv('GITLAB_TOKEN')
)
```

### PR/MR Number Extraction

Automatically extracts pull/merge request numbers:

- GitHub: `#123`, `(#123)`, `Merge pull request #123`
- GitLab: `!123`, `(!123)`, `Merge request !123`
- Returns: `"Not Found"` if no PR/MR reference

## Tips for Better Release Notes

1. **Trust Claude's Categorization**
   - Claude understands context better than regex
   - Review the categories - they'll make sense for your release
   - Edit if needed, but Claude usually gets it right

2. **Provide Repository URL**
   - Enables clickable PR and commit links
   - Generates compare URL
   - Makes release notes more interactive

3. **Use Tokens for Private Repos**
   - Required for private repositories
   - Recommended for public (higher rate limits)
   - Set as environment variables for convenience

4. **Write Descriptive Commits**
   - Claude can work with any format
   - More context = better categorization
   - Include "why" not just "what"

## Support

- Report workflow issues: [ambient-code/workflows](https://github.com/ambient-code/workflows)
- Report MCP tool issues: [utility-mcp-server](https://github.com/realmcpservers/utility-mcp-server)
- Check examples: [workflows repository](https://github.com/ambient-code/workflows)

## License

This workflow is part of the Ambient Code Platform workflows collection.
