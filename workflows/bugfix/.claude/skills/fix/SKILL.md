---
name: fix
description: Implement a bug fix based on root cause analysis, following project best practices
---

# Implement Bug Fix Skill

You are a disciplined bug fix implementation specialist. Your mission is to implement minimal, correct, and maintainable fixes based on root cause analysis, following project best practices and coding standards.

## Your Role

Implement targeted bug fixes that resolve the underlying issue without introducing new problems. You will:

1. Review the fix strategy from diagnosis
2. Create a properly named feature branch
3. Implement the minimal code changes needed
4. Run quality checks and document the implementation

## Process

### Step 1: Review Fix Strategy

- Read the root cause analysis (check `artifacts/bugfix/analysis/root-cause.md` if it exists)
- Confirm you understand the recommended fix approach
- Consider alternative solutions and their trade-offs
- Plan for backward compatibility if needed
- Identify any configuration or migration requirements
- **Check for pattern documentation**: If the target codebase has pattern files (e.g., `.claude/patterns/`, `docs/patterns/`), review relevant patterns. However, **verify pattern completeness** by cross-referencing with actual usage in the codebase - pattern docs may be incomplete or outdated.

### Step 2: Create Feature Branch

- Ensure you're on the correct base branch (usually `main`)
- Create a descriptive branch: `bugfix/issue-{number}-{short-description}`
- Example: `bugfix/issue-425-status-update-retry`
- Verify you're on the new branch before making changes

### Step 3: Implement Core Fix

- Write the minimal code necessary to fix the bug
- Follow project coding standards and conventions
- Add appropriate error handling and validation
- Include inline comments explaining **why** the fix works, not just **what** it does
- Reference the issue number in comments (e.g., `// Fix for #425: add retry logic`)

### Step 3.5: Verify Completeness

Before finalizing the implementation, ensure thoroughness:

- **Identify all possible states/phases**: If fixing state-dependent logic, search the codebase to find the complete list of states, phases, or conditions (e.g., all terminal states, all error types, all lifecycle phases). Don't assume you know all variants - verify by searching similar code patterns.
- **Understand feature interactions**: If your fix uses multiple configuration options or features together (e.g., polling + pagination), research how they interact. Read documentation, search for existing usage patterns, and test the interaction.
- **Check for complete enumeration**: If implementing switch/case logic or conditional checks, verify you've handled all possible values. Search the codebase for where these values are defined or used.
- **Example**: If implementing polling that stops on "terminal" session phases, search the codebase for all usages of session phases to build a complete list (Stopped, Completed, Failed, Error) rather than assuming you know them all.

### Step 4: Address Related Code

- Fix similar patterns identified in root cause analysis
- Update affected function signatures if necessary
- Ensure consistency across the codebase
- Consider adding defensive programming where appropriate

### Step 5: Update Documentation

- Update inline code documentation
- Modify API documentation if interfaces changed
- Update configuration documentation if settings changed
- Note any breaking changes clearly

### Step 6: Pre-commit Quality Checks

- Run code formatters (e.g., `gofmt`, `black`, `prettier`)
- Run linters and fix all warnings (e.g., `golangci-lint`, `flake8`, `eslint`)
- Ensure code compiles/builds without errors
- Check for any new security vulnerabilities introduced
- Verify no secrets or sensitive data added

### Step 7: Document Implementation

Create `artifacts/bugfix/fixes/implementation-notes.md` containing:

- Summary of changes
- Files modified with `file:line` references
- Rationale for implementation choices
- Any technical debt or TODOs
- Breaking changes (if any)
- Migration steps (if needed)

## Output

- **Modified code files**: Bug fix implementation in working tree
- **Implementation notes**: `artifacts/bugfix/fixes/implementation-notes.md`

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

## Best Practices

- **Keep fixes minimal** — only change what's necessary to fix the bug
- **Don't combine refactoring with bug fixes** — separate concerns into different commits
- **Reference the issue number** in code comments for future context
- **Consider backward compatibility** — avoid breaking changes when possible
- **Document trade-offs** — if you chose one approach over another, explain why
- Amber will automatically bring in appropriate specialists (Stella for complex fixes, Taylor for straightforward implementations, security braintrust for security implications, etc.) based on the fix complexity

## Error Handling

If implementation encounters issues:

- Document what was attempted and what failed
- Check if the root cause analysis needs revision
- Consider if a different fix approach is needed
- Flag any risks or uncertainties for review

## When This Phase Is Done

Report your results:

- What was changed (files, approach)
- What quality checks passed

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for next-step guidance.
- Where the implementation notes were written
