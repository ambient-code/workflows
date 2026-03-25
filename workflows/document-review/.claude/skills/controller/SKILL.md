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
   Consolidate all findings into a single deduplicated report grouped by
   severity.

5. **Fix** (`/fix`) — `.claude/skills/fix/SKILL.md`
   Generate inline fix suggestions for each finding.

6. **Jira** (`/jira`) — `.claude/skills/jira/SKILL.md`
   Create a Jira epic from the report with child bugs and tasks for each
   finding. Uses the Jira REST API via `curl`.

7. **Speedrun** (`/speedrun`)
   Run scan → review + verify (parallel) → report automatically, pausing
   only for critical decisions.

Phases can be skipped or reordered at the user's discretion.

## Dependency Graph

```text
scan ──┬──> review (sub-agent) ──┬──> report ──> fix
       └──> verify (sub-agent) ──┘            └──> jira
```

- **Scan** must run first — all other phases depend on the inventory.
- **Review** and **verify** are independent of each other. Both read the
  inventory and write to separate findings files. They can run in parallel
  as sub-agents.
- **Report** and **fix** read from whichever findings files exist.
- **Jira** reads from `artifacts/report.md` and requires a completed report.

### Findings Files

| Phase | Output |
|-------|--------|
| Review | `artifacts/findings-review.md` |
| Verify | `artifacts/findings-verify.md` |

Report and fix read from all findings files (whichever exist).

## How to Execute a Phase

1. **Announce** the phase to the user before doing anything else, e.g.,
   "Starting the /scan phase." This is very important so the user knows the
   workflow is progressing and learns about the commands.
2. **Read** the skill file from the list above
3. **Execute** the skill's steps directly — the user should see your progress
4. When the skill is done, use "Recommending Next Steps" below to offer options.
5. Present the skill's results and your recommendations to the user
6. **Stop and wait** for the user to tell you what to do next

## Handling Multiple Commands

When the user provides multiple commands in a single prompt (e.g.,
`/scan /review /report` or "run scan, review, and report"), execute **all**
listed commands in order. This is equivalent to the user invoking each command
one after another — do not stop between them to ask what to do next.

### How to process multiple commands

1. **Parse** the full prompt and identify all commands mentioned
2. **Announce** the plan: "Running /scan → /review → /report."
3. **Execute each command in sequence**, following the dependency graph:
   - If a later command depends on an earlier one (e.g., `/review` needs
     `/scan`), execute them in order
   - If commands are independent (e.g., `/review` and `/verify`), run them in
     parallel as sub-agents — same as during speedrun
4. **Report combined results** at the end, after all commands have completed
5. **Then stop and wait** — recommend next steps as usual

### Examples

- `/scan /review` → run scan, then review, then present results
- `/scan /review /verify` → run scan, then review + verify in parallel, then
  present results
- `/scan /review /report` → run scan, then review, then report, then present
  results
- `/review /report /fix` → run review (scan first if no inventory), then
  report, then fix, then present results

## Running Analysis Sub-Agents in Parallel

When multiple analysis phases should run (e.g., during speedrun, or when the
user requests several), use the Agent tool to launch them as parallel
sub-agents:

1. **Announce** which sub-agents you're launching in parallel
2. **Spawn Agent calls simultaneously:**
   - Agent (review): Read `.claude/skills/review/SKILL.md` and execute it.
     Write output to `artifacts/findings-review.md`.
   - Agent (verify): Read `.claude/skills/verify/SKILL.md` and execute it.
     Write output to `artifacts/findings-verify.md`.
3. **Wait** for all agents to complete
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
- Mention that review and verify can run in parallel
- Offer `/speedrun` if the user wants to go fast

**After review:**

- Recommend `/report` to consolidate all findings
- Offer `/verify` for deeper accuracy checking against code

**After verify:**

- Recommend `/report` to consolidate all findings

**After report:**

- Offer `/fix` if actionable issues were found
- Offer `/jira` to create Jira issues for tracking remediation
- The workflow may be complete if the report is the desired output

**After fix:**

- The workflow is typically complete
- Offer `/jira` to create Jira issues for tracking remediation
- Offer to re-run `/report` to reflect any updates

**After jira:**

- The workflow is typically complete
- Offer `/fix` if fix suggestions haven't been generated yet

**Going back** — sometimes earlier work needs revision:

- New documents discovered → offer `/scan` again
- Need deeper accuracy checking → offer `/verify`

### How to Present Options

Lead with your top recommendation, then list alternatives briefly:

```text
Recommended next step: /review — deep quality analysis of the 42 documents found.

Other options:
- /verify — cross-reference docs against source code (can run in parallel with review)
- /speedrun — run scan → review + verify → report automatically
```

## Executing a Speedrun

When the user invokes `/speedrun`:

1. Execute the **scan** phase — announce it, read the skill, run it
2. Launch **review** and **verify** as parallel sub-agents
3. Once both complete, execute the **report** phase
5. Present the final report to the user
6. Offer `/fix` as a follow-up option

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
  during speedrun or when the user provides multiple commands in a single
  prompt).
- **Recommendations come from this file, not from skills.** Skills report
  findings; this controller decides what to recommend next.
- **Respect the target project.** This workflow reviews external project
  documentation. Do not modify the target project's files unless the user
  explicitly requests it via `/fix`.
