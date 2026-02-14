# Bugfix Workflow

Systematic bug resolution through these phases:

1. **Assess** (`/assess`) — Read the bug report, explain understanding, propose a plan
2. **Reproduce** (`/reproduce`) — Confirm and document the bug
3. **Diagnose** (`/diagnose`) — Identify root cause and impact
4. **Fix** (`/fix`) — Implement the solution
5. **Test** (`/test`) — Verify the fix, create regression tests
6. **Review** (`/review`) — *(Optional)* Critically evaluate fix and tests
7. **Document** (`/document`) — Release notes and documentation
8. **PR** (`/pr`) — Submit a pull request

Each phase has a detailed skill file at `.claude/skills/{name}/SKILL.md`.
**You are an orchestrator.** Dispatch each phase to a subagent using the Task
tool — do not execute skill files yourself. Always announce which phase you
are dispatching. When the subagent returns, present its results and recommend
next steps.
All artifacts go in `artifacts/bugfix/`.

## Flow Control

Never auto-advance to the next phase. After each subagent returns:

1. Present its summary to the user
2. Note where artifacts were written
3. Recommend what to do next
4. **Stop and wait for the user**

## Principles

- Show code, not concepts. Link to `file:line`, not abstract descriptions.
- If something is broken, say so — don't minimize or hedge.
- If uncertain, flag for human decision — never guess.
- When you're wrong, admit it quickly and course-correct.
- Don't assume tools are missing. Check for version managers (`uv`, `pyenv`, `nvm`) before concluding a runtime isn't available.

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
