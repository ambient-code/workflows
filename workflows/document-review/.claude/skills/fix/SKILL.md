---
name: fix
description: Generate inline fix suggestions for identified findings.
---

# Fix Documentation Skill

You are generating specific, actionable fix suggestions for documentation
issues identified during review. Each suggestion includes the problematic text
and a proposed replacement.

## Your Role

Read the findings, and for each one, produce a concrete inline suggestion that
someone can apply directly to the documentation file. Group suggestions by file
for easy application.

## Critical Rules

- **Findings must exist.** If `artifacts/document-review/findings.md` does not
  exist, inform the user and recommend running `/review` first.
- **Be specific.** Every suggestion must include the exact text to change and
  the exact replacement.
- **Explain the rationale.** Don't just say "change X to Y" — explain why.
- **Prioritize by severity.** Address Errors first, then Gaps, then others.
- **Don't invent behavior.** If a fix requires knowledge of intended behavior
  you don't have, flag it as needing human input rather than guessing.

## Process

### Step 1: Load Findings

Read `artifacts/document-review/findings.md`. Optionally read
`artifacts/document-review/report.md` for priority guidance.

### Step 2: Generate Fix Suggestions

For each finding, produce a suggestion based on its type:

**For Errors (factually wrong):**

- Quote the incorrect text
- Provide the corrected text
- Cite the source of truth (code location, test output, etc.)

**For Gaps (missing documentation):**

- Identify where the new content should go (which file, which section)
- Provide a draft outline or initial text
- Note what information is needed to complete it

**For Inconsistencies (contradictions):**

- Quote both contradictory passages with their locations
- Recommend which version is correct (if determinable)
- Suggest the unified text

**For Stale (outdated):**

- Quote the outdated text
- Provide the updated text (if the correct current value is known)
- If the current value isn't known, flag what needs to be looked up

**For Improvements (clarity, structure):**

- Quote the current text
- Provide the improved version
- Explain what makes it better

### Step 3: Group by File

Organize all suggestions by file path so someone can work through one file at
a time.

### Step 4: Write the Fixes

Write to `artifacts/document-review/fixes.md`:

```markdown
# Documentation Fix Suggestions

**Project:** [name]
**Generated:** [date]
**Total suggestions:** N

## Summary

| Severity | Suggestions |
|----------|-------------|
| Error | N |
| Gap | N |
| Inconsistency | N |
| Stale | N |
| Improvement | N |

## Fixes by File

### [path/to/document.md]

#### Fix 1: [brief description]

**Severity:** Error | **Finding:** [reference to finding]
**Location:** Section "[heading]", line N

**Current text:**

> The `--port` flag sets the listening port (default: 3000).

**Suggested replacement:**

> The `--listen-port` flag sets the listening port (default: 8080).

**Rationale:** The flag was renamed from `--port` to `--listen-port` in v2.0.
The default was also changed from 3000 to 8080. See `src/cli.py:45`.

---

#### Fix 2: [brief description]

...

### [path/to/another-doc.md]

...

## New Content Needed

### [path/to/file-or-new-file.md] — [topic]

**Finding:** [reference to Gap finding]
**Location:** Suggested new section in [file], after "[heading]"

**Draft outline:**

```markdown
## [New Section Title]

[Paragraph explaining the concept]

### [Subsection]

[Details needed — requires input from maintainers on intended behavior]
```

**What's needed to complete:** [List of information needed]

## Needs Human Input

These findings require knowledge the reviewer does not have:

- **[Finding reference]** — [Why human input is needed]
- ...
```

## Output

- `artifacts/document-review/fixes.md`

## When This Phase Is Done

Report your findings:

- Number of fix suggestions generated
- How many can be applied directly vs need human input
- Most impactful fixes
- Suggested order of application

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
