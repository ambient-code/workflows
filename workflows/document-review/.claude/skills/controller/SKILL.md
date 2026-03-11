---
name: controller
description: Top-level workflow controller that manages phase transitions.
---

# Document Review Workflow Controller

You are the workflow controller. Your job is to manage the document review
workflow by executing phases and handling transitions between them.

## Phases

1. **Scan** (`/scan`) — `.claude/skills/scan/SKILL.md`
   Discover and catalog all documentation files in the target project. Produce
   an inventory of what exists, its format, and its apparent audience.

2. **Review** (`/review`) — `.claude/skills/review/SKILL.md`
   Deep-read each document, evaluating 7 quality dimensions. Classify findings
   by severity. Identify target audience per document.

3. **Verify** (`/verify`) — `.claude/skills/verify/SKILL.md`
   Cross-reference documentation against actual source code. Check that
   documented APIs, CLI flags, config options, and behavior descriptions match
   the implementation.

4. **Report** (`/report`) — `.claude/skills/report/SKILL.md`
   Generate a clean, prioritized executive summary from current findings.

5. **Fix** (`/fix`) — `.claude/skills/fix/SKILL.md`
   Generate inline fix suggestions for each finding.

6. **Speedrun** (`/speedrun`)
   Run scan → review + verify (parallel) → report automatically, pausing only
   for critical decisions.

Phases can be skipped or reordered at the user's discretion.

## Dependency Graph

```text
scan ──┬──> review (sub-agent) ──┬──> report ──> fix
       └──> verify (sub-agent) ──┘
```

- **Scan** must run first — all other phases depend on the inventory.
- **Review** and **verify** are independent of each other. Both read the
  inventory and write to separate findings files. They can run in parallel as
  sub-agents.
- **Report** and **fix** read from whichever findings files exist.

### Findings Files

| Phase | Output |
|-------|--------|
| Review | `artifacts/document-review/findings-review.md` |
| Verify | `artifacts/document-review/findings-verify.md` |

Report and fix read from both files (whichever exist).

## How to Execute a Phase

1. **Announce** the phase to the user before doing anything else, e.g.,
   "Starting the /scan phase." This is very important so the user knows the
   workflow is progressing and learns about the commands.
2. **Read** the skill file from the list above
3. **Execute** the skill's steps directly — the user should see your progress
4. When the skill is done, use "Recommending Next Steps" below to offer options.
5. Present the skill's results and your recommendations to the user
6. **Stop and wait** for the user to tell you what to do next

## Running Review and Verify in Parallel

When both review and verify should run (e.g., during speedrun, or when the user
requests both), use the Agent tool to launch them as parallel sub-agents:

1. **Announce** that you're launching review and verify in parallel
2. **Spawn two Agent calls simultaneously:**
   - Agent 1 (review): Read `.claude/skills/review/SKILL.md` and execute it.
     Write output to `artifacts/document-review/findings-review.md`.
   - Agent 2 (verify): Read `.claude/skills/verify/SKILL.md` and execute it.
     Write output to `artifacts/document-review/findings-verify.md`.
3. **Wait** for both agents to complete
4. **Summarize** the combined results to the user

When running a single phase (e.g., user invokes only `/review`), execute it
directly — no sub-agent needed.

## Recommending Next Steps

After each phase completes, present the user with **options** — not just one
next step. Use the typical flow as a baseline, but adapt to what actually
happened.

### Typical Flow

```text
scan → review + verify (parallel) → report → (optional) fix
```

### What to Recommend

After presenting results, consider what just happened, then offer options that
make sense:

**After scan:**

- Recommend `/review` — the natural next step
- Offer `/verify` if documentation references lots of code (APIs, CLI flags)
- Mention that review and verify can run in parallel if both are needed
- Offer `/speedrun` if the user wants to go fast

**After review:**

- Recommend `/report` to get a summary of findings
- Offer `/verify` for deeper accuracy checking against code

**After verify:**

- Recommend `/report` to consolidate all findings

**After report:**

- Offer `/fix` if actionable issues were found
- The workflow may be complete if the report is the desired output

**After fix:**

- The workflow is typically complete
- Offer to re-run `/report` to reflect any updates

**Going back** — sometimes earlier work needs revision:

- New documents discovered → offer `/scan` again
- Need deeper accuracy checking → offer `/verify`

### How to Present Options

Lead with your top recommendation, then list alternatives briefly:

```text
Recommended next step: /review — deep quality analysis of the 42 documents found.

Other options:
- /verify — cross-reference docs against source code (can run in parallel with review)
- /speedrun — run the full scan → review + verify → report pipeline automatically
```

## Executing a Speedrun

When the user invokes `/speedrun`:

1. Execute the **scan** phase — announce it, read the skill, run it
2. Launch **review** and **verify** as parallel sub-agents (see "Running Review
   and Verify in Parallel" above)
3. Once both complete, execute the **report** phase
4. Present the final report to the user
5. Offer `/fix` as a follow-up option

During speedrun, only pause if:

- The project repository cannot be found or accessed
- No documentation files are discovered
- A critical error prevents the review from continuing

## Starting the Workflow

When the user first provides a project path, repository URL, or description:

1. Execute the **scan** phase
2. After scanning, present results and wait

If the user invokes a specific command (e.g., `/review`), execute that phase
directly — don't force them through earlier phases. However, if a phase is
invoked without an existing inventory, run `/scan` first and inform the user.

## Rules

- **Never auto-advance.** Always wait for the user between phases (except
  during speedrun).
- **Recommendations come from this file, not from skills.** Skills report
  findings; this controller decides what to recommend next.
- **Respect the target project.** This workflow reviews external project
  documentation. Do not modify the target project's files unless the user
  explicitly requests it via `/fix`.
