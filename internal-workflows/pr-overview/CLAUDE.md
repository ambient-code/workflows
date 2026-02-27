# PR Review Workflow — Agent Instructions

You are an agent that reviews open pull requests for merge readiness and generates a ranked merge meeting document.

## Task Checklist

Create these as your todo items at the start. Mark each one as you complete it — do not stop until all are done.

1. **Run fetch-prs.sh** — collect all PR data into artifacts/pr-review/
2. **Run analyze-prs.py** — produce analysis.json with blocker statuses and merge order
3. **Evaluate review comments** — spawn a sub-agent to read raw PR files for `needs_review` PRs and return verdicts
4. **Run test-merge-order.sh** — locally merge clean PRs in order, record which merged/conflicted
5. **Find or create Merge Queue milestone** — get the milestone number
6. **Sync PRs to milestone** — add clean PRs, remove ones with blockers
7. **Write the merge meeting report** — fill the template with all data including merge test results
8. **Update milestone description** — overwrite with the final report

**Do not stop after writing the report.** The milestone description update is the final deliverable.

## Workflow

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

Run the analysis script to evaluate every PR against the blocker checklist:

```bash
python3 ./scripts/analyze-prs.py --output-dir artifacts/pr-review
```

This produces:

- `artifacts/pr-review/analysis.json` — compact summary with stats, merge order, overlap data, and a `pr_index` (one line per PR: number, rank, title, author, fail_count, review_status). Small enough to read in one go.
- `artifacts/pr-review/analysis/{number}.json` — full per-PR analysis (all blocker statuses, details, labels, notes). Read these when you need detail on specific PRs.

The script prints a `needs_review` list of PR numbers that require your evaluation. The summary file also has a `needs_review` array.

**Review comments require evaluation.** Use **parallel sub-agents** to evaluate the `needs_review` PRs so the raw comment data doesn't flood your main context and evaluation runs fast.

Split the `needs_review` list into batches of ~10 PRs each and spawn sub-agents **in parallel** (multiple Task calls in a single message). Use this prompt for each batch:

> Read the PR data files listed below and evaluate each PR's review comments. For each PR, read `artifacts/pr-review/prs/{number}.json` — look at `pr.comments[]` (includes bot reviews) and the top-level `reviews[]` (formal verdicts).
>
> **Bot review comments (e.g., "Amber Code Review" from github-actions) are real code reviews.** They analyzed the actual diff. If the latest bot review lists Blocker or Critical issues with specific descriptions, that is a FAIL — do NOT dismiss them as informational.
>
> For each PR, return: PR number, verdict (FAIL or pass), and a one-line summary of the issue (or "no issues" for pass). Only mark pass if the review explicitly found no issues or findings are purely minor/style.
>
> PRs to evaluate: {batch list}

Each sub-agent reads the **full, untruncated** raw PR files directly — no data loss.

Collect all verdicts from the parallel sub-agents and update each PR's `review_status` and `fail_count` in your working data before proceeding.

**Do not rewrite the analysis script.** If you need to adjust a deterministic check, edit `scripts/analyze-prs.py` directly. Do **not** write the final report yet — the milestone count is needed first (see Phase 3).

## Blocker Checklist

For **every** open PR, evaluate each of these five categories. Each is either clear or a blocker.

### 1. CI

- Check `check_runs` (primary) and `statusCheckRollup` (fallback).
- **Clear:** all completed check runs have conclusion `success` or `neutral` (ignore `skipped`).
- **Warn:** check runs still in progress (`status` is `queued` or `in_progress`) — CI hasn't finished yet.
- **Blocker:** any completed check run with `failure`, `timed_out`, `cancelled`, or `action_required`. List the failing check names.

### 2. Merge Conflicts

- Check the `mergeable` field.
- **Clear:** `MERGEABLE`.
- **Blocker:** `CONFLICTING` or `UNKNOWN`. Note which files overlap with other open PRs if detectable.

### 3. Review Comments

The script handles two deterministic checks automatically:
- **CHANGES_REQUESTED** without a subsequent APPROVED or DISMISSED → `FAIL`
- **Inline review threads** (from `review_comments[]`) → `FAIL` with count

For PRs with `review_status: "needs_review"`, spawn a sub-agent to read the raw PR data at `prs/{number}.json` and evaluate comments. The sub-agent reads the full untruncated data and returns a FAIL/pass verdict per PR. See Phase 2 instructions above for the sub-agent prompt.

### 4. Jira Hygiene

- Scan the PR **title**, **body**, and **branch name** (`headRefName`) for Jira ticket patterns:
  - Primary: `RHOAIENG-\d+`
  - General: `[A-Z]{2,}-\d+` — but **exclude** non-Jira prefixes: `CVE`, `GHSA`, `HTTP`, `API`, `URL`, `PR`, `WIP`
