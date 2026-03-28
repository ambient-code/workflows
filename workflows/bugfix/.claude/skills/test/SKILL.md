---
name: test
description: Verify a bug fix with comprehensive testing and create regression tests to prevent recurrence
---

# Test & Verify Fix Skill

## Dispatch

If you were dispatched by the controller or by speedrun, continue below.
Otherwise, read `.claude/skills/controller/SKILL.md` first — it will send
you back here with the proper workflow context.

---

You are a thorough testing and verification specialist. Your mission is to verify that a bug fix works correctly and create comprehensive tests to prevent regression, ensuring the fix resolves the issue without introducing new problems.

## Your Role

Systematically verify fixes and build test coverage that prevents recurrence. You will:

1. Create regression tests that prove the fix works
2. Run comprehensive unit and integration tests
3. Perform manual verification of the original reproduction steps
4. Validate performance and security impact

## Process

### Step 1: Survey Existing Test Patterns

Before writing any tests, examine how the project already tests its code.
This prevents style clashes and ensures you use the right tools.

- **Identify the test framework and runner:**

```bash
# Check for test configuration
cat pytest.ini 2>/dev/null || cat setup.cfg 2>/dev/null | head -20
cat jest.config.* 2>/dev/null || cat vitest.config.* 2>/dev/null
cat *_test.go 2>/dev/null | head -5
```

- **Read 2-3 existing test files** in the same area of the codebase as your
  fix. Look for:
  - How tests are structured (arrange/act/assert, BDD, table-driven)
  - What assertion style is used (`assert`, `expect`, `require`)
  - What mocking approach is used (fixtures, factories, `unittest.mock`,
    `jest.mock`, `testify/mock`)
  - Whether there are shared test helpers, fixtures, or utilities
  - How tests are named (conventions for test functions and descriptions)

- **Check for existing test fixtures and helpers:**

```bash
# Common locations for test utilities
ls tests/conftest.py 2>/dev/null
ls tests/helpers/ 2>/dev/null || ls tests/utils/ 2>/dev/null
ls tests/fixtures/ 2>/dev/null
ls __tests__/setup.* 2>/dev/null
```

- **Prefer project infrastructure over generic approaches:**
  - If the project has a `CliRunner` fixture → use it instead of `capsys`
  - If the project has factory functions → use them instead of raw constructors
  - If the project uses `httpx` test client → don't switch to `requests`

### Step 2: Create Regression Test

- Write a test that reproduces the original bug
- Verify the test **fails** without your fix (proves it catches the bug)
- Verify the test **passes** with your fix (proves the fix works)
- Use descriptive test names that reference the issue (e.g., `TestStatusUpdateRetry_Issue425`)
- **Match the style of existing tests** — use the same assertion patterns,
  mock strategies, and naming conventions you found in Step 1
- Prefer modern, readable APIs over legacy patterns:
  - Python: use `call_args.args[0]` over `call_args[0][0]` (tuple indexing)
  - Use framework-specific test utilities over generic ones
  - Use named parameters over positional where the API supports it

### Step 3: Unit Testing

- Test the specific functions/methods that were modified
- Cover all code paths in the fix
- Test edge cases identified during diagnosis
- Test error handling and validation logic
- Aim for high coverage of changed code
- **Test all states/phases/conditions**: If the fix involves state-dependent logic, ensure tests cover ALL possible states, not just the common ones. For example, if fixing polling that stops on terminal phases, test all terminal phases (Stopped, Completed, Failed, Error), not just one or two.
- **Test feature interactions**: If the fix involves multiple interacting features or configurations, test their combinations (e.g., pagination + polling together, not separately)

### Step 4: Integration Testing

- Test the fix in realistic scenarios with dependent components
- Verify end-to-end behavior matches expectations
- Test interactions with databases, APIs, or external systems
- Ensure the fix works in the full system context

### Step 5: Run the Full Test Suite (MANDATORY)

This step is not optional. Do not skip it. Do not run only your new tests.

- Run the **entire** test suite — unit tests, integration tests, and E2E tests:

```bash
# Run everything. Don't cherry-pick.
pytest tests/                          # Python
npm test                               # Node.js
go test ./...                          # Go
```

- If the project has separate test directories (e.g., `tests/unit/`,
  `tests/e2e/`, `tests/integration/`), run ALL of them.
- **Why this matters:** Your fix may break tests in unrelated areas. A config
  validation change can break an E2E test that uses a mock config. A new
  import can cause a circular dependency. These failures will surface in CI —
  catch them here instead.
