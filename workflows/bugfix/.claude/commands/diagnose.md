# /diagnose - Diagnose Root Cause

## Purpose
Perform systematic root cause analysis to identify the underlying issue causing the bug. This phase focuses on understanding *why* the bug occurs, not just *what* is happening.

## Prerequisites
- Completed reproduction report (from `/reproduce`)
- Access to source code and git history
- Understanding of the affected system architecture

## Process

1. **Review Reproduction**
   - Read the reproduction report thoroughly
   - Understand the exact conditions that trigger the bug
   - Note any patterns or edge cases discovered
   - Identify the entry point for investigation

2. **Code Analysis**
   - Locate the code responsible for the observed behavior
   - Trace the execution flow from entry point to failure
   - Examine relevant functions, methods, and classes
   - Use file:line notation when referencing code (e.g., `handlers.go:245`)
   - Review surrounding context and related components

3. **Historical Analysis**
   - Use `git blame` to identify recent changes to affected code
   - Review relevant pull requests and commit messages
   - Check if similar bugs were reported or fixed previously
   - Look for recent refactoring or architectural changes

4. **Hypothesis Formation**
   - List all potential root causes based on evidence
   - Rank hypotheses by likelihood (high/medium/low confidence)
   - Consider multiple failure modes: logic errors, race conditions, edge cases, missing validation
   - Document reasoning for each hypothesis

5. **Hypothesis Testing**
   - Add targeted logging or debugging to test hypotheses
   - Create minimal test cases to validate or disprove each hypothesis
   - Use binary search if the change was introduced gradually
   - Narrow down to the definitive root cause

6. **Impact Assessment**
   - Identify all code paths affected by this bug
   - Assess severity and blast radius
   - Determine if similar bugs exist elsewhere (pattern analysis)
   - Check if other features are impacted
   - Evaluate if fix requires breaking changes

7. **Solution Approach**
   - Recommend fix strategy based on root cause
   - Consider multiple solution approaches
   - Assess trade-offs (simplicity vs performance vs maintainability)
   - Document why the recommended approach is best

## Output

Creates `artifacts/bugfix/analysis/root-cause.md` containing:

- **Root Cause Summary**: Clear, concise statement of the underlying issue
- **Evidence**: Code references, logs, test results supporting the conclusion
- **Timeline**: When the bug was introduced (commit/PR reference)
- **Affected Components**: List of all impacted code paths with file:line references
- **Impact Assessment**:
  - Severity: Critical/High/Medium/Low
  - User impact: Description of who is affected
  - Blast radius: Scope of the issue
- **Hypotheses Tested**: List of all hypotheses considered and results
- **Recommended Fix Approach**: Detailed strategy for fixing the bug
- **Alternative Approaches**: Other potential solutions with pros/cons
- **Similar Bugs**: References to related issues or patterns to fix
- **References**: Links to relevant PRs, issues, documentation

## Usage Examples

**After reproduction:**
```
/diagnose
```

**With specific focus:**
```
/diagnose Focus on the status update logic in the operator
```

**Output example:**
```
✓ Root cause identified
✓ Created: artifacts/bugfix/analysis/root-cause.md
✓ Root cause: Missing error handling in UpdateStatus call (operator/handlers/sessions.go:334)
✓ Impact: High - affects all session status updates
✓ Recommendation: Add retry logic with exponential backoff
✓ Found 2 similar patterns in other handlers

Next steps:
- Review the root cause analysis
- Run /fix to implement the recommended solution
- Consider fixing similar patterns in other components
```

## Notes

- Take time to fully understand the root cause - rushing leads to incomplete fixes
- Document your reasoning process - future developers will thank you
- If you identify multiple root causes, create separate analysis files
- **ALWAYS** use `file:line` notation when referencing code for easy navigation
- Amber will automatically engage specialists (Stella for complex debugging, sre-reliability-engineer for infrastructure, etc.) based on the bug's nature and complexity
