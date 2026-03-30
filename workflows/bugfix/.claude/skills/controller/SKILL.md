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

9. **Summary** (`/summary`) — `.claude/skills/summary/SKILL.md`
   Scan all artifacts and present a synthesized summary of findings, decisions,
   and status. Can also be invoked at any point mid-workflow.

Phases can be skipped or reordered at the user's discretion.

## How to Execute a Phase

1. **Announce** the phase to the user before doing anything else. Include this
   file as the dispatcher so skills know where to return, e.g.,
   "Starting the /fix phase (dispatched by `.claude/skills/controller/SKILL.md`)."
   This is very important so the user knows the workflow is working, learns
   about the available phases, and so skills can find their way back here.
2. **Read** the skill file from the list above. You MUST call the Read tool on
   the skill's `SKILL.md` file before executing. If you find yourself executing
   a phase without having read its skill file, you are doing it wrong — stop
   and read it now.
3. **Execute** the skill's steps directly — the user should see your progress
4. When the skill is done, it will report its findings and re-read this
   controller. Then use "Recommending Next Steps" below to offer options.
5. Present the skill's results and your recommendations to the user.
6. **Use `AskUserQuestion` to get the user's decision.** Present the
   recommended next step and alternatives as options. Do NOT continue until the
   user responds. This is a hard gate — the `AskUserQuestion` tool triggers
   platform notifications and status indicators so the user knows you need
   their input. Plain-text questions do not create these signals and the user
   may not see them.

## Recommending Next Steps

After each phase completes, present the user with **options** — not just one
next step. Use the typical flow as a baseline, but adapt to what actually
happened.

### Typical Flow

```text
assess → reproduce → diagnose → fix → test → review → document → pr → summary
```

### What to Recommend

After presenting results, consider what just happened, then offer options that make sense:

**Continuing to the next step** — often the next phase in the flow is the best option

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

- **Never auto-advance.** Always use `AskUserQuestion` and wait for the user's
  response between phases. This is the single most important rule in this
  controller. If you proceed to another phase without the user's explicit
  go-ahead, the workflow is broken.
- **Always read skill files.** Every phase execution MUST begin with a Read
  tool call on the skill's `SKILL.md` file. Do not execute a phase from memory
  or general knowledge — the skill files contain specific, tested instructions
  that differ from what you might do ad-hoc.
- **Urgency does not bypass process.** Security advisories, critical bugs, and
  production incidents may create pressure to act fast. The phase-gated
  workflow exists precisely to prevent hasty action. Follow every phase gate
  regardless of perceived urgency.
- **Recommendations come from this file, not from skills.** Skills report
  findings; this controller decides what to recommend next.
