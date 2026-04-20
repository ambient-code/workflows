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

2. **Quality Review** (`/quality-review`) — `.claude/skills/quality-review/SKILL.md`
   Deep-read each document, evaluating 7 quality dimensions. Classify findings
   by severity. Identify target audience per document.

3. **Code Check** (`/code-check`) — `.claude/skills/code-check/SKILL.md`
   Cross-reference documentation against actual source code. Check that
   documented APIs, CLI flags, config options, and behavior descriptions match
   the implementation.

4. **Report** (`/report`) — `.claude/skills/report/SKILL.md`
   Consolidate all findings into a single deduplicated report grouped by
   severity.

5. **Jira** (`/jira`) — `.claude/skills/jira/SKILL.md`
   Create a Jira epic from the report with child bugs and tasks for each
   finding. Uses the Jira REST API via `curl`.

6. **Full Review** (`/full-review`)
   Run scan → quality-review + code-check (parallel) → report automatically, pausing
   only for critical decisions.

Phases may be requested in any order, but dependency requirements still apply
(e.g., run `/scan` before phases that require `artifacts/inventory.md`).

## Dependency Graph

```text
scan ──┬──> quality-review (sub-agent) ──┬──> report
       └──> code-check (sub-agent)    ──┘       └──> jira
```

- **Scan** must run first — all other phases depend on the inventory.
- **Quality review** and **code check** are independent of each other. Both
  read the inventory and write to separate findings files. They can run in
  parallel as sub-agents.
- **Jira** reads from `artifacts/report.md` and requires a completed report.

### Findings Files

| Phase | Output |
|-------|--------|
| Quality Review | `artifacts/findings-quality-review.md` |
| Code Check | `artifacts/findings-code-check.md` |

Report reads from all findings files (whichever exist).

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
`/scan /quality-review /report` or "run scan, quality-review, and report"), execute **all**
listed commands in order. This is equivalent to the user invoking each command
one after another — do not stop between them to ask what to do next.

### How to process multiple commands

1. **Parse** the full prompt and identify all commands mentioned
2. **Announce** the plan: "Running /scan → /quality-review → /report."
3. **Execute each command in sequence**, following the dependency graph:
   - If a later command depends on an earlier one (e.g., `/quality-review`
     needs `/scan`), execute them in order
   - If commands are independent (e.g., `/quality-review` and `/code-check`),
     run them in
     parallel as sub-agents — same as during full-review
4. **Report combined results** at the end, after all commands have completed
5. **Then stop and wait** — recommend next steps as usual

### Examples

- `/scan /quality-review` → run scan, then quality-review, then present results
- `/scan /quality-review /code-check` → run scan, then quality-review +
  code-check in parallel, then present results
- `/scan /quality-review /report` → run scan, then quality-review, then report,
  then present results
- `/quality-review /report` → run quality-review (scan first if no inventory),
  then report, then present results

## Running Analysis Sub-Agents in Parallel

When multiple analysis phases should run (e.g., during full-review, or when the
user requests several), use the Agent tool to launch them as parallel
sub-agents:

1. **Announce** which sub-agents you're launching in parallel
2. **Spawn Agent calls simultaneously:**
   - Agent (quality-review): Read `.claude/skills/quality-review/SKILL.md` and
     execute it. Write output to `artifacts/findings-quality-review.md`.
   - Agent (code-check): Read `.claude/skills/code-check/SKILL.md` and execute
     it. Write output to `artifacts/findings-code-check.md`.
3. **Wait** for all agents to complete
4. **Summarize** the combined results to the user

When running a single phase (e.g., user invokes only `/quality-review`), execute it
directly — no sub-agent needed.

## Recommending Next Steps

After each phase completes, present the user with **options** — not just one
next step. Use the typical flow as a baseline, but adapt to what actually
happened.

### Typical Flow

```text
scan → quality-review + code-check (parallel) → report
```

### What to Recommend

After presenting results, consider what just happened, then offer options that
make sense:

**After scan:**

- Recommend `/quality-review` — the natural next step
- Offer `/code-check` if documentation references lots of code (APIs, CLI flags)
- Mention that quality-review and code-check can run in parallel
- Offer `/full-review` if the user wants to run the entire pipeline at once

**After quality-review:**

- Recommend `/report` to consolidate all findings
- Offer `/code-check` for deeper accuracy checking against code

**After code-check:**

- Recommend `/report` to consolidate all findings

**After report:**

- Offer `/jira` to create Jira issues for tracking remediation
- The workflow may be complete if the report is the desired output

**After jira:**

- The workflow is typically complete

**Going back** — sometimes earlier work needs revision:

- New documents discovered → offer `/scan` again
- Need deeper accuracy checking → offer `/code-check`

### How to Present Options

Lead with your top recommendation, then list alternatives briefly:

```text
Recommended next step: /quality-review — deep quality analysis of the 42 documents found.

Other options:
- /code-check — cross-reference docs against source code (can run in parallel with quality-review)
- /full-review — run scan → quality-review + code-check → report automatically
```

## Executing a Full Review

When the user invokes `/full-review`:

1. Execute the **scan** phase — announce it, read the skill, run it
2. Launch **quality-review** and **code-check** as parallel sub-agents
3. Once both complete, execute the **report** phase
4. Present the final report to the user
5. Offer `/jira` as a follow-up option

During full-review, only pause if:

- The project repository cannot be found or accessed
- No documentation files are discovered
- A critical error prevents the review from continuing

## Starting the Workflow

When the user first provides a project path, repository URL, or description:

1. Execute the **scan** phase
2. After scanning, present results and wait

If the user invokes a specific command (e.g., `/quality-review`), execute that phase
directly — don't force them through earlier phases. However, if a phase is
invoked without an existing inventory, run `/scan` first and inform the user.

## Rules

- **Never auto-advance.** Always wait for the user between phases (except
  during full-review or when the user provides multiple commands in a single
  prompt).
- **Recommendations come from this file, not from skills.** Skills report
  findings; this controller decides what to recommend next.
- **Respect the target project.** This workflow reviews external project
  documentation. Do not modify the target project's files.
