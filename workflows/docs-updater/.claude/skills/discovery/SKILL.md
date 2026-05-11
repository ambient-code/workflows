---
name: discovery
description: Find documentation files that need updates based on code changes. Default mode uses identifier matching and grep. Optional semantic indexing for large repos.
---

# Documentation Discovery

Given a code diff and a docs repository, identify which documentation files
need updating based on the code changes.

## Modes

- **Discovery mode** (default): Find files that need updating using identifier
  matching and grep — no setup required, works immediately
- **Index-assisted mode**: If semantic indexes exist (`.doc-index/`), use them
  for faster discovery on large repos
- **Index-build mode** (when invoked via `/index`): Build or rebuild semantic
  indexes only

## Discovery Process (Default — No Indexes)

Follow these steps in order. Do not skip steps.

### Step 1: Receive the diff and changed file list

Use the diff provided by the controller. Record the list of changed files:

```bash
git diff --name-only <base>...<head>
```

If no changes can be identified, stop and report.

### Step 2: Build the identifier checklist

Go through **every** changed file in the diff. For each file, extract
identifiers from the modified lines (lines starting with `+` or `-`) and
from diff hunk headers (`@@` lines).

Identifiers to extract:
- Function and method names
- Class and type names
- CLI flag names and configuration keys
- API endpoint paths
- Constants and variable names that appear in public interfaces

Use the most specific form of each identifier. Full function names, CLI
flags, and config keys are good — they match only relevant docs. Avoid
short generic words that would match hundreds of unrelated files.

Write them as a numbered checklist — one entry per changed file, with all
identifiers from that file. **Do not skip files.** Every changed file gets
an entry. This checklist is your contract — you will search docs for every
identifier on it.

### Step 3: Discover documentation files

Find all text-based documentation files in the docs location:

```bash
find {docs_root} -type f \( -name "*.md" -o -name "*.adoc" -o -name "*.rst" \
  -o -name "*.txt" -o -name "*.html" -o -name "*.yaml" -o -name "*.yml" \) \
  ! -path "*/.git/*" ! -path "*/.doc-index/*" ! -path "*/node_modules/*"
```

If the location has no documentation files, produce zero findings and stop.

### Step 4: Search docs for every identifier

Write a shell script that greps for each identifier across the documentation
files. Run it in a single Bash call:

```bash
for id in "identifier1" "identifier2" "identifier3"; do
  matches=$(grep -rl "$id" {docs_root} --include="*.md" --include="*.adoc" --include="*.rst" --include="*.txt" --include="*.html" --include="*.yaml" --include="*.yml" 2>/dev/null)
  if [ -n "$matches" ]; then
    echo "MATCH: $id -> $matches"
  fi
done
```

Include **every** identifier from the checklist. No identifiers are skipped.

From the output, collect all matched doc files into a candidate list.
Exclude documentation files that are already modified in the same diff —
those are being actively updated.

### Step 5: Evaluate candidates (two passes)

**Pass 1 — Quick scan.** For each candidate doc file from step 4, view
only the lines that matched (use `grep -n` to see them in context). Based
on the matching lines alone, decide whether the doc might be stale:

```
- path/to/doc.md → possibly stale (describes behavior that changed)
- path/to/other.md → not stale (mentions identifier in passing)
- path/to/another.md → not stale (changelog entry, historical)
```

Every candidate must have a verdict. Do not skip candidates.

**Pass 2 — Deep read.** For each candidate marked "possibly stale" in
pass 1, read the relevant sections of the file alongside the corresponding
part of the diff. Confirm whether the doc is actually stale.

When evaluating:
- **Only flag docs whose content is now incorrect.** A doc that mentions
  an identifier is not stale if the described behavior is unchanged.
- **Do not flag changelog entries or release notes** that describe past
  releases — historical entries are not stale.
- **Do not flag docs about a different component** that happens to share
  an identifier name.

### Step 6: Present results

For each confirmed stale doc, present to the user:

- File path
- What is stale and why (reference the specific code change)
- What should be updated

Use `AskUserQuestion` to let the user confirm or modify the selection.
Present files as options the user can accept or reject individually.

## Index-Assisted Discovery (Optional — For Large Repos)

If `.doc-index/` exists in the docs location, use it for faster discovery.

The value of indexes is **only realized when they are committed and pushed**
so that subsequent runs (by you or other users) can reuse them. Building
indexes without committing them is equivalent to the default grep-based
approach but slower and more token-costly. Only suggest `/index` when the
user intends to persist them.

### How it works

1. Read all `{docs_root}/.doc-index/*.index.md` files — these are compact
   per-folder summaries
2. For each index, determine: would documentation in this area become
   incorrect based on this diff?
3. Only folders that pass this check are scanned — the rest are skipped
4. Within relevant folders, apply the same identifier matching and grep
   process from the default mode (Steps 2-5)

This narrows the search from all folders to just 2-3 relevant ones,
which matters on locations with many doc folders.

### When to suggest indexing

After completing discovery in default mode, if the docs location has more
than 15 documentation files across 3+ folders, suggest running `/index`
and committing the indexes to speed up future runs.

## Index Build Mode (`/index`)

When invoked via `/index`, build semantic indexes without running discovery.

### Process

Scan the docs location for top-level folders containing documentation files.
Skip hidden directories and internal folders (starting with `_` or `.`).

For each folder:

1. Read all documentation files in the folder
2. Generate a semantic index with these sections:

```markdown
# {FOLDER} Documentation Index

## Overview
[2-3 sentences describing what this documentation area covers]

## Files Summary
[Each file with a 1-2 sentence description of its purpose]

## Code Changes That Would Require Documentation Updates
[Specific types of code changes that would make these docs outdated]

## Key Technical Concepts
[Important terms, APIs, configuration options, commands]

## Related Components
[System components, modules, or subsystems this documentation describes]
```

3. Write the index to `{docs_root}/.doc-index/{folder-name}.index.md`

After building all indexes, update `{docs_root}/.doc-index/manifest.json`:

```json
{
  "version": "1.0",
  "updated": "<ISO 8601>",
  "folders": {
    "folder-name": {
      "built": "<ISO 8601>",
      "doc_hashes": {
        "folder-name/file.md": "<sha256>"
      }
    }
  }
}
```

### Hash-based invalidation

Before rebuilding an index, compare current file hashes against
`manifest.json`. Only rebuild folders where file hashes changed. Skip
unchanged folders.

```bash
sha256sum {docs_root}/{folder}/*.md {docs_root}/{folder}/*.adoc {docs_root}/{folder}/*.rst 2>/dev/null
```

### Committing indexes

After building indexes, ask the user via `AskUserQuestion` where to commit
them. Indexes only have value if they are persisted:

- **Commit to current branch** — indexes travel with the doc changes
- **Commit to main/default branch** — indexes persist across all sessions (recommended)

If the user chooses not to commit, warn that the indexes will be lost when
the session ends and the default grep-based discovery will be used next time.

Do not push to any branch without explicit confirmation.

## Output

Return the list of selected file paths (confirmed by the user) to the
controller for the generation phase.
