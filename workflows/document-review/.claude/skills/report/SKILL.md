---
name: report
description: Generate a prioritized executive summary from findings.
---

# Report Skill

You are generating a clean, prioritized summary report from documentation
review findings. This report is the primary deliverable of the workflow — it
should be actionable and easy to scan.

## Your Role

Read the findings file, synthesize the results, and produce a report that helps
the user understand the overall documentation health and prioritize what to fix
first.

## Critical Rules

- **Findings must exist.** If neither
  `artifacts/document-review/findings-review.md` nor
  `artifacts/document-review/findings-verify.md` exists, inform the user and
  recommend running `/review` first.
- **Be concise.** The report is a summary, not a copy of the findings. Link to
  findings for details.
- **Prioritize actionably.** Order recommendations by impact, not just severity
  count.
- **Include statistics.** Quantify the findings so the user can gauge the
  overall health.

## Process

### Step 1: Load Findings

Read whichever findings files exist:

- `artifacts/document-review/findings-review.md` (from `/review`)
- `artifacts/document-review/findings-verify.md` (from `/verify`)
- `artifacts/document-review/findings-install-test.md` (from `/install-test`)
- `artifacts/document-review/findings-usage-test.md` (from `/usage-test`)

Also read `artifacts/document-review/inventory.md` for context.

### Step 2: Compute Statistics

Calculate:

- Total findings by severity (Critical, High, Medium, Low) across all findings
  files
- Total findings by dimension (Accuracy, Completeness, Consistency, Clarity,
  Currency, Structure, Examples)
- Findings per document (which docs have the most issues)

### Step 3: Assess Overall Health

Provide a qualitative assessment for each dimension:

- **Good** — Few or no issues, docs are solid in this area
- **Fair** — Some issues but generally acceptable
- **Poor** — Significant issues that need attention

### Step 4: Identify Top Issues

Select the highest-impact findings to highlight:

- All Critical findings (factually wrong information, broken commands)
- All High findings (significant gaps, contradictions, outdated content)
- Patterns (e.g., "all CLI flag docs are outdated" rather than listing each
  one)

### Step 5: Recommend Fix Priority

Suggest an order for addressing issues:

1. Critical first (factually wrong content, broken commands cause the most harm)
2. High next (missing docs, contradictions, outdated content)
3. Medium (confusing but has workarounds)
4. Low (nice to have improvements)

### Step 6: Note Skipped Phases

Check whether optional phases were skipped and note the reason in the report:

- If `findings-install-test.md` exists and contains `**Status:** Skipped`,
  include a note in the report with the skip reason (e.g., "Install-test was
  skipped: cluster credentials not available").
- If `findings-install-test.md` does not exist at all, note that installation
  testing was not performed.
- If `findings-usage-test.md` exists and contains `**Status:** Skipped`,
  include a note with the skip reason (e.g., "Usage-test was skipped:
  install-test did not succeed").
- If `findings-usage-test.md` does not exist at all, note that usage testing
  was not performed.
- If `findings-verify.md` does not exist, note that code verification was not
  performed.

This helps readers understand the scope of the review.

### Step 7: Write the Report

Follow the template at `templates/report.md` exactly. Write to
`artifacts/document-review/report.md`.

## Output

- `artifacts/document-review/report.md`

## When This Phase Is Done

Report your findings:

- Overall documentation health (one-line summary)
- Number of issues by severity
- The top 3 most critical issues
- Recommended next step

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
