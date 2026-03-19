# Bug Fix Workflow Tutorial

This tutorial walks you through using the Bug Fix workflow on the Ambient
Code Platform to diagnose and fix software bugs. By the end you will know how
to start a session, move through each phase of the workflow, and submit a pull
request with the fix.

## Getting Started

### Log in and create a session

Open [red.ht/ambient](https://red.ht/ambient) and start a new session. Select
the **Bug Fix** workflow and the model you want to use.

### Choosing a model

At the time of writing, **Claude Opus** is the model we find works best for
fixing bugs. If your bug is straightforward (a clear error message pointing to
an obvious cause), a less powerful model may be fine and can be quicker and
cheaper.

Keep in mind, though, that if the bug turns out to be more complex than you
expect, a less powerful model can end up being *slower* and *more expensive*. A
bug that a stronger model solves in one pass may take several rounds of
back-and-forth with a weaker model, consuming more time and tokens overall. When
in doubt, start with a capable model.

### Adding repository context

You can add the GitHub repository you want to work on by clicking the
**Add Context** tab in the Explorer panel before you begin. However, this is
not strictly necessary. If you give the workflow a link to the repository, or
to an issue in that repository, it will clone the repo into your session
automatically.

## Starting the Workflow

There are several ways to kick things off once your session is running.

### Option 1: Paste a bug issue link

Simply paste a link to a GitHub issue and the workflow will clone the repository
and begin walking you through the bug fix process interactively. For example:

```text
https://github.com/llamastack/llama-stack/issues/5119
```

The workflow will assess the issue, summarize its understanding, and ask for
your input before moving on to the next step.

### Option 2: Speedrun a bug issue

If you want the workflow to run through every phase without stopping for
input between steps, use the `/speedrun` command followed by the issue link:

```text
/speedrun https://github.com/llamastack/llama-stack/issues/5119
```

See [Speedrun mode](#speedrun-mode) below for details on what this does and
when to use it.

### Option 3: Describe the bug yourself

You do not need a GitHub issue at all. You can describe the bug in your own
words and provide a link to the repository:

```text
The Milvus vector store integration rejects collection names that contain
hyphens. Repo: https://github.com/llamastack/llama-stack
```

The workflow will clone the repo and proceed from there. This works with or
without `/speedrun`. Prefix your description with `/speedrun` to run through
all phases automatically, or leave it off to step through interactively.

## Workflow Phases

The Bug Fix workflow is organized into a series of phases. In the default
interactive mode the workflow completes one phase at a time, presents you with
results and recommendations, and then waits for you to decide what to do next.
You can follow the suggested order, skip ahead, or go back to revisit an
earlier phase at any point.

Most phases produce a **report**, a Markdown file you can view in the
**Files** section of the Explorer panel. These reports are internal to
your session (they are not published to GitHub or anywhere else) and serve
two purposes:

1. **Visibility for you.** The reports give you a deeper view of what the
   workflow found and decided at each step, so you can provide more informed
   input and steer the process effectively.

2. **Memory for the workflow.** The platform can only keep a finite amount of
   context in memory at a time. By the time the workflow reaches the Test or
   Review phase, for example, the details of the original assessment may no
   longer be in its working context. The written reports let later phases refer
   back to earlier analysis without losing important details.

### Assess

**Command:** `/assess`

The first phase reads the bug report (or your description) and presents a
summary of its understanding: what the bug is, where it likely occurs, what
information is available, what is missing, and a proposed plan for
reproducing it. No code is changed or executed in this phase; it is purely
analysis and planning.

This is your chance to correct any misunderstandings or fill in missing
details before work begins.

**Report:** `artifacts/bugfix/reports/assessment.md`

### Reproduce

**Command:** `/reproduce`

This phase attempts to reproduce the bug in a controlled environment. It
follows the plan from the Assess phase, documents the steps taken, and records
what happened. Even a failed reproduction attempt is documented, since
understanding *why* a bug is hard to reproduce is useful information for
diagnosis.

**Report:** `artifacts/bugfix/reports/reproduction.md`

### Diagnose

**Command:** `/diagnose`

Root cause analysis. The workflow traces through the code, examines git
history, forms hypotheses about what is going wrong, and tests them. The goal
is to understand *why* the bug happens, not just *what* happens. The diagnosis
also assesses how much of the codebase is affected and recommends an approach
for the fix.

**Report:** `artifacts/bugfix/analysis/root-cause.md`

### Fix

**Command:** `/fix`

Implements the bug fix. The workflow creates a feature branch, makes the
minimal code changes needed to resolve the root cause, runs linters and
formatters, and documents the implementation choices it made.

**Report:** `artifacts/bugfix/fixes/implementation-notes.md`

### Test

**Command:** `/test`

Verifies the fix. The workflow creates regression tests that fail without the
fix and pass with it, runs the project's full test suite to check for
unintended side effects, and performs manual verification of the original
reproduction steps.

**Report:** `artifacts/bugfix/tests/verification.md`

### Review

**Command:** `/review`

An optional but recommended self-review phase. The workflow steps back and
critically evaluates the fix and tests: Does the fix address the root cause or
just suppress a symptom? Do the tests actually prove the bug is resolved, or
could they be hiding problems? The review produces a verdict:

- **Fix and tests are solid.** Ready to proceed to documentation and PR.
- **Fix is adequate but tests are incomplete.** Additional testing is
  recommended before proceeding.
- **Fix is inadequate.** The fix needs more work. The workflow will suggest
  going back to the Fix phase with specific guidance.

### Document

**Command:** `/document`

Creates the supporting documentation for the fix: release notes, a changelog
entry, an issue update, and a draft pull request description.

**Reports:** `artifacts/bugfix/docs/` (multiple files including
`release-notes.md`, `changelog-entry.md`, and `pr-description.md`)

### PR

**Command:** `/pr`

The final phase. The workflow pushes the feature branch to a fork and creates a
draft pull request against the upstream repository. If automated PR creation
fails for any reason (e.g., missing permissions), it provides instructions for
creating the PR manually.

## Speedrun Mode

**Command:** `/speedrun`

Speedrun mode runs through all remaining phases in sequence without pausing for
your input between steps. It is useful when you have a well-defined bug and
trust the workflow to handle the full lifecycle autonomously.

Even in speedrun mode, the workflow will stop and ask you for guidance if it
hits a situation that needs human judgment, such as when the root cause is
unclear, if there are multiple valid fix approaches with different trade-offs,
or if a security concern arises.

### Why speedrun is not the default

The default interactive mode pauses after each phase so you can review the
results and steer the process. For many bugs, especially complex ones or bugs
where the report is incomplete or ambiguous, this deliberate pacing is
valuable. Reviewing the assessment before reproduction begins, or checking the
diagnosis before a fix is attempted, lets you catch mistakes early and provide
context that the workflow might not have.

Speedrun is best suited for well-understood bugs where you are confident the
report contains enough information for the workflow to proceed on its own.

### Speedrun examples

Run from the beginning with a bug issue link:

```text
/speedrun https://github.com/llamastack/llama-stack/issues/5119
```

Continue from wherever you are in the flow (the workflow detects which phases are already complete):

```text
/speedrun
```

Jump ahead to a specific phase:

```text
/speedrun Jump ahead to /fix
```

## Viewing Reports and Artifacts

As the workflow progresses, reports and other artifacts are written to the
`artifacts/bugfix/` directory. You can view these files at any time in the
**Files** section of the Explorer panel. The reports are Markdown files that
provide a detailed record of each phase's analysis, decisions, and outcomes.

## A Note on Automation

This tutorial has covered using the Bug Fix workflow through the interactive UI.
It is also possible to connect to the Ambient Code Platform remotely (for
example, via a GitHub Action or other automation) to trigger bug fix workflows
programmatically. The details of that setup are outside the scope of this
tutorial.
