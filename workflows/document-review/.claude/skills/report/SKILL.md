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

- **Findings must exist.** If `artifacts/document-review/findings.md` does not
  exist, inform the user and recommend running `/review` first.
- **Be concise.** The report is a summary, not a copy of the findings. Link to
  findings for details.
- **Prioritize actionably.** Order recommendations by impact, not just severity
  count.
- **Include statistics.** Quantify the findings so the user can gauge the
  overall health.

## Process

### Step 1: Load Findings

Read `artifacts/document-review/findings.md` and optionally
`artifacts/document-review/inventory.md` for context.

### Step 2: Compute Statistics

Calculate:

- Total findings by severity (Error, Gap, Inconsistency, Stale, Improvement)
- Total findings by dimension (Accuracy, Completeness, Consistency, Clarity,
  Currency, Structure, Examples)
- Findings per document (which docs have the most issues)
- If test results are included, pass/fail rates for executable instructions

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

Write to `artifacts/document-review/report.md`:

```markdown
# Documentation Review Report

**Project:** [name]
**Generated:** [date]
**Documents reviewed:** N of M
**Total findings:** N

## Overall Health

| Dimension | Rating | Issues |
|-----------|--------|--------|
| Accuracy | Good/Fair/Poor | N |
| Completeness | Good/Fair/Poor | N |
| Consistency | Good/Fair/Poor | N |
| Clarity | Good/Fair/Poor | N |
| Currency | Good/Fair/Poor | N |
| Structure | Good/Fair/Poor | N |
| Examples | Good/Fair/Poor | N |

## Findings Summary

| Severity | Count |
|----------|-------|
| Error | N |
| Gap | N |
| Inconsistency | N |
| Stale | N |
| Improvement | N |

## Top Issues

### 1. [Most critical issue]

**Severity:** Error | **Dimension:** Accuracy
**Location:** [file:section]
[Brief description and why it matters]

### 2. [Second most critical]

...

## Documents Needing Attention

| Document | Errors | Gaps | Other | Total |
|----------|--------|------|-------|-------|
| [most issues first] | N | N | N | N |
| ... | ... | ... | ... | ... |

## Instruction Test Results (if /test was run)

- **Instruction blocks tested:** N
- **Passed:** N
- **Failed:** N
- **Skipped:** N

## Recommended Fix Priority

1. **[Category]** — [Why this should be fixed first]
2. **[Category]** — [Why this is next]
3. ...

## Next Steps

- Run `/fix` to generate inline fix suggestions
- Run `/verify` for deeper code cross-referencing (if not already done)
- Run `/test` to validate executable instructions (if not already done)

---

*Full findings: artifacts/document-review/findings.md*
*Document inventory: artifacts/document-review/inventory.md*
```

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
