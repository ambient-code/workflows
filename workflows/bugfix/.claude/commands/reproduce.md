# /reproduce - Reproduce Bug

## Purpose
Systematically reproduce the reported bug and document its observable behavior. This creates a solid foundation for diagnosis by establishing a clear, reproducible test case.

## Prerequisites
- Bug report, issue URL, or description of symptoms
- Access to the affected system/codebase
- Required environment or test data (if applicable)

## Process

1. **Parse Bug Report**
   - Extract bug description and expected vs actual behavior
   - Identify affected components, versions, and environment details
   - Note any error messages, stack traces, or relevant logs
   - Record reporter information and original report timestamp

2. **Set Up Environment**
   - Verify environment matches the conditions described in the bug report
   - Check dependencies, configuration files, and required data
   - Document any environment variables or special setup needed
   - Ensure you're on the correct branch or commit

3. **Attempt Reproduction**
   - Follow the reported steps to reproduce exactly as described
   - Document the outcome: success, partial, or failure to reproduce
   - Try variations to understand the boundaries of the bug
   - Test edge cases and related scenarios
   - Capture all relevant outputs: screenshots, logs, error messages, network traces

4. **Document Reproduction**
   - Create a minimal set of steps that reliably reproduce the bug
   - Note reproduction success rate (always, intermittent, specific conditions)
   - Document any deviations from the original report
   - Include all environmental details and preconditions

5. **Create Reproduction Report**
   - Write comprehensive report in `artifacts/bugfix/reports/reproduction.md`
   - Include severity assessment (critical, high, medium, low)
   - Attach or link to all relevant logs and outputs
   - Note any workarounds discovered during reproduction

## Output

Creates `artifacts/bugfix/reports/reproduction.md` containing:

- **Bug Summary**: One-line description
- **Severity**: Critical/High/Medium/Low with justification
- **Environment Details**: OS, versions, configuration
- **Steps to Reproduce**: Minimal, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Reproduction Rate**: Always/Often/Sometimes/Rare
- **Attachments**: Links to logs, screenshots, error outputs
- **Notes**: Any observations, workarounds, or additional context

## Usage Examples

**With issue URL:**
```
/reproduce https://github.com/org/repo/issues/425
```

**With description:**
```
/reproduce The session status updates are failing when pods are deleted
```

**Output example:**
```
✓ Bug reproduction documented
✓ Created: artifacts/bugfix/reports/reproduction.md
✓ Reproduction rate: Always (100%)
✓ Severity: High
✓ Attached: 3 log files

Next steps:
- Run /diagnose to perform root cause analysis
- Review the reproduction report for completeness
```

## Notes

- Take your time to reproduce reliably - a flaky reproduction leads to incomplete diagnosis
- Document even failed reproduction attempts - inability to reproduce is valuable information
- If you cannot reproduce, document the differences between your environment and the report
- Amber will automatically engage appropriate specialists (Stella, frontend-performance-debugger, etc.) if reproduction complexity warrants it
