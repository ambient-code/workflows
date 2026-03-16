---
name: fix
description: Generate inline fix suggestions for identified findings.
---

# Fix Documentation Skill

You are generating specific, actionable fix suggestions for documentation
issues identified during review. The output must be a self-contained artifact
that an independent agent — with no prior context about this review — can use
to create GitHub pull requests autonomously.

## Your Role

Read the findings and produce concrete fix suggestions grouped into pull
request units. Each suggestion must include enough context for reliable text
matching and a clear rationale. Classify every fix as automatable or
needs-human-input so a PR agent knows how to handle it.

## Critical Rules

- **Findings must exist.** If neither
  `artifacts/document-review/findings-review.md` nor
  `artifacts/document-review/findings-verify.md` exists, inform the user and
  recommend running `/review` first.
- **Be specific.** Every suggestion must include the exact text to change and
  the exact replacement.
- **Explain the rationale.** Don't just say "change X to Y" — explain why.
- **Prioritize by severity.** Address Errors first, then Gaps, then others.
- **Don't invent behavior.** If a fix requires knowledge of intended behavior
  you don't have, flag it as needing human input rather than guessing.
- **Self-contained output.** Every fix must include all context inline — do not
  reference findings files. A reader of the fixes file must understand each fix
  without access to any other artifact.
- **Precise text matching.** Include 2–4 lines of surrounding context above and
  below the target text so the consuming agent can locate it uniquely in the
  file, even if similar text appears elsewhere.
- **Classify every fix.** Mark each fix as `Automatable: Yes` (exact current
  and replacement text provided, no ambiguity) or `Automatable: No` (requires
  human decision, missing information, or new content that cannot be fully
  drafted).

## Process

### Step 1: Load Context

Read whichever findings files exist:

- `artifacts/document-review/findings-review.md` (from `/review`)
- `artifacts/document-review/findings-verify.md` (from `/verify`)
- `artifacts/document-review/findings-install-test.md` (from `/install-test`)
- `artifacts/document-review/findings-usage-test.md` (from `/usage-test`)

Optionally read `artifacts/document-review/report.md` for priority guidance.

If install-test or usage-test findings exist, pay special attention to the
**Troubleshooting Guide** sections — use them to generate error-handling
guidance, troubleshooting tips, and corrected commands for the installation
and usage documentation.

Collect repository metadata for the output file:

```bash
git remote get-url origin 2>/dev/null
git rev-parse --abbrev-ref HEAD 2>/dev/null
git rev-parse --short HEAD 2>/dev/null
```

Record the remote URL, default branch, and current commit SHA.

### Step 2: Generate Fix Suggestions

For each finding, produce a suggestion. Every suggestion must be
self-contained — inline the evidence and context from the finding so the fixes
file stands alone without cross-references.

**For each fix, read the target file** and extract 2–4 lines of surrounding
context above and below the text to change. This context block is what the
consuming agent will use to locate the exact edit position.

**For Errors (factually wrong):**

- Quote the incorrect text with surrounding context
- Provide the corrected text
- Cite the source of truth inline (code location and snippet, test output,
  etc.)
- Mark as `Automatable: Yes` when the correct value is known

**For Gaps (missing documentation):**

- Identify where the new content should go (which file, which section, after
  which existing line)
- Provide a complete draft if possible, or a draft with `[TODO: ...]` markers
  for parts that need human input
- Mark as `Automatable: Yes` if the draft is complete with no `TODO` markers,
  `Automatable: No` if it contains `TODO` markers or needs information you
  don't have

**For Inconsistencies (contradictions):**

- Quote both contradictory passages with their locations and surrounding
  context
- Recommend which version is correct (if determinable from code or test
  results)
- Suggest the unified text
- Mark as `Automatable: Yes` if the correct version is known,
  `Automatable: No` if a human must decide which version is authoritative

**For Stale (outdated):**

- Quote the outdated text with surrounding context
- Provide the updated text (if the correct current value is known)
- If the current value isn't known, flag what needs to be looked up and mark
  as `Automatable: No`

**For Improvements (clarity, structure):**

- Quote the current text with surrounding context
- Provide the improved version
- Explain what makes it better

### Step 3: Group into Pull Requests

Organize fixes into logical pull request units:

1. **Default grouping:** one PR per file — all fixes targeting the same file
   go into a single PR
2. **Exception — cross-file issues:** when an inconsistency or gap spans
   multiple files (e.g., contradictory statements that must be unified, or a
   new cross-reference between two docs), group those fixes into a single PR
3. **Exception — large files:** if a single file has more than 10 fixes, split
   into separate PRs by severity (Errors + Gaps in one PR, Improvements in
   another)

For each PR group, generate:

- A short PR title (under 70 characters)
- A PR description summarizing the changes with rationale
- An `Automatable` status for the whole PR: `Yes` (all fixes automatable),
  `Partial` (mix), or `No` (all fixes need input)
- If any fix needs human input, a "Human Input Needed" checklist in the PR
  description listing the specific decisions or information the reviewer must
  provide

### Step 4: Write the Fixes

Follow the template at `templates/fixes.md` exactly. Write to
`artifacts/document-review/fixes.md`.

## Output

- `artifacts/document-review/fixes.md`

## When This Phase Is Done

Report your findings:

- Number of fix suggestions generated
- How many are automatable vs need human input
- Number of suggested PRs they map to
- Most impactful fixes

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
