---
name: generation
description: Generate documentation updates based on code changes. Supports preview and apply modes.
---

# Documentation Generation

Given a code diff and a list of documentation files selected for updating,
generate minimal, format-correct updated content for each file.

## Modes

- **Preview mode** (during `/review`): Generate proposed changes, show diffs
  to the user. Do not write files.
- **Apply mode** (during `/update`): Generate changes, write them to disk,
  and show the diff of each change to the user so they can see exactly what
  was modified.

## Formatting

Match the existing format of each file. Do not mix syntax formats within
a file.

**Critical**: When generating updated file content, output RAW content only.
NEVER wrap the output in code fences (no `` ```markdown ``, no `` ``` ``).
The output must be the file content itself, ready to write directly to disk.

## Decision Logic Per File

For each file, apply this logic:

1. **Does this file document the EXACT thing being changed in the diff?**
   - If NO → skip this file (NO_UPDATE_NEEDED)

2. **Does the diff add something NEW that should be documented?**
   - If NO → skip (NO_UPDATE_NEEDED)

3. **Is that new thing already documented in this file?**
   - If YES → skip (NO_UPDATE_NEEDED)

4. **Otherwise** → add ONLY the specific change, nothing more

Do not restructure or rewrite surrounding content. Change only what the
diff justifies.

If the diff alone doesn't provide enough context to write an accurate
update, read the relevant source code to understand the behavior before
writing. If the behavior is still unclear, flag the update as needing
human review rather than guessing.

## User Instructions

The user may provide instructions when invoking `/update`:

- **Global instructions** (e.g., "keep changes minimal")
- **Per-file instructions** (e.g., "config.rst: only update the CLI usage
  example")

Per-file instructions override global instructions for that specific file.
