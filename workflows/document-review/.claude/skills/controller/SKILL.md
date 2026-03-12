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

4. **Install-test** (`/install-test`) — `.claude/skills/install-test/SKILL.md`
   Execute documented installation instructions on a live cluster. Compare
   actual results against documented expectations and track common errors
   with their solutions.

5. **Report** (`/report`) — `.claude/skills/report/SKILL.md`
   Generate a clean, prioritized executive summary from current findings.

6. **Fix** (`/fix`) — `.claude/skills/fix/SKILL.md`
   Generate inline fix suggestions for each finding.

7. **Speedrun** (`/speedrun`)
   Run scan → review + verify + install-test (parallel) → validate → report
   automatically, pausing only for critical decisions.

Phases can be skipped or reordered at the user's discretion.

## Dependency Graph

```text
scan ──┬──> review (sub-agent) ────────┬──> validate ──> report ──> fix
       ├──> verify (sub-agent) ────────┤       ↑  │
       └──> install-test (sub-agent) ──┘       └──┘
                                           (retry on fail,
                                            max 1 retry)
```

- **Scan** must run first — all other phases depend on the inventory.
- **Review**, **verify**, and **install-test** are independent of each other.
  All read the inventory and write to separate findings files. They can run
  in parallel as sub-agents.
- **Validate** checks sub-agent output for coverage, structure, and evidence
  quality. On failure, the failing sub-agent is re-dispatched with specific
  feedback. Maximum 1 retry per sub-agent.
- **Report** and **fix** read from whichever findings files exist.

### Findings Files

| Phase | Output |
|-------|--------|
| Review | `artifacts/document-review/findings-review.md` |
| Verify | `artifacts/document-review/findings-verify.md` |
| Install-test | `artifacts/document-review/findings-install-test.md` |

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

## Running Analysis Sub-Agents in Parallel

When multiple analysis phases should run (e.g., during speedrun, or when the
user requests several), use the Agent tool to launch them as parallel
sub-agents:

1. **Announce** which sub-agents you're launching in parallel
2. **Spawn Agent calls simultaneously** (include whichever are requested):
   - Agent (review): Read `.claude/skills/review/SKILL.md` and execute it.
     Write output to `artifacts/document-review/findings-review.md`.
   - Agent (verify): Read `.claude/skills/verify/SKILL.md` and execute it.
     Write output to `artifacts/document-review/findings-verify.md`.
   - Agent (install-test): Read `.claude/skills/install-test/SKILL.md` and
     execute it. Write output to
     `artifacts/document-review/findings-install-test.md`.
3. **Wait** for all agents to complete
4. **Run validation** (see below)
5. **Summarize** the combined results to the user

When running a single phase (e.g., user invokes only `/review`), execute it
directly — no sub-agent needed. Still run validation afterward.

## Validation Loop

After review, verify, and/or install-test complete, validate their output using
a validation sub-agent. This catches coverage gaps, missing fields, and weak
evidence before the findings flow into report and fix.

### How to Run Validation

1. **Spawn a validation Agent:** Give it these instructions:
   - Read `.claude/skills/validate/SKILL.md` and follow it.
   - Read `artifacts/document-review/inventory.md`.
   - Read whichever findings files exist (`findings-review.md`,
     `findings-verify.md`, `findings-install-test.md`).
   - Return the validation result.
2. **Check the result:**
   - If all checked files **PASS** → proceed to next step.
   - If any file **FAIL** → re-dispatch the failing sub-agent(s) with the
     validator's feedback (see "Retry on Failure" below).

### Retry on Failure

When validation fails for a findings file:

1. **Announce** to the user that validation found issues and a retry is
   happening. Briefly list what failed (e.g., "3 documents were not reviewed,
   2 findings are missing evidence").
2. **Re-dispatch** the failing sub-agent with an augmented prompt:
   - Include the original skill instructions
   - Append the validator's specific feedback
   - Instruct the agent to read its previous output and fix the identified
     issues rather than starting from scratch
3. **Re-run validation** on the new output.
4. If the retry still fails, **accept the output and move on**. Report the
   remaining validation issues to the user but do not loop further. Maximum
   1 retry per sub-agent.

### Example Retry Prompt (for review sub-agent)

```text
Read .claude/skills/review/SKILL.md and execute it.

IMPORTANT: A previous run produced artifacts/document-review/findings-review.md
but validation found these issues:

- Coverage gap: Documents not reviewed: `docs/api.md`, `docs/config.md`
- Missing field: Finding 3 in `README.md` is missing **Evidence**
- Weak evidence: Finding 2 in `CONTRIBUTING.md` has no direct quote

Read your previous output, fix these specific issues, and write the corrected
findings to artifacts/document-review/findings-review.md.
```

### When to Skip Validation

- If the user explicitly asks to skip validation
- If findings files don't exist (the phase wasn't run — that's not a
  validation failure)

## Recommending Next Steps

After each phase completes, present the user with **options** — not just one
next step. Use the typical flow as a baseline, but adapt to what actually
happened.

### Typical Flow

```text
scan → review + verify + install-test (parallel) → validate → report → (optional) fix
```

### What to Recommend

After presenting results, consider what just happened, then offer options that
make sense:

**After scan:**

- Recommend `/review` — the natural next step
- Offer `/verify` if documentation references lots of code (APIs, CLI flags)
- Offer `/install-test` if installation docs were found and a cluster is
  available (`$CLUSTER_URL` and `$CLUSTER_TOKEN` must be set)
- Mention that review, verify, and install-test can run in parallel
- Offer `/speedrun` if the user wants to go fast

**After review (and validation):**

- Recommend `/report` to get a summary of findings
- Offer `/verify` for deeper accuracy checking against code

**After verify (and validation):**

- Recommend `/report` to consolidate all findings

**After install-test (and validation):**

- Recommend `/report` to consolidate all findings
- Note that the troubleshooting guide will feed into `/fix`

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
2. Launch **review**, **verify**, and **install-test** as parallel sub-agents
   (see "Running Analysis Sub-Agents in Parallel" above). Skip install-test
   if no installation docs were found or no cluster is available
   (`$CLUSTER_URL` and `$CLUSTER_TOKEN` must be set).
3. **Run validation** — retry any failing sub-agents (max 1 retry)
4. Once validation passes (or retries are exhausted), execute the **report**
   phase
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
  during speedrun).
- **Always validate.** Run validation after every review, verify, or
  install-test execution, including retries. The only exception is if the user explicitly asks to skip.
- **Recommendations come from this file, not from skills.** Skills report
  findings; this controller decides what to recommend next.
- **Respect the target project.** This workflow reviews external project
  documentation. Do not modify the target project's files unless the user
  explicitly requests it via `/fix`.
