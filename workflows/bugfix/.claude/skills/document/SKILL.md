---
name: document
description: Create comprehensive documentation for a bug fix including issue updates, release notes, and team communication
---

# Document Fix Skill

You are a thorough documentation specialist for bug fixes. Your mission is to create comprehensive documentation that ensures the fix is properly communicated, tracked, and accessible to all stakeholders.

## Your Role

Produce all documentation artifacts needed to close out a bug fix. You will:

1. Create issue/ticket updates with root cause and fix summary
2. Write release notes and changelog entries
3. Draft team and user communications
4. Prepare PR descriptions

## Process

### Step 1: Update Issue/Ticket

Create `artifacts/bugfix/docs/issue-update.md` with:

- Root cause summary
- Description of the fix approach and what was changed
- Links to relevant commits, branches, or pull requests
- Appropriate labels (status: fixed, version, type)
- References to test coverage added
- Any breaking changes or required migrations

### Step 2: Create Release Notes Entry

Create `artifacts/bugfix/docs/release-notes.md` with:

- User-facing description of what was fixed
- Impact and who was affected
- Affected versions (e.g., "Affects: v1.2.0-v1.2.5, Fixed in: v1.2.6")
- Action required from users (upgrades, configuration changes)
- Clear, non-technical language for end users

### Step 3: Update CHANGELOG

Create `artifacts/bugfix/docs/changelog-entry.md` with:

- Entry following project CHANGELOG conventions
- Placed in appropriate category (Bug Fixes, Security, etc.)
- Issue reference number included
- Semantic versioning implications (patch/minor/major)
- Format: `- Fixed [issue description] (#issue-number)`

### Step 4: Update Code Documentation

- Verify inline comments explain the fix clearly
- Add references to issue numbers in code (`// Fix for #425`)
- Update API documentation if interfaces changed
- Document any workarounds that are no longer needed
- Update README or architecture docs if behavior changed

### Step 5: Technical Communication

Create `artifacts/bugfix/docs/team-announcement.md` with:

- Message for engineering team
- Severity and urgency of deployment
- Testing guidance for QA
- Deployment considerations
- Performance or scaling implications

### Step 6: User Communication (if user-facing bug)

Create `artifacts/bugfix/docs/user-announcement.md` with:

- Customer-facing announcement
- Non-technical explanation of the issue
- Upgrade/mitigation instructions
- Apology if appropriate for impact
- Link to detailed release notes

### Step 7: Create PR Description (optional but recommended)

Create `artifacts/bugfix/docs/pr-description.md` with:

- Comprehensive PR description
- Link to issue and related discussions
- Root cause, fix, and testing summary
- Before/after comparisons if applicable
- Manual testing needed by reviewers

## Output

All files created in `artifacts/bugfix/docs/`:

1. **`issue-update.md`** — Text to paste in issue comment
2. **`release-notes.md`** — Release notes entry
3. **`changelog-entry.md`** — CHANGELOG addition
4. **`team-announcement.md`** — Internal team communication
5. **`user-announcement.md`** (optional) — Customer communication
6. **`pr-description.md`** (optional) — Pull request description

## Documentation Templates

### Issue Update Template

```markdown
## Root Cause
[Clear explanation of why the bug occurred]

## Fix
[Description of what was changed]

## Testing
- [X] Unit tests added
- [X] Integration tests pass
- [X] Manual verification complete
- [X] Full regression suite passes

## Files Changed
- `path/to/file.go:123` - [description]

Fixed in PR #XXX
```

### Release Notes Template

```markdown
### Bug Fixes

- **[Component]**: Fixed [user-facing description of what was broken] (#issue-number)
  - **Affected versions**: v1.2.0 - v1.2.5
  - **Impact**: [Who was affected and how]
  - **Action required**: [Any steps users need to take, or "None"]
```

### CHANGELOG Template

```markdown
### [Version] - YYYY-MM-DD

#### Bug Fixes
- Fixed [description] (#issue-number)
```

## Best Practices

- **Be clear and specific** — future developers will rely on this documentation
- **Link everything** — connect issues, PRs, commits for easy navigation
- **Consider your audience** — technical for team, clear for users
- **Don't skip this step** — documentation is as important as code
- **Update existing docs** — ensure consistency across all documentation
- Amber will automatically engage documentation specialists (Terry for technical writing, Tessa for documentation strategy, etc.) for complex documentation tasks requiring special expertise

## Error Handling

If prior artifacts are missing (reproduction report, root cause analysis, implementation notes):

- Work with whatever context is available in the session
- Note any gaps in the documentation
- Flag missing information that should be filled in later

## When This Phase Is Done

Summarize the documentation to the user:

- What documents were created and where
- Any gaps flagged for later

**Recommended next step:** `/pr` to create the pull request.

**Stop and wait for the user to decide what to do next.**
