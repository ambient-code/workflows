# /document - Document Fix

## Purpose
Create comprehensive documentation for the bug fix including issue updates, release notes, changelog entries, and team communication. This ensures the fix is properly communicated and tracked.

## Prerequisites
- Completed fix implementation (from `/fix`)
- Completed testing (from `/test`)
- Understanding of the bug's impact and resolution

## Process

1. **Update Issue/Ticket**
   - Summarize the root cause discovered
   - Describe the fix approach and what was changed
   - Link to relevant commits, branches, or pull requests
   - Add appropriate labels:
     - Status: "fixed", "resolved"
     - Version: "fixed-in-v{version}"
     - Type: "bug", "critical", etc.
   - Include references to test coverage added
   - Mention any breaking changes or required migrations

2. **Create Release Notes Entry**
   - Write user-facing description of what was fixed
   - Explain the impact and who was affected
   - Mention affected versions (e.g., "Affects: v1.2.0-v1.2.5, Fixed in: v1.2.6")
   - Note any action required from users (upgrades, configuration changes)
   - Keep language clear and non-technical for end users
   - Save to `artifacts/bugfix/docs/release-notes.md`

3. **Update CHANGELOG**
   - Add entry following project CHANGELOG conventions
   - Place in appropriate category (Bug Fixes, Security, etc.)
   - Include issue reference number
   - Follow semantic versioning implications (patch/minor/major)
   - Format: `- Fixed [issue description] (#issue-number)`
   - Save to `artifacts/bugfix/docs/changelog-entry.md`

4. **Update Code Documentation**
   - Verify inline comments explain the fix clearly
   - Add references to issue numbers in code (`// Fix for #425`)
   - Update API documentation if interfaces changed
   - Document any workarounds that are no longer needed
   - Update README or architecture docs if behavior changed

5. **Technical Communication**
   - Draft message for engineering team
   - Highlight severity and urgency of deployment
   - Provide testing guidance for QA
   - Mention any deployment considerations
   - Note performance or scaling implications
   - Save to `artifacts/bugfix/docs/team-announcement.md`

6. **User Communication** (if user-facing bug)
   - Draft customer-facing announcement
   - Explain the issue in non-technical terms
   - Provide upgrade/mitigation instructions
   - Apologize if appropriate for impact
   - Link to detailed release notes
   - Save to `artifacts/bugfix/docs/user-announcement.md`

7. **Create PR Description** (optional but recommended)
   - Write comprehensive PR description
   - Link to issue and related discussions
   - Summarize root cause, fix, and testing
   - Include before/after comparisons if applicable
   - List any manual testing needed by reviewers
   - Save to `artifacts/bugfix/docs/pr-description.md`

## Output

Creates the following files in `artifacts/bugfix/docs/`:

1. **`issue-update.md`** - Text to paste in issue comment
   - Root cause summary
   - Fix description
   - Testing performed
   - Links to commits/PRs

2. **`release-notes.md`** - Release notes entry
   - User-facing description
   - Impact and affected versions
   - Action items for users

3. **`changelog-entry.md`** - CHANGELOG addition
   - Formatted for project CHANGELOG
   - Proper category and issue reference

4. **`team-announcement.md`** - Internal team communication
   - Technical details
   - Deployment guidance
   - Testing recommendations

5. **`user-announcement.md`** (optional) - Customer communication
   - Non-technical explanation
   - Upgrade instructions
   - Support information

6. **`pr-description.md`** (optional) - Pull request description
   - Comprehensive PR summary
   - Review guidance
   - Testing checklist

## Usage Examples

**After testing:**
```
/document
```

**With specific context:**
```
/document This is a critical security fix affecting all users
```

**Output example:**
```
✓ Documentation created
✓ Generated artifacts/bugfix/docs/:
  - issue-update.md (ready to paste in #425)
  - release-notes.md (for v1.2.6 release)
  - changelog-entry.md (add to CHANGELOG.md)
  - team-announcement.md (send to #engineering)
  - pr-description.md (use when creating PR)

Summary:
- Bug: Status update failures in operator
- Root cause: Missing retry logic on transient K8s API errors
- Fix: Added exponential backoff retry (3 attempts)
- Impact: High - affects all AgenticSession status updates
- Testing: 12 new tests, full regression passed
- Breaking changes: None

Next steps:
- Paste issue-update.md content into issue #425
- Create pull request with pr-description.md
- Notify team via team-announcement.md
- Add changelog-entry.md to CHANGELOG.md
- Schedule release v1.2.6 with release-notes.md

🎉 Bug fix documentation complete! Ready for PR and deployment.
```

## Documentation Templates

### Issue Update Template:
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

### Release Notes Template:
```markdown
### Bug Fixes

- **[Component]**: Fixed [user-facing description of what was broken] (#issue-number)
  - **Affected versions**: v1.2.0 - v1.2.5
  - **Impact**: [Who was affected and how]
  - **Action required**: [Any steps users need to take, or "None"]
```

### CHANGELOG Template:
```markdown
### [Version] - YYYY-MM-DD

#### Bug Fixes
- Fixed [description] (#issue-number)
```

## Notes

- **Be clear and specific** - future developers will rely on this documentation
- **Link everything** - connect issues, PRs, commits for easy navigation
- **Consider your audience** - technical for team, clear for users
- **Don't skip this step** - documentation is as important as code
- **Update existing docs** - ensure consistency across all documentation
- Amber will automatically engage documentation specialists (Terry for technical writing, Tessa for documentation strategy, etc.) for complex documentation tasks requiring special expertise
