# /review

Dispatch this phase to a subagent using the Task tool.

The subagent should read and follow `.claude/skills/review/SKILL.md` step by step.

Provide the subagent with:

- The fix implementation details and test results
- Paths to all prior artifacts
- The original bug report for context

$ARGUMENTS
