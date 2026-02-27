# PR Review Workflow — Agent Instructions

You are an agent that reviews open pull requests for merge readiness and generates a ranked merge meeting document.

## Two-Phase Process

### Phase 1: Fetch Data

Run the fetch script to collect all PR data:

```bash
./scripts/fetch-prs.sh --repo <owner/repo> --output-dir artifacts/pr-review
```

This produces:

- `artifacts/pr-review/index.json` — summary of all open PRs
- `artifacts/pr-review/prs/{number}.json` — detailed data per PR

### Data Structure Reference

Each `prs/{number}.json` file has this top-level structure:

```json
{
  "pr": {
    "number": 123,
    "title": "...",
    "author": { "login": "username" },
    "isDraft": false,
    "mergeable": "MERGEABLE",
    "updatedAt": "2026-02-20T...",
    "headRefName": "feat/branch-name",
    "body": "PR description text...",
    "additions": 42,
    "deletions": 18,
    "changedFiles": 5,
    "labels": [{ "name": "bug" }],
    "milestone": { "title": "Merge Queue" },
    "statusCheckRollup": [...],
    "comments": [
      {
        "author": { "login": "github-actions" },
        "body": "# Amber Code Review\n### Blocker Issues\n..."
      }
    ],
    "reviewDecision": "APPROVED",
    "files": [...]
  },
  "reviews": [
    {
      "user": { "login": "reviewer", "type": "User" },
      "state": "CHANGES_REQUESTED",
      "body": "..."
    }
  ],
  "review_comments": [
    {
      "user": { "login": "reviewer", "type": "User" },
      "body": "inline comment text..."
    }
  ],
  "check_runs": [
    {
      "name": "ci/build",
      "conclusion": "success",
      "status": "completed"
    }
  ],
  "diff_files": [
    {
      "filename": "path/to/file.go",
      "status": "modified",
      "additions": 10,
      "deletions": 3,
      "patch": "@@ -1,5 +1,7 @@\n..."
    }
  ]
}
```

**Critical data path notes:**

- **PR comments** (including bot reviews like Amber Code Review) are at `pr.comments[]` — NOT at the top-level `reviews` or `review_comments`.
- **Reviews** (approve/request changes) are at the top-level `reviews[]` with `user.login` and `state` fields. The `user.type` field is `"User"` for humans and `"Bot"` for GitHub Apps.
- **Inline review comments** (code-level discussion threads) are at the top-level `review_comments[]` with `user.login`.
- **CI status** is in both `pr.statusCheckRollup[]` and the top-level `check_runs[]`. Use `check_runs` as the primary source — it has the `conclusion` field.
- **Milestone** is at `pr.milestone` — will be `null` or `{ "title": "..." }`.

### Phase 2: Analyze PRs

Read the fetched data and evaluate every PR against the blocker checklist below. Do **not** write the final report yet — the milestone count is needed first (see Phase 3).

## Blocker Checklist

For **every** open PR, evaluate each of these five categories. Each is either clear or a blocker.

### 1. CI

- Check `statusCheckRollup` and `check_runs`.
- **Clear:** all check runs have conclusion `success` or `neutral` (ignore `skipped`).
- **Blocker:** any check run with `failure`, `timed_out`, `cancelled`, or `action_required`. List the failing check names.

### 2. Merge Conflicts

- Check the `mergeable` field.
- **Clear:** `MERGEABLE`.
- **Blocker:** `CONFLICTING` or `UNKNOWN`. Note which files overlap with other open PRs if detectable.

### 3. Review Comments

Inspect **all three** data sources — they contain different types of feedback:

- `reviews[]` — formal review verdicts (APPROVED, CHANGES_REQUESTED, COMMENTED). Check the `state` field.
- `review_comments[]` — inline code-level discussion threads.
- `pr.comments[]` — general PR comments, **including bot reviews** (e.g., Amber Code Review from `github-actions`). Look for structured review comments with severity sections (Blocker Issues, Critical Issues, etc.).

Consider all authors equally — do not attempt to distinguish bots from humans.

For bot review comments (e.g., Amber Code Review), only the **last** bot review comment reflects the current state. When checking blocker/critical sections, treat the content as "None" (no issues) if the section body is any variation of: `None.`, `_None._`, `**None**`, `None identified.`, or is empty. These are all equivalent to "no issues found."

- **Clear:** no unresolved review threads, no outstanding `CHANGES_REQUESTED` review state (without a subsequent `APPROVED`), and no genuine blocker/critical issues in the latest bot review comment.
- **Blocker:** list the count of unresolved threads and summarise the topics (e.g., "2 threads: naming concern on `handler.go`, missing test for edge case"). Include any `CHANGES_REQUESTED` reviews that haven't been resolved. Flag genuine blocker/critical issues from bot reviews — but only if the issue is specific and real (e.g., compile errors, security issues, data races), not speculative or vague.

