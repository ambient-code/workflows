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

### Step 2: Create Feature Branch

- Ensure you're on the correct base branch (usually `main`)
- Create a descriptive branch: `bugfix/issue-{number}-{short-description}`
- Example: `bugfix/issue-425-status-update-retry`
- Verify you're on the new branch before making changes

### Step 3: Research Implementation Patterns

**CRITICAL: Before writing any code, research how similar functionality is already implemented.**

- **Search for existing patterns**: Use Grep to find similar implementations in the codebase
  - Example: If fixing polling logic, search for other polling implementations
  - Example: If working with state machines, find all state definitions
- **Identify all possible states/cases**: When working with state-based logic, enumerate ALL possible states by searching the codebase
  - Example: If handling session phases, grep for ALL phase constants/enums, not just the ones mentioned in the bug
  - Don't assume - verify by checking actual usage in the codebase
- **Understand feature interactions**: When combining multiple features (e.g., polling + pagination), research how they interact
  - Read relevant documentation (official docs for libraries/frameworks)
  - Search for existing code that combines these features
  - Look for comments or patterns that explain interaction behavior
- **Check for framework-specific gotchas**: If using library features (React Query, Redux, etc.), research edge cases
  - Example: `placeholderData: keepPreviousData` affects what data is available during transitions
  - Example: Polling callbacks may receive stale data during page changes
- **Document your research**: Note what patterns you found and why you're following them (or diverging)

### Step 4: Implement Core Fix

- Write the minimal code necessary to fix the bug
- Follow project coding standards and conventions
- Add appropriate error handling and validation
- Include inline comments explaining **why** the fix works, not just **what** it does
- Reference the issue number in comments (e.g., `// Fix for #425: add retry logic`)

### Step 5: Address Related Code

- Fix similar patterns identified in root cause analysis
- Update affected function signatures if necessary
- Ensure consistency across the codebase
- Consider adding defensive programming where appropriate

### Step 6: Update Documentation

- Update inline code documentation
- Modify API documentation if interfaces changed
- Update configuration documentation if settings changed
- Note any breaking changes clearly

### Step 7: Pre-commit Quality Checks

- Run code formatters (e.g., `gofmt`, `black`, `prettier`)
- Run linters and fix all warnings (e.g., `golangci-lint`, `flake8`, `eslint`)
- Ensure code compiles/builds without errors
- Check for any new security vulnerabilities introduced
- Verify no secrets or sensitive data added

### Step 8: Document Implementation

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
