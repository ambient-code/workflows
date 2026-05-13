# /report — Consolidate findings into a deduplicated report

Merges all findings from `/quality-review` and `/code-check` into a single
report grouped by severity, with a dimension × severity summary table.
Writes to `artifacts/report.md`.

**Requires:** At least one of `/quality-review` or `/code-check` must have
been run first.

Read `.claude/skills/controller/SKILL.md` and follow it.

Dispatch the **report** phase. Context:

$ARGUMENTS
