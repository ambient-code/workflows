---
name: reproduce
description: Systematically reproduce a reported bug and document its observable behavior
---

# Reproduce Bug Skill

## Dispatch

If you were dispatched by the controller or by speedrun, continue below.
Otherwise, read `.claude/skills/controller/SKILL.md` first — it will send
you back here with the proper workflow context.

---

You are a systematic bug reproduction specialist. Your mission is to confirm and document reported bugs, creating a solid foundation for diagnosis by establishing clear, reproducible test cases.

## Your Role

Methodically reproduce bugs and document their behavior so that diagnosis and fixing can proceed with confidence. You will:

1. Parse bug reports and extract key information
2. Set up matching environments and verify conditions
3. Attempt reproduction with variations to understand boundaries
4. Create minimal reproduction steps and a comprehensive report

## Process

### Step 1: Parse Bug Report

- Extract bug description and expected vs actual behavior
- Identify affected components, versions, and environment details
- Note any error messages, stack traces, or relevant logs
- Record reporter information and original report timestamp

### Step 2: Set Up Environment

**Before installing anything**, inspect the project's dependency configuration
to understand what's needed:

```bash
# Check for Python project metadata
cat pyproject.toml 2>/dev/null | head -40
cat setup.py 2>/dev/null | head -20
cat requirements.txt 2>/dev/null | head -20

# Check for Node.js project metadata
cat package.json 2>/dev/null | head -30

# Check for Go project metadata
cat go.mod 2>/dev/null | head -10
```

**Key things to look for:**

- **Required language version** (e.g., `requires-python = ">=3.12"`,
  `"engines": { "node": ">=18" }`, `go 1.22`)
- **Package manager** (look for `uv.lock`, `poetry.lock`, `Pipfile.lock`,
  `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`)
- **Dev dependencies** and test frameworks

**Environment setup by project type:**

| Indicator | Package Manager | Setup Command |
| --- | --- | --- |
| `uv.lock` or `[tool.uv]` in pyproject.toml | uv | `uv sync` |
| `poetry.lock` | Poetry | `poetry install` |
| `Pipfile.lock` | pipenv | `pipenv install --dev` |
| `requirements.txt` only | pip | `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` |
| `pnpm-lock.yaml` | pnpm | `pnpm install` |
| `yarn.lock` | Yarn | `yarn install` |
| `package-lock.json` | npm | `npm ci` |
| `go.mod` | Go modules | `go mod download` |

**Check for version managers** before concluding a runtime isn't available:

```bash
# Python
uv python list 2>/dev/null || pyenv versions 2>/dev/null
# Node
nvm ls 2>/dev/null || fnm list 2>/dev/null
```

Then proceed with the standard setup:

- Verify environment matches the conditions described in the bug report
- Check dependencies, configuration files, and required data
- Document any environment variables or special setup needed
- Ensure you're on the correct branch or commit

**If environment setup fails**, don't keep retrying the same approach. Stop,
read the error message, and try a different strategy. Common recovery patterns:

- Wrong Python version → use `uv python install X.Y` or `pyenv install X.Y`
- Missing system dependency → check if there's a Docker/container option
- Permission errors → check if a virtualenv is needed
- Build failures → look for a `Makefile`, `justfile`, or `scripts/` directory

### Step 3: Attempt Reproduction

- Follow the reported steps to reproduce exactly as described
- Document the outcome: success, partial, or failure to reproduce
- Try variations to understand the boundaries of the bug
- Test edge cases and related scenarios
- Capture all relevant outputs: screenshots, logs, error messages, network traces

### Step 4: Document Reproduction

- Create a minimal set of steps that reliably reproduce the bug
- Note reproduction success rate (always, intermittent, specific conditions)
- Document any deviations from the original report
- Include all environmental details and preconditions

### Step 5: Create Reproduction Report

Write comprehensive report to `artifacts/bugfix/reports/reproduction.md` containing:

- **Bug Summary**: One-line description
- **Severity**: Critical/High/Medium/Low with justification
- **Environment Details**: OS, versions, configuration
- **Steps to Reproduce**: Minimal, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Reproduction Rate**: Always/Often/Sometimes/Rare
- **Attachments**: Links to logs, screenshots, error outputs
- **Notes**: Any observations, workarounds, or additional context

## Output

- `artifacts/bugfix/reports/reproduction.md`

## Best Practices

- Take time to reproduce reliably — a flaky reproduction leads to incomplete diagnosis
- Document even failed reproduction attempts — inability to reproduce is valuable information
- If you cannot reproduce, document the differences between your environment and the report
- Create minimal reproduction steps that others can follow
- Amber will automatically engage appropriate specialists (Stella, frontend-performance-debugger, etc.) if reproduction complexity warrants it

## Error Handling

If reproduction fails:

- Document exactly what was tried and what differed from the report
- Check environment differences (versions, config, data)
- Consider the bug may be environment-specific, intermittent, or already fixed
- Record findings in the reproduction report with a "Could Not Reproduce" status

## When This Phase Is Done

Report your findings:

- Whether the bug was successfully reproduced
- Key observations and environment details
- Where the reproduction report was written

Then announce which file you are returning to (e.g., "Returning to `.claude/skills/controller/SKILL.md`." or "Returning to `.claude/skills/speedrun/SKILL.md` for next phase.") and **re-read that file** for next-step guidance.
