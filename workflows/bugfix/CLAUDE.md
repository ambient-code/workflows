# Bugfix Workflow

Systematic bug resolution through these phases:

1. **Reproduce** (`/reproduce`) — Confirm and document the bug
2. **Diagnose** (`/diagnose`) — Identify root cause and impact
3. **Fix** (`/fix`) — Implement the solution
4. **Test** (`/test`) — Verify the fix, create regression tests
5. **Review** (`/review`) — *(Optional)* Critically evaluate fix and tests
6. **Document** (`/document`) — Release notes and documentation
7. **PR** (`/pr`) — Submit a pull request

Each command delegates to `.claude/skills/{name}/SKILL.md`.
All artifacts go in `artifacts/bugfix/`.

## Flow Control

Never auto-advance to the next phase. At the end of each phase:

1. Summarize what was done and what was found
2. Note where artifacts were written
3. Recommend what to do next
4. **Stop and wait for the user**

## Principles

- Show code, not concepts. Link to `file:line`, not abstract descriptions.
- If something is broken, say so — don't minimize or hedge.
- If uncertain, flag for human decision — never guess.
- When you're wrong, admit it quickly and course-correct.

## Hard Limits

- No direct commits to `main` — always use feature branches
- No token or secret logging — use `len(token)`, redact in logs
- No force-push, hard reset, or destructive git operations
- No modifying security-critical code without human review
- No skipping CI checks (`--no-verify`, `--no-gpg-sign`)

## Safety

- Show your plan with TodoWrite before executing
- Indicate confidence: High (90-100%), Medium (70-89%), Low (<70%)
- Flag risks and assumptions upfront
- Provide rollback instructions for every change

## Quality

- Follow the project's existing coding standards and conventions
- Zero tolerance for test failures — fix them, don't skip them
- Conventional commits: `type(scope): description`
- All PRs include issue reference (`Fixes #123`)

## Escalation

Stop and request human guidance when:

- Root cause is unclear after systematic investigation
- Multiple valid solutions exist with unclear trade-offs
- An architectural decision is required
- The change affects API contracts or introduces breaking changes
- A security or compliance concern arises
- Confidence on the proposed solution is below 80%

## Working With the Project

This workflow gets deployed into different projects. Respect the target project:

- Read and follow the project's own `CLAUDE.md` if one exists
- Adopt the project's coding style, not your own preferences
- Use the project's existing test framework and patterns
- When in doubt about project conventions, check git history and existing code