- **Clear:** at least one Jira reference found.
- **Blocker:** no Jira reference detected. This is a hygiene issue — it should not prevent merging on its own but must be flagged.

### 5. Staleness

The analysis script flags PRs older than 30 days and detects potential supersession (newer PRs with similar branches/titles). But **use your judgment** beyond the script's output — the script provides `days_since_update`, `recommend_close`, and `superseded_by` fields as signals, not final verdicts.

Consider recommending closure for PRs that show multiple signs of abandonment:
- Draft PR + merge conflicts + no activity in 3+ weeks
- Multiple blockers + no updates in 30+ days
- Superseded by a newer PR from the same author
- Very old (60+ days) regardless of other signals

Do not waste report space on these — use the condensed "Recommend Closing" table instead of a full blocker breakdown.

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

Use the template at `templates/merge-meeting.md`. Populate it from `analysis.json`.

### Dates

Use absolute dates in `YYYY-MM-DD` format (e.g., `2026-02-27`). Do not use relative dates like "2 days ago" — the report is stored in the milestone description and becomes stale.

### At a Glance

A 2-3 sentence summary at the top of the report. Mention how many PRs are ready, call out the top 3-4 smallest ones by number, and flag any notable concerns (e.g., "3 PRs recommended for closure", "6 PRs blocked by merge conflicts").

### Clean PRs (condensed table)

PRs with `fail_count == 0` and `isDraft == false` go in the condensed summary table — one row per PR. List them in the order from the `merge_order` array (smallest and least conflicting first).

The **Merge Test** column shows the result from `test-merge-order.sh`:
- `merged` — PR merged cleanly on top of all previous PRs in the sequence
- `CONFLICT` — merge failed; note the conflicting file(s)
- `not attempted` — skipped because an earlier PR conflicted

The **Notes** column: overlap warnings, jira hygiene, or "—".

After the table, if any PR conflicted, add a **Resolution Strategy** section explaining:
- Which PRs conflicted and on which files
- Who owns the conflicting PR and what they need to do (rebase on top of which PR)
- Which downstream PRs are blocked and will need rebasing once the conflict is resolved

### PRs With Blockers (full tables)

PRs with `fail_count > 0` and `isDraft == false` get the full blocker table. PRs flagged with `recommend_close == true` go in the "Recommend Closing" table instead — do **not** give them a full blocker breakdown.

### Recommend Closing

PRs flagged by the script (`recommend_close == true`) or that you judge to be abandoned. One-row-per-PR table with: PR link, author, reason, last updated (relative). Use your judgment to add PRs the script missed.

### Status indicators

| Status | Meaning |
|--------|---------|
| `pass` | No issues detected |
| `FAIL` | Blocker — must be resolved before merge |
| `warn` | Hygiene / informational issue — does not block merge |

## Phase 3: Test Merge Order

After analysis and review evaluation, test the merge order locally to verify clean PRs actually merge without conflicts:

```bash
MERGE_ORDER=$(python3 -c "import json; d=json.load(open('artifacts/pr-review/analysis.json')); print(' '.join(str(n) for n in d['merge_order']))")

./scripts/test-merge-order.sh \
  --repo <owner/repo> \
  --repo-dir /workspace/repos/<repo-name> \
  --prs "$MERGE_ORDER"
```

This creates a temporary local branch, fetches all PR refs (including forks via `refs/pull/*/head`), and merges each PR in sequence. It stops on the first conflict and reports results as JSON.

**The script NEVER pushes to any remote.** The push URL is overridden to `/dev/null` and the tmp branch is deleted on exit.

Use the results to:
- Mark each clean PR's merge test result in the report table (merged / conflict / not attempted)
- For conflicts: note the conflicting files and which PR pair caused it
- For not-attempted PRs: explain why (blocked by earlier conflict)
- Add a **resolution strategy** after the table explaining what needs to happen to unblock the remaining PRs (who needs to rebase, which file, what the conflict is about)

If the merge test script is not available or fails, skip this phase and note it in the report.

## Phase 4: Milestone Management

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

### Step 2: Sync PRs to the milestone

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

### Step 3: Write the final report

Now that milestone sync is complete and `{{MILESTONE_COUNT}}` is known, write the final report to `artifacts/pr-review/merge-meeting-{YYYY-MM-DD}.md` using the template.

### Step 4: Update milestone description with the report

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

## Important Notes

- Do NOT approve or merge any PRs. This workflow is read-only (except for milestone management).
- If the fetch script fails, report the error clearly and stop.
- Always include the PR URL as a link: `[#123](url)`.
- Size format: `X files (+A/-D)` where A = additions, D = deletions.
