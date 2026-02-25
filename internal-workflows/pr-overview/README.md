# PR Review Workflow

Automates pre-merge-meeting PR triage for a GitHub repository. Fetches all open PR data, analyzes merge readiness, and generates a structured meeting document.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated
- `jq` installed

## Quick Start

```bash
# 1. Fetch PR data
./scripts/fetch-prs.sh --repo ambient-code/platform

# 2. Run the agent to analyze and generate the report
#    (via Ambient Code Platform or Claude Code)
```

The agent reads the fetched data, applies merge readiness criteria, and writes a report to `artifacts/pr-review/merge-meeting-{date}.md`.

## Directory Structure

```
pr-review/
├── .ambient/
│   └── ambient.json           # Workflow config
├── CLAUDE.md                  # Agent behavioral instructions
├── scripts/
│   └── fetch-prs.sh           # Data fetching script
├── templates/
│   └── merge-meeting.md       # Output template
├── artifacts/
│   └── pr-review/             # Generated reports and raw data
└── README.md
```

## Fetch Script

```bash
./scripts/fetch-prs.sh --repo owner/repo [--output-dir artifacts/pr-review]
```

**Output:**

- `index.json` — array of all open PR summaries
- `prs/{number}.json` — detailed data per PR (reviews, CI checks, comments, and diff hunks for mergeable PRs)

## Merge Readiness Criteria

A PR is **ready to merge** when:
- CI passes (all checks green or neutral)
- Not a draft
- No merge conflicts
- No unresolved human review comments
- Latest automated review has no genuine critical issues

## Report Format

The output is a single ranked list of all open PRs, ordered by merge readiness (fewest blockers first). Each PR entry includes a blocker table covering:

| Blocker Category | What It Checks |
|------------------|----------------|
| CI | All check runs passing |
| Merge conflicts | `mergeable` status is not `CONFLICTING` |
| Human review comments | Unresolved threads from human reviewers |
| Agent review issues | Critical issues from automated code review bots |
| Jira hygiene | Jira ticket reference in body or branch name |
| Staleness | Updated within 30 days, not superseded |
| Diff overlap risk | Line-level hunk overlap with other mergeable PRs |

For mergeable PRs, the fetch script pulls actual diff patches from the GitHub API. The agent parses `@@` hunk headers to detect line-range overlaps between PR pairs, enabling smarter merge ordering (merge the smaller PR first when two overlap on the same lines).

A summary at the bottom tallies PRs by readiness bucket (clean, one blocker away, needs work, recommend closing).

## Customization

- Edit `templates/merge-meeting.md` to change the report format
- Edit `CLAUDE.md` to adjust readiness criteria or ordering logic
- The Jira pattern defaults to `RHOAIENG-\d+` but also catches any `[A-Z]{2,}-\d+` pattern
