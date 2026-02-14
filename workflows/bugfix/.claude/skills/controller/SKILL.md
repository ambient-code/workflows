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
5. Present the skill's results to the user
6. **Use the "Recommending Next Steps" section below** to offer options —
   do NOT use any next-step suggestions from the skill itself
7. **Stop and wait** for the user to tell you what to do next

**Important:** Step 4 is critical. Re-reading this file after each phase
prevents you from staying stuck in the previous skill's context.

## Recommending Next Steps

After each phase completes, present the user with **options** — not just one
next step. Use the typical flow as a baseline, but adapt to what actually
happened.

### Typical Flow

```text
assess → reproduce → diagnose → fix → test → review → document → pr
```

### What to Recommend

Consider what just happened, then offer options that make sense:

**Skipping forward** — sometimes phases aren't needed:

- Assess found an obvious root cause → offer `/fix` alongside `/reproduce`
- The bug is a test coverage gap, not a runtime issue → skip `/reproduce`
  and `/diagnose`
- Review says everything is solid → offer `/pr` directly

**Going back** — sometimes earlier work needs revision:

- Test failures → offer `/fix` to rework the implementation
- Review finds the fix is inadequate → offer `/fix`
- Diagnosis was wrong → offer `/diagnose` again with new information

**Ending early** — not every bug needs the full pipeline:

- A trivial fix might go straight from `/fix` → `/test` → `/pr`
- If the user already has their own PR process, they may stop after `/test`

### How to Present Options

Lead with your top recommendation, then list alternatives briefly:

```text
Recommended next step: /test — verify the fix with regression tests.

Other options:
- /review — critically evaluate the fix before testing
- /pr — if you've already tested manually and want to submit
```

The user picks. If they say "yes" or "go ahead," execute your top
recommendation.

## How to Interpret User Responses

After presenting phase results, the user will respond. Match their intent:

| User says | Action |
| --- | --- |
| A phase name or command (e.g., "reproduce", `/fix`) | Execute that phase |
| "yes", "let's do that", "proceed", "go ahead", etc. | Execute the phase you just **recommended** |
| "skip to X" | Execute phase X, skipping intermediate phases |
| A question or request for clarification | Answer it — do not execute anything |
| New information about the bug | Incorporate it, then ask what to do next |

**Critical:** When the user agrees to proceed, execute the phase you
**recommended** — not the phase that just finished. Do NOT re-run the
current phase.

## Starting the Workflow

When the user first provides a bug report, issue URL, or description:

1. Execute the **assess** phase
2. After assessment, present results and wait

If the user invokes a specific command (e.g., `/fix`), execute that phase
directly — don't force them through earlier phases.

## Rules

- **Never auto-advance.** Always wait for the user between phases.
- **Recommendations come from this file, not from skills.** Skills report
  findings; this controller decides what to recommend next.
- **Re-read this file between phases.** This is how you stay in control.
