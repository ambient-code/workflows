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
  `artifacts/findings-quality-review.md` nor
  `artifacts/findings-code-check.md` exists, inform the user and
  recommend running `/quality-review`, `/code-check`, or `/full-review`.
- **Include every finding.** This is not a summary — it is the consolidated
  record. Every finding from every phase must appear unless it is a duplicate.
- **Deduplicate across phases.** The same issue may be reported by
  quality-review and code-check. Merge these into a single finding, noting which phases detected
  it in the **Source** field.
- **Group by severity.** Findings are organized under `## Critical`,
  `## High`, `## Medium`, and `## Low` headings, in that order.
- **Number findings within each group.** Use a severity prefix: C1, C2, …
  for Critical; H1, H2, … for High; M1, M2, … for Medium; L1, L2, … for Low.

## Process

### Step 1: Load Findings

Read whichever findings files exist:

- `artifacts/findings-quality-review.md` (from `/quality-review`)
- `artifacts/findings-code-check.md` (from `/code-check`)

Also read `artifacts/inventory.md` for context.

### Step 2: Merge and Deduplicate

Collect every finding from all files into a single list. For each finding,
record its severity, dimension, location, description, evidence, and which
phase produced it (quality-review, code-check).

Identify duplicates — findings that describe the same issue in the same
location. When two or more phases report the same issue:

- Keep the version with the strongest evidence
- Use the highest severity if they differ
- Merge the **Source** field to list all phases that detected it

### Step 2.5: Identify Cross-Dependencies

Scan the deduplicated findings for dependencies — cases where fixing one
finding affects or requires fixing another. Common patterns:

- **Anchor dependencies.** A finding about misnumbered steps (e.g., step 4
  jumps to step 6) and a finding about a broken anchor link to one of those
  steps (e.g., `#6-test-rate-limiting`) are dependent — renumbering changes
  the correct anchor.
- **Shared content.** Multiple findings about the same concept (e.g., legacy
  feature references across several files) should be coordinated into one
  remediation effort.
- **Prerequisite fixes.** A finding that adds a new section (e.g., a missing
  CRD reference page) may resolve a separate finding about a broken link to
  that section.

For each dependency found, add a **Dependencies** field to the affected
findings listing the IDs of related findings (e.g., `Dependencies: C4, M5`).
Add the field to both sides of the dependency.

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

- If `artifacts/findings-quality-review.md` does not exist, note that quality
  review was not performed.
- If `artifacts/findings-code-check.md` does not exist, note that code
  verification was not performed.

This helps readers understand the scope of the review.

### Step 5: Write the Report

Follow the template at `templates/report.md` exactly. Write to
`artifacts/report.md`.

Write every finding under its severity heading. Each finding must include:

- **Dimension** — which quality dimension is affected
- **File** — file path and line in backticks (e.g., `docs/guide.md:42`).
  All paths must be relative to the repository root stated in the report
  header.
- **Source** — which phase(s) detected it (quality-review, code-check)
- **Issue** — what the problem is
- **Evidence** — quoted text, code snippet, or command output. For code-check
  findings, include the source file path and line (e.g.,
  `pkg/server/main.go:142`) so the reader can locate both the doc claim and
  the code reality.
- **Fix** — the correction, if known with high confidence (omit if unsure)
- **Dependencies** — IDs of related findings that should be fixed together
  or in a specific order (omit if none)

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
