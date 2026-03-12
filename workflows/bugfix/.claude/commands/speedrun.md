---
description: Speed-run the remaining bugfix phases without stopping between them.
displayName: speedrun
icon: ⚡
---

# /speedrun — Run the Remaining Workflow

You are in **speedrun mode**. Run the next incomplete phase, then return here
for the next one. Do not use the controller (`.claude/skills/controller/SKILL.md`).

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding. It may contain a bug report, issue
URL, context about where they are in the workflow, or instructions about which
phases to include or skip.

## How Speedrun Works

Each time you read this file, you will:

1. Determine which phase to run next (see "Determine Next Phase" below)
2. If all phases are done, print the completion report and stop
3. Otherwise, execute that one phase (see "Execute a Phase" below)
4. The phase skill will tell you to return to the file that dispatched it —
   that's this file (`.claude/commands/speedrun.md`). Re-read it and repeat.

This loop continues until all phases are complete or an escalation stops you.

## Determine Next Phase

Check which phases are already done by looking for artifacts and conversation
context, then pick the first phase that is NOT done.

### Phase Order and Completion Signals

| Phase | Skill | "Done" signal |
| ------- | ------- | --------------- |
| assess | `.claude/skills/assess/SKILL.md` | `artifacts/bugfix/reports/assessment.md` exists |
| reproduce | `.claude/skills/reproduce/SKILL.md` | `artifacts/bugfix/reports/reproduction.md` exists |
| diagnose | `.claude/skills/diagnose/SKILL.md` | `artifacts/bugfix/analysis/root-cause.md` exists |
| fix | `.claude/skills/fix/SKILL.md` | `artifacts/bugfix/fixes/implementation-notes.md` exists |
| test | `.claude/skills/test/SKILL.md` | `artifacts/bugfix/tests/verification.md` exists |
| review | `.claude/skills/review/SKILL.md` | `artifacts/bugfix/review/verdict.md` exists |
| document | `.claude/skills/document/SKILL.md` | `artifacts/bugfix/docs/pr-description.md` exists |
| pr | `.claude/skills/pr/SKILL.md` | A PR URL has been shared in conversation |

### Rules

- Check artifacts in order. The first phase whose signal is NOT satisfied is next.
- If no artifacts exist, start at **assess**.
- If the user specifies a starting point in `$ARGUMENTS`, respect that.
- If conversation context clearly establishes a phase was completed (even
  without an artifact), skip it.

## Execute a Phase

1. **Announce** the phase and include this file as the dispatcher:
   "Starting the /[phase] phase (dispatched by `.claude/commands/speedrun.md` — speedrun mode)."
2. **Read** the phase skill from the table above
3. **Execute** the skill's steps
4. The skill will tell you to announce which file you are returning to and
   re-read it. Return to **this file** (`.claude/commands/speedrun.md`).

## Speedrun Rules

- **Do not stop and wait between phases.** After each phase, return here and
  continue to the next one.
- **Do not read the controller.** This command replaces the controller for this
  run. If you are tempted to read `.claude/skills/controller/SKILL.md`, read
  `.claude/commands/speedrun.md` instead.
- **DO still follow CLAUDE.md escalation rules.** If a phase hits an
  escalation condition (confidence below 80%, unclear root cause after
  investigation, multiple valid solutions with unclear trade-offs, security or
  compliance concern, architectural decision needed), stop and ask the user.
  After the user responds, re-read this file to resume.

## Phase-Specific Notes

### assess

- If no bug report or issue URL exists in `$ARGUMENTS` or conversation, ask
  the user once, then proceed.
- Present the assessment inline but do not wait for confirmation.

### reproduce

- If reproduction fails, note the failure and continue to diagnose anyway
  (diagnosis may reveal why reproduction is difficult).

### diagnose

- If multiple root causes are plausible and you cannot determine which is
  correct with high confidence, this is an escalation point — stop and ask.

### fix

- Create a feature branch if one doesn't exist yet.
- If the diagnosis identified multiple fix approaches with unclear trade-offs,
  this is an escalation point — stop and ask.

### test

- Run the full test suite. If tests fail due to your fix, attempt to resolve
  them before continuing.
- If failures persist after a reasonable attempt, note them and continue —
  review will catch outstanding issues.

### review

- Always run this phase between test and document.
- **Verdict: "fix and tests are solid"** — continue to document.
- **Verdict: "fix is adequate, tests incomplete"** — attempt to add the
  missing tests, then continue to document.
- **Verdict: "fix is inadequate"** — perform **one** revision cycle: go back
  to fix → test → review. If the second review still says "inadequate," stop
  and report the issues to the user instead of looping further.

### document

- Generate all documentation artifacts per the skill.

### pr

- Follow the PR skill's full process including its fallback ladder.
- If PR creation fails after exhausting fallbacks, report and stop.

## Completion Report

When all phases are done (or if you stop early due to escalation), present:

```markdown
## Speedrun Complete

### Phases Run
- [each phase that ran and its key outcome]

### Artifacts Created
- [all artifacts with paths]

### Result
- [PR URL, or reason for stopping early]

### Notes
- [any escalations, skipped phases, or items needing follow-up]
```

## Usage Examples

**From the beginning (no prior work):**

```text
/speedrun Fix bug https://github.com/org/repo/issues/425 - session status updates failing
```

**Mid-workflow (some phases already done):**

```text
/speedrun
```

The command detects existing artifacts and picks up from the next incomplete phase.

**With an explicit starting point:**

```text
/speedrun Start from /fix — I already know the root cause
```
