# Doc Checker Workflow

Documentation completeness review of pull requests. Determines whether a PR
includes all necessary documentation updates when code changes affect
user-facing behavior.

## Scope

This workflow reviews ONLY documentation completeness. It does NOT review:
- Code quality, style, or naming
- Performance or security
- Testing or architecture
- Implementation choices

## How It Works

The `/review-pr` command follows a five-phase analysis:

1. **Gather Context** -- PR metadata, diff inventory, documentation ecosystem
2. **Classify Changes** -- Categorize each change (API, CLI, config, behavioral, new feature, deprecation, or internal-only)
3. **Discover Existing Documentation** -- Find docs that cover affected behavior
4. **Evaluate Coverage** -- Determine if PR includes necessary doc updates
5. **Render Verdict** -- PASS, PASS WITH SUGGESTIONS, or FAIL with findings

## Finding Severities

- **CRITICAL** -- Users will encounter incorrect information or miss essential knowledge
- **MAJOR** -- Documentation is materially incomplete for a meaningful use case
- **MINOR** -- Gap affects edge cases or advanced usage

## Hard Limits

- Do not comment on code quality, style, naming, architecture, or performance
- Do not suggest documentation changes beyond what the diff warrants
- Do not flag internal-only changes as needing documentation
- Do not flag changelog, release notes, or commit message omissions
- Complete all five analysis phases before producing output
