---
name: controller
description: Top-level workflow controller that manages phase transitions.
---

# Bugfix Workflow Controller

You are the workflow controller. Your job is to manage the bugfix workflow by
executing phases and handling transitions between them.

## Phases

| # | Phase | Command | Skill Path |
| --- | --- | --- | --- |
| 1 | Assess | `/assess` | `.claude/skills/assess/SKILL.md` |
| 2 | Reproduce | `/reproduce` | `.claude/skills/reproduce/SKILL.md` |
| 3 | Diagnose | `/diagnose` | `.claude/skills/diagnose/SKILL.md` |
| 4 | Fix | `/fix` | `.claude/skills/fix/SKILL.md` |
| 5 | Test | `/test` | `.claude/skills/test/SKILL.md` |
| 6 | Review | `/review` | `.claude/skills/review/SKILL.md` |
| 7 | Document | `/document` | `.claude/skills/document/SKILL.md` |
| 8 | PR | `/pr` | `.claude/skills/pr/SKILL.md` |

Phases can be skipped or reordered at the user's discretion.

## How to Execute a Phase

1. **Announce** which phase you are about to run
2. **Read** the skill file from the table above
3. **Execute** the skill's steps directly — the user should see your progress
4. When the skill is done, it will tell you to report your findings.
   **Before responding to the user, re-read this controller file**
   (`.claude/skills/controller/SKILL.md`) so the transition rules below
   are fresh in your context
5. Present results and the skill's recommended next step to the user
6. **Stop and wait** for the user to tell you what to do next

**Important:** Step 4 is critical. Re-reading this file after each phase
prevents you from staying stuck in the previous skill's context.

## How to Interpret User Responses

After presenting phase results, the user will respond. Match their intent:

| User says | Action |
| --- | --- |
| A phase name or command (e.g., "reproduce", `/fix`) | Execute that phase |
| "yes", "let's do that", "proceed", "go ahead", etc. | Execute whatever the **last phase recommended** |
| "skip to X" | Execute phase X, skipping intermediate phases |
| A question or request for clarification | Answer it — do not execute anything |
| New information about the bug | Incorporate it, then ask what to do next |

**Critical:** When the user agrees to proceed, execute the **recommended**
phase — the one the skill just suggested. Do NOT re-run the phase that just
finished. Do NOT default to the next sequential phase if the skill
recommended something different.

## Starting the Workflow

When the user first provides a bug report, issue URL, or description:

1. Execute the **assess** phase
2. After assessment, present results and wait

If the user invokes a specific command (e.g., `/fix`), execute that phase
directly — don't force them through earlier phases.

## Rules

- **Never auto-advance.** Always wait for the user between phases.
- **Track the last recommendation.** You need it to interpret "yes."
- **Re-read this file between phases.** This is how you stay in control.
