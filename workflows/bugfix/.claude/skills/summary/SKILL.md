---
name: summary
description: Scan all workflow artifacts and present a synthesized summary of findings, decisions, and status.
---

# Workflow Summary Skill

## Dispatch

This skill can be invoked at any point in the workflow — from the controller,
from speedrun, or directly by the user. It does not require prior phases to
have completed; it summarizes whatever exists so far.

---

You are producing a concise, high-signal summary of everything the bugfix
workflow has done so far. Your audience is someone who hasn't been watching
the workflow run — they want to know what happened, what was decided, and
what needs attention, without reading every artifact.

## Your Role

Scan the artifact directory, read what's there, and synthesize the important
findings into a single summary. Surface things that might otherwise get buried:
related PRs found, reproduction failures, review concerns, assumptions that
were never confirmed, decisions made on the user's behalf.

## Process

### Step 1: Discover Artifacts

Scan the artifact root directory to find everything the workflow has produced:

```bash
find artifacts/bugfix/ -type f -name '*.md' 2>/dev/null | sort
```

If `artifacts/bugfix/` doesn't exist or is empty, report that no artifacts
have been generated yet and stop.

### Step 2: Read All Artifacts

Read every artifact file found in Step 1. Don't skip any — even small or
seemingly unimportant files may contain notable findings.

### Step 3: Extract Key Findings

As you read each artifact, pull out information in these categories:

**Existing work discovered**
- Related PRs, duplicate issues, or prior fix attempts found during assessment
- Whether any of these were acted on or deferred

**Bug understanding**
- What the bug is and whether it was confirmed
- If reproduction failed, why
- If the assessment concluded the bug doesn't apply, what happened next

**Root cause and fix**
- The identified root cause (one sentence)
- What was changed and why
- Any alternative approaches that were considered but rejected

**Testing status**
- Whether the full test suite was run and passed
- New regression tests added
- Any test failures or gaps flagged during review

**Review concerns**
- The review verdict (solid / tests incomplete / fix inadequate)
- Any specific concerns or caveats raised
- Whether concerns were addressed or are still outstanding

**Outstanding items**
- Assumptions that were never confirmed by the user
- Decisions made without explicit user input
- Follow-up work recommended but not yet done
- Known limitations or edge cases not covered

**PR status**
- Whether a PR was created, and the URL
- Whether it was created via `gh pr create` or a manual compare URL
- What branch it targets

### Step 4: Present the Summary

Present the summary directly to the user using this structure:

```markdown
## Bugfix Workflow Summary

**Issue:** [title or one-line description]
**Status:** [where the workflow stopped — e.g., "PR created", "review complete, PR pending", "assessment only"]

### Key Findings
- [The most important things the user should know — 3-5 bullet points max]

### Decisions Made
- [Any choices made during the workflow, especially those made without explicit user input]

### Outstanding Concerns
- [Review caveats, untested edge cases, unconfirmed assumptions — or "None"]

### Artifacts
- [List of all artifact files with one-line descriptions]

### PR
- [PR URL and status, or "Not yet created"]
```

Keep it tight. The value of this summary is density — if it's as long as the
artifacts themselves, it's not a summary.

### Step 5: Write the Summary Artifact

Save the summary to `artifacts/bugfix/summary.md`.

## Rules

- **Read, don't assume.** Base everything on what the artifacts actually say,
  not on what you think happened during the workflow. If you weren't the agent
  that ran the earlier phases, you don't know what happened — read the files.
- **Flag what's missing.** If a phase was skipped or an artifact is absent,
  say so. "No reproduction report was generated" is useful information.
- **Don't editorialize.** Report what the artifacts say. If the review flagged
  a concern, include it. Don't soften it or add your own interpretation.
- **Keep it short.** The whole point is that nobody reads the full artifacts.
  If your summary is more than ~40 lines of markdown, cut it down.

## Output

- Summary presented directly to the user (inline)
- Summary saved to `artifacts/bugfix/summary.md`

## When This Phase Is Done

The summary is the deliverable. Present it and stop — there is no next phase
to recommend.

If dispatched by the controller or speedrun, announce which file you are
returning to and re-read it.
