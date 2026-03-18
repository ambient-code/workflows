---
name: report
description: Consolidate all findings into a single deduplicated report grouped by severity.
---

# Report Skill

You are consolidating all documentation review findings into a single
authoritative report. This report is the primary deliverable of the workflow —
it contains every finding, deduplicated and grouped by severity.

## Your Role

Read all findings files, merge them into one consolidated list, remove
duplicates, and produce a report grouped by severity (Critical → High → Medium
→ Low). Every finding from every phase must appear in the report unless it
duplicates another.

## Critical Rules

- **Findings must exist.** If neither
  `artifacts/findings-review.md` nor
  `artifacts/findings-verify.md` exists, inform the user and
  recommend running `/review` first.
- **Include every finding.** This is not a summary — it is the consolidated
  record. Every finding from every phase must appear unless it is a duplicate.
- **Deduplicate across phases.** The same issue may be reported by review,
  verify, and install-test. Merge these into a single finding, noting which
  phases detected it in the **Source** field.
- **Group by severity.** Findings are organized under `## Critical`,
  `## High`, `## Medium`, and `## Low` headings, in that order.
- **Number findings within each group.** Use a severity prefix: C1, C2, …
  for Critical; H1, H2, … for High; M1, M2, … for Medium; L1, L2, … for Low.

## Process

### Step 1: Load Findings

Read whichever findings files exist:

- `artifacts/findings-review.md` (from `/review`)
- `artifacts/findings-verify.md` (from `/verify`)
- `artifacts/findings-install-test.md` (from `/install-test`)
- `artifacts/findings-usage-test.md` (from `/usage-test`)

Also read `artifacts/inventory.md` for context.

### Step 2: Merge and Deduplicate

Collect every finding from all files into a single list. For each finding,
record its severity, dimension, location, description, evidence, and which
phase produced it (review, verify, install-test, usage-test).

Identify duplicates — findings that describe the same issue in the same
location. When two or more phases report the same issue:

- Keep the version with the strongest evidence (e.g., install-test confirming
  a broken command trumps review suspecting it)
- Use the highest severity if they differ
- Merge the **Source** field to list all phases that detected it

### Step 3: Compute Statistics

Build a dimension × severity cross-tabulation from the deduplicated list: for
each of the 7 dimensions (Accuracy, Completeness, Consistency, Clarity,
Currency, Structure, Examples), count findings at each severity level (Critical,
High, Medium, Low). Include row and column totals.

For each dimension, assign a qualitative rating:

- **Good** — Few or no issues
- **Fair** — Some issues but generally acceptable
- **Poor** — Significant issues that need attention

### Step 4: Note Skipped Phases

Check whether optional phases were skipped and note the reason in the report:

- If `artifacts/findings-install-test.md` exists and contains `**Status:** Skipped`,
  include a note in the report with the skip reason (e.g., "Install-test was
  skipped: cluster credentials not available").
- If `artifacts/findings-install-test.md` does not exist at all, note that installation
  testing was not performed.
- If `artifacts/findings-usage-test.md` exists and contains `**Status:** Skipped`,
  include a note with the skip reason (e.g., "Usage-test was skipped:
  install-test did not succeed").
- If `artifacts/findings-usage-test.md` does not exist at all, note that usage testing
  was not performed.
- If `artifacts/findings-verify.md` does not exist, note that code verification was not
  performed.

This helps readers understand the scope of the review.

### Step 5: Write the Report

Follow the template at `templates/report.md` exactly. Write to
`artifacts/report.md`.

Write every finding under its severity heading. Each finding must include:

- **Dimension** — which quality dimension is affected
- **File** — file path and line in backticks (e.g., `docs/guide.md:42`)
- **Source** — which phase(s) detected it (review, verify, install-test,
  usage-test)
- **Issue** — what the problem is
- **Evidence** — quoted text, code snippet, or command output
- **Fix** — the correction, if known with high confidence (omit if unsure)
- **PR** — link to a fix PR, if one was created by `/create-prs` (omit
  initially; added later by the create-prs phase)

Omit any severity section that has zero findings (e.g., if there are no
Critical findings, omit the `## Critical` section entirely).

## Output

- `artifacts/report.md`

## When This Phase Is Done

Report to the user:

- Total findings (after deduplication)
- Breakdown by severity
- The top 3 most impactful findings
- Recommended next step

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