### 4. Jira Hygiene

- Scan the PR **title**, **body**, and **branch name** (`headRefName`) for Jira ticket patterns:
  - Primary: `RHOAIENG-\d+`
  - General: `[A-Z]{2,}-\d+` — but **exclude** non-Jira prefixes: `CVE`, `GHSA`, `HTTP`, `API`, `URL`, `PR`, `WIP`
- **Clear:** at least one Jira reference found.
- **Blocker:** no Jira reference detected. This is a hygiene issue — it should not prevent merging on its own but must be flagged.

### 5. Staleness

- **Clear:** `updatedAt` is within the last 30 days and the PR is not superseded.
- **Blocker:** flag if any of the following are true:
  - `updatedAt` is more than 30 days ago
  - Another open or recently merged PR targets the same files with a newer `createdAt` (superseded)
  - The fix described in the PR has already been merged via a different PR

## Ranking Logic

Produce a single ranked list of all open PRs, ordered by merge readiness:

1. **Blocker count** — PRs with zero blockers first, then one, then two, etc.
2. **Priority labels** — within the same blocker count, PRs with `priority/critical`, `bug`, or `hotfix` labels rank higher.
3. **Size (smaller first)** — PRs with fewer changed files and smaller diffs rank higher, reducing merge risk.
4. **Line-level conflict risk** — use diff hunk data (see below) to determine which mergeable PRs would actually collide. Rank the smaller PR first within a conflict pair.
5. **Dependency chains** — if a PR's branch is based on another PR's branch, the base PR must rank higher. Note these explicitly.
6. **Draft PRs last** — drafts always sort to the bottom regardless of other signals.

## Diff Hunk Analysis (Merge Order Optimisation)

For mergeable (non-draft) PRs, the fetch script collects `diff_files` — an array of per-file objects containing the `patch` field with actual diff content. Use this data to detect **line-level overlaps** between mergeable PRs and optimise merge order.

### How to parse hunks

Each `patch` string contains one or more hunk headers in unified diff format:

```
@@ -oldStart,oldCount +newStart,newCount @@ optional context
```

Extract the `newStart` and `newCount` values (the `+` side) for each hunk. These represent the line ranges the PR modifies in the target file. A hunk touches lines `newStart` through `newStart + newCount - 1`.

### How to detect overlaps

For every pair of mergeable PRs (A, B):

1. Find files that appear in both `diff_files` arrays (match on `filename`).
2. For each shared file, compare hunk ranges. Two hunks overlap if:
   - Hunk A: lines `a_start` to `a_start + a_count - 1`
   - Hunk B: lines `b_start` to `b_start + b_count - 1`
   - Overlap exists when `a_start <= b_start + b_count - 1` AND `b_start <= a_start + a_count - 1`
3. If any hunk pair overlaps, the two PRs have a **line-level conflict risk**.

### How to use overlap data

- **No overlapping hunks** between two PRs that touch the same file: they can merge in any order safely. Note this as "same file, no line overlap" — it's good news.
- **Overlapping hunks**: merge the smaller PR first to minimise rebase pain. Flag the overlap in the `{{NOTES}}` field with the specific file and line ranges.
- When multiple mergeable PRs form a chain of overlaps (A overlaps B, B overlaps C), recommend a specific merge sequence and explain why.

## Status Indicators

Use these in the **Status** column of the per-PR blocker table:

| Status | Meaning |
|--------|---------|
| `pass` | No issues detected |
| `FAIL` | Blocker — must be resolved before merge |
| `warn` | Hygiene / informational issue — does not block merge |

## Output Format

Use the template at `templates/merge-meeting.md`. Replace all `{{PLACEHOLDER}}` tokens with actual content. The template uses `{{#each PR_ENTRIES}}` / `{{/each}}` as structural markers — generate one PR block per open PR in ranked order.

For the per-PR blocker table:
- **Status** column: use `pass`, `FAIL`, or `warn` as defined above.
- **Detail** column: keep it short — one line. For `pass`, use `—` or a brief confirmation. For `FAIL`/`warn`, describe the specific issue.

### Diff overlap risk row

The blocker table includes a **Diff overlap risk** row. This is only meaningful for mergeable PRs that have `diff_files` data:

- **`pass`** — no line-level overlaps with any other mergeable PR.
- **`warn`** — shares files with another mergeable PR but hunks don't overlap. Safe to merge in any order.
- **`FAIL`** — line-level overlap detected with another mergeable PR. Merge order matters. Detail should name the conflicting PR(s), file(s), and line ranges.
- For non-mergeable PRs (no diff data), use `—` in both status and detail columns.

