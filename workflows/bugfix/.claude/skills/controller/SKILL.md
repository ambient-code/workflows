---
name: controller
description: Top-level workflow controller that manages phase transitions.
---

# Bugfix Workflow Controller

You are the workflow controller. Your job is to manage the bugfix workflow by
executing phases and handling transitions between them.

## Phases

1. **Assess** (`/assess`) — `.claude/skills/assess/SKILL.md`
   Read the bug report, summarize your understanding, identify gaps, propose a plan.

2. **Reproduce** (`/reproduce`) — `.claude/skills/reproduce/SKILL.md`
   Confirm the bug exists by reproducing it in a controlled environment.

3. **Diagnose** (`/diagnose`) — `.claude/skills/diagnose/SKILL.md`
   Trace the root cause through code analysis, git history, and hypothesis testing.

4. **Fix** (`/fix`) — `.claude/skills/fix/SKILL.md`
   Implement the minimal code change that resolves the root cause.

5. **Test** (`/test`) — `.claude/skills/test/SKILL.md`
   Write regression tests, run the full suite, and verify the fix holds.

6. **Review** (`/review`) — `.claude/skills/review/SKILL.md`
   Critically evaluate the fix and tests — look for gaps, regressions, and missed edge cases.

7. **Document** (`/document`) — `.claude/skills/document/SKILL.md`
   Create release notes, changelog entries, and team communications.

8. **PR** (`/pr`) — `.claude/skills/pr/SKILL.md`
   Push the branch to a fork and create a draft pull request.

Phases can be skipped or reordered at the user's discretion.

## How to Execute a Phase

1. **Announce** the phase to the user before doing anything else, e.g., "Starting the /fix phase."
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

- A trivial fix might go straight from `/fix` → `/test` → `/review` → `/pr`
- If the user already has their own PR process, they may stop after `/review`

### How to Present Options

Lead with your top recommendation, then list alternatives briefly:

```text
Recommended next step: /test — verify the fix with regression tests.

Other options:
- /review — critically evaluate the fix before testing
- /pr — if you've already tested manually and want to submit
```

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
