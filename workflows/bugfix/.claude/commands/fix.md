# /fix - Implement Bug Fix

## Purpose
Implement the bug fix based on the root cause analysis, following project best practices and coding standards. This phase focuses on creating a minimal, correct, and maintainable fix.

## Prerequisites
- Completed root cause analysis (from `/diagnose`)
- Understanding of the recommended fix approach
- Access to modify code and create branches

## Process

1. **Review Fix Strategy**
   - Read the root cause analysis and recommended approach
   - Confirm you understand the fix completely
   - Consider alternative solutions and their trade-offs
   - Plan for backward compatibility if needed
   - Identify any configuration or migration requirements

2. **Create Feature Branch**
   - Ensure you're on the correct base branch (usually `main`)
   - Create a descriptive branch: `bugfix/issue-{number}-{short-description}`
   - Example: `bugfix/issue-425-status-update-retry`
   - Verify you're on the new branch before making changes

3. **Implement Core Fix**
   - Write the minimal code necessary to fix the bug
   - Follow project coding standards and conventions
   - Add appropriate error handling and validation
   - Include inline comments explaining **why** the fix works, not just **what** it does
   - Reference the issue number in comments (e.g., `// Fix for #425: add retry logic`)

4. **Address Related Code**
   - Fix similar patterns identified in root cause analysis
   - Update affected function signatures if necessary
   - Ensure consistency across the codebase
   - Consider adding defensive programming where appropriate

5. **Update Documentation**
   - Update inline code documentation
   - Modify API documentation if interfaces changed
   - Update configuration documentation if settings changed
   - Note any breaking changes clearly

6. **Pre-commit Quality Checks**
   - Run code formatters (e.g., `gofmt`, `black`, `prettier`)
   - Run linters and fix all warnings (e.g., `golangci-lint`, `flake8`, `eslint`)
   - Ensure code compiles/builds without errors
   - Check for any new security vulnerabilities introduced
   - Verify no secrets or sensitive data added

7. **Document Implementation**
   - Create `artifacts/bugfix/fixes/implementation-notes.md`
   - Describe what was changed and why
   - Reference all modified files with file:line notations
   - Note any technical debt or follow-up work needed

## Output

- **Modified code files**: Bug fix implementation in working tree
- **Implementation notes**: `artifacts/bugfix/fixes/implementation-notes.md` containing:
  - Summary of changes
  - Files modified with file:line references
  - Rationale for implementation choices
  - Any technical debt or TODOs
  - Breaking changes (if any)
  - Migration steps (if needed)

## Usage Examples

**After diagnosis:**
```
/fix
```

**With specific instruction:**
```
/fix Implement retry logic with exponential backoff in the status update handler
```

**Output example:**
```
✓ Bug fix implemented
✓ Modified files:
  - operator/handlers/sessions.go:334 (added retry logic)
  - operator/handlers/helpers.go:89 (new retry helper function)
✓ Ran formatters: gofmt, golangci-lint
✓ All linters passed
✓ Created: artifacts/bugfix/fixes/implementation-notes.md

Next steps:
- Run /test to verify the fix and create regression tests
- Review the implementation notes
- Consider if any similar patterns need fixing
```

## Project-Specific Guidelines

**For Go projects:**
- Run: `gofmt -w .` then `golangci-lint run`
- Follow error handling patterns: return errors, don't panic
- Use table-driven tests for test coverage

**For Python projects:**
- Run: `black .`, `isort .`, `flake8 .`
- Use virtual environments
- Follow PEP 8 style guide

**For JavaScript/TypeScript projects:**
- Run: `npm run lint:fix` or `prettier --write .`
- Use TypeScript strict mode
- Avoid `any` types

## Notes

- **Keep fixes minimal** - only change what's necessary to fix the bug
- **Don't combine refactoring with bug fixes** - separate concerns into different commits
- **Reference the issue number** in code comments for future context
- **Consider backward compatibility** - avoid breaking changes when possible
- **Document trade-offs** - if you chose one approach over another, explain why
- Amber will automatically bring in appropriate specialists (Stella for complex fixes, Taylor for straightforward implementations, security braintrust for security implications, etc.) based on the fix complexity
