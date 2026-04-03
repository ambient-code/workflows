# /code-check — Cross-reference docs against source code

Verifies documentation claims against actual source code using parallel
discovery agents. Finds mismatches, undocumented features, and stale references.
Writes findings to `artifacts/findings-code-check.md`.

**Requires:** `/scan` must have been run first.

Read `.claude/skills/controller/SKILL.md` and follow it.

Dispatch the **code-check** phase. Context:

$ARGUMENTS