- If tests fail, investigate whether:
  - The test was wrong (update it)
  - The fix broke something (revise the fix)
  - Test needs updating due to intentional behavior change (document it)
- **Do not proceed to the next step until the full suite passes.** If you
  cannot get all tests passing, document the failures clearly.

### Step 6: Lint and Format All Modified Files

Run the project's formatters and linters on **every file you've touched** —
both source files and test files. Test code must meet the same formatting
standards as production code.

```bash
# Identify all modified files
git diff --name-only HEAD

# Then run the appropriate formatters on ALL of them:
# Python:  black FILE1 FILE2 ... && isort FILE1 FILE2 ... && ruff check --fix FILE1 FILE2 ...
# Node.js: npx prettier --write FILE1 FILE2 ... && npx eslint --fix FILE1 FILE2 ...
# Go:      gofmt -w FILE1 FILE2 ...
```

If the project has a pre-commit hook or a `make lint` / `npm run lint:fix`
target, use that instead — it will apply all configured checks at once.

**Why this is a separate step:** It's common to run formatters after writing
source code in `/fix` but forget to re-run them after writing test code in
`/test`. This step ensures both are covered.

### Step 7: Manual Verification

- Manually execute the original reproduction steps from the reproduction report
- Verify the expected behavior is now observed
- Test related functionality to ensure no side effects
- Test in multiple environments if applicable (dev, staging)

### Step 8: Performance Validation

- If the fix touches performance-sensitive code, measure impact
- Profile before/after if the bug was performance-related
- Ensure no performance degradation introduced
- Document any performance changes in test report

### Step 9: Security Check

- Verify the fix doesn't introduce security vulnerabilities
- Check for common issues: SQL injection, XSS, CSRF, etc.
- Ensure error messages don't leak sensitive information
- Validate input handling and sanitization

### Step 10: Document Test Results

Create comprehensive test report at `artifacts/bugfix/tests/verification.md` containing:

- **Test Summary**: Overview of testing performed
- **Regression Test**: Location and description of new test(s)
- **Unit Test Results**: Pass/fail status, coverage metrics
- **Integration Test Results**: End-to-end validation results
- **Full Suite Results**: Status of all project tests
- **Manual Testing**: Steps performed and observations
- **Performance Impact**: Before/after metrics (if applicable)
- **Security Review**: Findings from security check
- **Known Limitations**: Any edge cases not fully addressed
- **Recommendations**: Follow-up work or monitoring needed

### Step 11: Report Results to the User

After writing `artifacts/bugfix/tests/verification.md`:

1. **Tell the user where the file was written** — include the full path
2. **Summarize the results inline** — don't make the user open the file to find out what happened. Include at minimum:
   - Overall pass/fail status
   - Number of tests run, passed, and failed
   - Any new regression tests added (file and test name)
   - Any failures or concerns that need attention
   - Recommended next steps (proceed to `/document`, revisit `/fix`, etc.)

## Output

- New test files in the project repository
- `artifacts/bugfix/tests/verification.md`

## Project-Specific Testing Commands

**Go projects:**

```bash
go test ./... -v                    # Run all tests
go test -cover ./...                # With coverage
go test -race ./...                 # Race detection
```

**Python projects:**

```bash
pytest tests/                       # Run all tests
pytest --cov=. tests/               # With coverage
pytest -v tests/test_bugfix.py      # Specific test
```

**JavaScript/TypeScript projects:**

```bash
npm test                            # Run all tests
npm run test:coverage               # With coverage
npm test -- --watch                 # Watch mode
```

## Best Practices

- **Regression tests are mandatory** — every bug fix must include a test that would catch recurrence
- **Test the test** — verify your new test actually fails without the fix
- **Don't skip the full suite** — even if unit tests pass, integration might reveal issues
- **Manual testing matters** — automated tests don't always catch UX issues
- **Document failed tests** — if tests fail, that's valuable information
- Amber will automatically engage testing specialists (Neil for comprehensive strategies, sre-reliability-engineer for infrastructure testing, secure-software-braintrust for security testing, etc.) based on testing complexity and domain requirements

## Error Handling

If tests fail unexpectedly:

- Determine if the failure is in the new test or an existing test
- Check if the fix introduced a regression
- Document all failures with details for investigation
- Consider if the fix approach needs revision

## When This Phase Is Done

Report your results:

- How many tests were added and their results
- Whether the full test suite passes
- Where the verification report was written

Then announce which file you are returning to (e.g., "Returning to `.claude/skills/controller/SKILL.md`." or "Returning to `.claude/skills/speedrun/SKILL.md` for next phase.") and **re-read that file** for next-step guidance.
