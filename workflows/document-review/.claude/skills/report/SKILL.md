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

Also read `artifacts/document-review/inventory.md` for context.

### Step 2: Compute Statistics

Calculate:

- Total findings by severity (Error, Gap, Inconsistency, Stale, Improvement)
  across all findings files
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

- All Errors (factually wrong information misleads users)
- Critical Gaps (missing docs for important features)
- Patterns (e.g., "all CLI flag docs are outdated" rather than listing each
  one)

### Step 5: Recommend Fix Priority

Suggest an order for addressing issues:

1. Errors first (factually wrong content causes the most harm)
2. Gaps in critical paths (missing quickstart, missing install guide)
3. Stale content (outdated info is the next-worst after wrong info)
4. Inconsistencies (confusing but not wrong)
5. Improvements (nice to have)

### Step 6: Write the Report

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
