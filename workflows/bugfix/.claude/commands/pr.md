# /pr

Dispatch this phase to a subagent using the Task tool.

The subagent should read and follow `.claude/skills/pr/SKILL.md` step by step.

**Important:** The PR skill has a specific multi-step process for handling
authentication, forking, and PR creation. The subagent must follow the
numbered steps exactly as written.

Provide the subagent with:

- The project repository path
- What was fixed, tested, and documented
- Paths to all prior artifacts (especially `artifacts/bugfix/docs/`)
- The issue number and repository details

$ARGUMENTS
