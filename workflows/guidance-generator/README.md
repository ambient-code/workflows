# PR Guidance Generator

Analyzes a GitHub repository's fix PR history to generate compact guidance files
that teach automated workflows — CVE Fixer and Bugfix — how to create pull requests
that match that repo's conventions. Opens a PR in the target repo with the generated files.

## Problem It Solves

Automated fix workflows (CVE Fixer, Bugfix) create PRs without knowing a repo's
specific conventions: how titles should read, which files always change together,
what reviewers will ask for, what gets PRs closed. This leads to PRs that get
closed or require many review cycles.

This workflow learns those conventions directly from the repo's PR history and
encodes them into guidance files that automated workflows read before making changes.

## How It Works

1. Fetches PR metadata from the target repo (titles, branches, labels)
2. Filters into CVE and bugfix buckets based on title/branch patterns
3. Fetches targeted details per PR: files changed + review REQUEST_CHANGES comments
4. For closed PRs: fetches the closing context to extract "don'ts"
5. Synthesizes rules using an adaptive threshold based on available data
6. Generates compact guidance files (80-line cap, one rule per line)
7. Opens a PR in the target repo adding the files

## Commands

### `/guidance.generate <repo-url>`

Full pipeline for a fresh repo. Analyzes all recent fix PRs automatically,
or analyze specific PRs of your choice with `--pr`.

```
/guidance.generate https://github.com/org/repo
/guidance.generate org/repo --cve-only
/guidance.generate org/repo --bugfix-only
/guidance.generate org/repo --limit 50
/guidance.generate org/repo --pr https://github.com/org/repo/pull/42,https://github.com/org/repo/pull/87
/guidance.generate org/repo --pr 42,87
```

Flags:
- `--cve-only` / `--bugfix-only`: generate only one of the two guidance files
- `--limit N`: cap the number of PRs fetched per bucket (default: 100)
- `--pr <refs>`: comma-separated PR URLs or numbers — skips bulk fetch and
  analyzes only these PRs. Useful for seeding guidance from a curated set of
  representative PRs. The generated file header records which PRs were used.

Generates:
- `.cve-fix/examples.md` — read by the CVE Fixer workflow (step 4.5)
- `.bugfix/guidance.md` — read by the Bugfix workflow

### `/guidance.update <repo-url>`

Refreshes existing guidance with PRs merged/closed since the last analysis.
Reads the `last-analyzed` date from existing files, fetches only newer PRs,
merges new patterns, and opens a PR with the updates.

```
/guidance.update https://github.com/org/repo
/guidance.update org/repo --pr https://github.com/org/repo/pull/103
/guidance.update org/repo --pr 103,104
```

Flags:
- `--pr <refs>`: instead of fetching all PRs since the last-analyzed date,
  merge only the specified PRs into existing guidance. The `last-analyzed`
  date is still updated to today.

## Generated File Format

Files are intentionally compact. Example `.cve-fix/examples.md`:

```markdown
# CVE Fix Guidance — org/repo
<!-- last-analyzed: 2026-03-29 | cve-merged: 47 | cve-closed: 12 -->

## Titles
`Security: Fix CVE-YYYY-XXXXX (<package>)` (47/47)

## Branches
`fix/cve-YYYY-XXXXX-<package>-attempt-N` (47/47)

## Files — Go stdlib CVEs
Always update go.mod + Dockerfile + Dockerfile.konflux together (8/8)
Run go mod tidy — missing go.sum was flagged in 3 closed PRs

## Files — Node.js CVEs
Use overrides in package.json, not direct npm update (5/5)

## Co-upgrades
fastapi must be co-upgraded with starlette (2 closed PRs lacked this)

## PR Description
Required sections (missing caused REQUEST_CHANGES in 6 PRs):
- CVE Details, Test Results, Breaking Changes, Jira refs (plain text IDs only)

## Don'ts
- One CVE per PR — combined PRs were closed (4 cases)
- Don't target release branches — target main (3 cases)
```

## Rule Threshold

Rules use an adaptive threshold based on how much data is available in each bucket:

| Merged PRs in bucket | Min PRs per rule |
|----------------------|-----------------|
| 10+                  | 3               |
| 3–9                  | 2               |
| 1–2                  | 1 + `WARNING: limited data` in header |
| 0                    | File skipped entirely |

This means the workflow always produces something useful, even for repos with
few fix PRs — while flagging low-confidence output clearly.

## Line Count Behaviour

The 80-line target applies differently depending on the command:

**`/guidance.generate`** — treats 80 lines as a formatting target for new files.
All rules that meet the evidence threshold are included regardless. If the natural
output exceeds 80 lines, all rules are kept and the line count is noted in the PR.

**`/guidance.update`** — never drops existing rules to stay under 80 lines.
New rules are always appended in full. If the file grows past 80 lines, the PR
description flags it with a suggestion to run `/guidance.generate` to rebuild
and consolidate the guidance from scratch with the full updated history.

## Token Efficiency

The workflow uses a two-pass fetch strategy to minimize API calls and context size:

- **Pass 1**: Lightweight metadata for all PRs (title, branch, labels, state).
  In `--pr` mode this pass is skipped — only the specified PRs are fetched.
- **Pass 2**: Per-PR detail only for PRs in the CVE/bugfix buckets (files + reviews)
- **Closed PRs only**: Fetch closing context (last 2 comments)

This avoids fetching full PR bodies and review threads for irrelevant PRs,
keeping the analysis input compact (structured JSON, ~200 tokens/PR).

## How Automated Workflows Use the Files

**CVE Fixer** (`/cve.fix`): In step 4.5, after cloning repos and before making
any fixes, the workflow reads all files in `.cve-fix/` and builds a knowledge base
from them. The guidance from `examples.md` applies to every subsequent decision —
PR title format, branch naming, which files to update, co-upgrade requirements,
Jira reference format, and known pitfalls.

**Bugfix workflow**: Reads `.bugfix/guidance.md` before implementing fixes.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated (`gh auth login`)
- `jq` installed
- Write access to the target repository (to open a PR)

## Artifacts

All artifacts are saved to `artifacts/guidance/<repo-slug>/`:

```
artifacts/guidance/<repo-slug>/
├── raw/
│   ├── cve-prs.json          # Compact per-PR records for CVE bucket
│   └── bugfix-prs.json       # Compact per-PR records for bugfix bucket
├── analysis/
│   ├── cve-patterns.md       # Intermediate pattern extraction
│   └── bugfix-patterns.md
└── output/
    ├── cve-fix-guidance.md   # Final file (placed at .cve-fix/examples.md)
    └── bugfix-guidance.md    # Final file (placed at .bugfix/guidance.md)
```
