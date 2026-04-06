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
9. **Summary** (`/summary`) — Synthesize all artifacts into a final status report

All phases are implemented as skills at `.claude/skills/{name}/SKILL.md`.
The workflow controller at `.claude/skills/controller/SKILL.md` manages phase
transitions and recommendations. The `/speedrun` skill at
`.claude/skills/speedrun/SKILL.md` runs all remaining phases without stopping.
Artifacts go in `artifacts/bugfix/`.

## Principles

- Show code, not concepts. Link to `file:line`, not abstract descriptions.
- If something is broken, say so — don't minimize or hedge.
- If uncertain, flag for human decision — never guess.
- When you're wrong, admit it quickly and course-correct.
- Don't assume tools are missing. Check for version managers (`uv`, `pyenv`, `nvm`) before concluding a runtime isn't available.
- **Be thorough and complete**: When fixing bugs involving states, phases, or conditions, search the codebase to identify the complete set of possible values. Don't assume you know all variants. When features interact (e.g., polling + pagination), research and understand their interactions before implementing.
- **Use available tools and APIs fully**: Before assuming a tool or API is read-only or limited, check its full capabilities. For example, if Jira integration is available, check if you can update tickets directly via API, not just read them. Use tools to their full potential.
- **Check all relevant branches**: When investigating bugs or looking for examples, check both main branch AND release branches (e.g., `rhoai-3.4`, `release-*` patterns). Release branches often contain production code not yet merged to main.
- **DRY principle (Don't Repeat Yourself)**: Before creating new constants, types, or helper functions, search for existing implementations. Check:
  - Existing constant files (e.g., `const.ts`, `constants.py`)
  - Type definition files and barrel exports (e.g., `index.ts`, `types.ts`)
  - Shared utility modules
  - Never duplicate constants or types when a single source of truth exists
- **Understand import restrictions**: Before importing from a path, understand tsconfig/module restrictions. Files at package root may not be able to import from subdirectories if tsconfig excludes them. Check tsconfig.json and existing import patterns before adding new imports.
- **Think through edge cases**: When proposing a fix, analyze all scenarios it affects. A fix that works for the reported case but hides errors in other cases is incomplete. Distinguish between different scenarios (e.g., Helm chart builds vs. container builds) and handle each appropriately.

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