### Notes field

Use the optional `{{NOTES}}` field for:
- Dependency chain info ("Depends on #456 — merge that first")
- Diff overlap warnings with recommended merge order ("Overlaps with #789 on `handler.go:45-62` — merge this one first (smaller diff)")
- Superseded warnings ("May be superseded by #101")

## Phase 3: Milestone Management

Manage the **"Merge Queue"** milestone. This milestone acts as a living bucket of ready-to-merge PRs — no due date, never closed, updated every run. The milestone description stores the report and per-PR analysis timestamps, which are used as state on subsequent runs.

**Important: complete milestone sync BEFORE writing the final report** so that `{{MILESTONE_COUNT}}` in the report is accurate.

### Step 1: Find or create the milestone

```bash
# Find existing milestone
MILESTONE_NUM=$(gh api "repos/{owner}/{repo}/milestones" --jq '.[] | select(.title=="Merge Queue") | .number')

# If not found, create it
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api "repos/{owner}/{repo}/milestones" \
    -f title="Merge Queue" \
    -f state=open \
    -f description="Auto-managed by PR Overview workflow" \
    --jq '.number')
fi
```

### Step 2: Load previous state from milestone

If the milestone already has a description containing a previous report, parse it to extract per-PR `{{LAST_ANALYZED}}` timestamps. Build a map of `PR number → last analyzed timestamp`.

Compare each open PR's `updatedAt` against its `lastAnalyzed`:

| Condition | Action |
|-----------|--------|
| **New PR** — not in previous report | Full analysis (all blockers) |
| **Updated PR** — `updatedAt > lastAnalyzed` | Full re-analysis; set `{{LAST_ANALYZED}}` to now |
| **Unchanged PR** — `updatedAt <= lastAnalyzed` | Carry forward previous blocker results, but **always re-check CI and mergeable** (these are volatile and change without updating `updatedAt`) |
| **Gone PR** — in previous report but now merged/closed | Remove from milestone, drop from report |

Set `{{LAST_ANALYZED}}` to the current UTC timestamp for any PR that was fully analyzed or re-analyzed. For unchanged PRs, keep the previous `{{LAST_ANALYZED}}` value.

### Step 3: Sync PRs to the milestone

Based on the analysis results (whether fresh or carried forward):

- **Add** PRs with **0 blockers** (all statuses are `pass` or `warn`, no `FAIL`):
  ```bash
  gh api -X PATCH "repos/{owner}/{repo}/issues/{number}" -F milestone=${MILESTONE_NUM}
  ```
- **Remove** PRs currently in the milestone that now have blockers, are drafts, or have been merged/closed:
  ```bash
  gh api -X PATCH "repos/{owner}/{repo}/issues/{number}" -F milestone=null
  ```
- **Never** add draft PRs to the milestone.

**Note:** Use the REST API (`gh api -X PATCH .../issues/{number}`) instead of `gh pr edit --milestone`, which requires `read:org` scope that runners typically lack.

Use the `milestone` field from the fetched PR data (already included in `gh pr view` output) to identify which PRs are currently in the milestone without extra API calls.

After syncing, count the PRs now in the milestone — this is `{{MILESTONE_COUNT}}` for the report.

### Step 4: Write the final report

Now that milestone sync is complete and `{{MILESTONE_COUNT}}` is known, write the final report to `artifacts/pr-review/merge-meeting-{YYYY-MM-DD}.md` using the template.

### Step 5: Update milestone description with the report

Overwrite the milestone description with the final report, prefixed with a timestamp:

```bash
REPORT=$(cat artifacts/pr-review/merge-meeting-{date}.md)
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
DESCRIPTION="**Last updated:** ${TIMESTAMP}

${REPORT}"

gh api -X PATCH "repos/{owner}/{repo}/milestones/${MILESTONE_NUM}" \
  -f description="${DESCRIPTION}"
```

### Milestone constraints

- The milestone has **no due date** — it persists as a running bucket.
- Do **NOT** close the milestone — it is reused across runs.
- The description is **overwritten** each run (not appended).
- Always include the `Last updated` timestamp at the top of the description.
- The per-PR `{{LAST_ANALYZED}}` timestamps are the mechanism for incremental analysis — they must be preserved accurately.

## Important Notes

- Do NOT approve or merge any PRs. This workflow is read-only (except for milestone management).
- If the fetch script fails, report the error clearly and stop.
- Always include the PR URL as a link: `[#123](url)`.
- Size format: `X files (+A/-D)` where A = additions, D = deletions.
