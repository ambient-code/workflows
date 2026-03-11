# Review Queue — Agent Instructions

You are an agent that evaluates open pull requests and generates a prioritized review queue — an ordered list of what needs human attention, ranked by urgency and type.

## Task Checklist

Create these as your todo items at the start. Mark each one as you complete it.

1. **Fetch & analyze** — run `fetch-prs.sh` then `analyze-prs.py`
2. **Evaluate PRs** — spawn one sub-agent per PR (parallel, never batch)
3. **Milestone sync** — find/create milestone, add clean PRs, remove blocked ones
4. **Write report & update milestone** — generate report, set as milestone description
5. **Comment on blocked PRs** — post blocker summaries (skip if auth fails)
6. **Self-evaluate** — read `.ambient/rubric.md` and score efficiency

## Workflow

### Phase 1: Fetch Data

Run the fetch script to collect all PR data:

```bash
./scripts/fetch-prs.sh --repo <owner/repo> --output-dir artifacts/pr-review
```

This produces:

- `artifacts/pr-review/index.json` — raw PR index (**do not read directly** — can exceed token limits. The analyze script reads this for you.)
- `artifacts/pr-review/prs/{number}.json` — raw PR data (**do not read directly** — use summaries and analysis files instead.)

### Data Structure Reference

Each `prs/{number}.json` file has this top-level structure (for reference — the analyze script reads these, you don't need to):

```json
{
  "pr": {
    "number": 123,
    "title": "...",
    "author": { "login": "username" },
    "isDraft": false,
    "isCrossRepository": true,
    "headRepositoryOwner": { "login": "fork-owner" },
    "mergeable": "MERGEABLE",
    "updatedAt": "2026-02-20T...",
    "headRefName": "feat/branch-name",
    "body": "PR description text...",
    "additions": 42,
    "deletions": 18,
    "changedFiles": 5,
    "labels": [{ "name": "bug" }],
    "milestone": { "title": "Review Queue" },
    "statusCheckRollup": [...],
    "comments": [...],
    "reviewDecision": "APPROVED",
    "files": [...]
  },
  "reviews": [...],
  "review_comments": [...],
  "check_runs": [...],
  "diff_files": [...]
}
```

### Phase 2: Analyze PRs

Run the analysis script to evaluate every PR against the blocker checklist and classify by type:

```bash
python3 ./scripts/analyze-prs.py --output-dir artifacts/pr-review
```

This produces:

- `artifacts/pr-review/analysis.json` — compact summary with stats, review order, overlap data, and a `pr_index` (one line per PR with number, rank, title, author, type, fail_count, review_status).
- `artifacts/pr-review/analysis/{number}.json` — full per-PR analysis (all blocker statuses, type classification, details).
- `artifacts/pr-review/summaries/{number}.md` — **agent-friendly markdown summary** per PR with blocker table, comment counts, and notes. Read these instead of the raw JSON for quick triage.
- `artifacts/pr-review/reviews/{number}/` — unified chronological comment stream per PR:
  - `meta.json` — PR number, title, author, total comment count
  - `01.json`, `02.json`, ... — each comment in chronological order with timestamp, author, body, and source hint

### Phase 3: PR Evaluation

Evaluate each PR that needs review. **One PR per sub-agent** — spawn them in parallel for speed, but never batch multiple PRs into a single agent (that causes context overload and inaccurate verdicts).

**Sort the `needs_review` list by `updatedAt` descending** (most recent first). Spawn one sub-agent per PR with this prompt template, passing the PR number. Each sub-agent should:

1. **Read the summary:** `artifacts/pr-review/summaries/{number}.md` — gives you the blocker table and comment counts at a glance.
2. **Read review meta:** `artifacts/pr-review/reviews/{number}/meta.json` — check `total_comments`. If 0, verdict is `ready` (no review comments = needs first review, not blocked).
3. **Read comments newest-first:** Start from the highest-numbered file (`05.json`, `04.json`, etc.).
4. **Skip resolved inline comments:** If an inline comment was addressed by a later commit or reply, treat it as resolved. Only flag genuinely unresolved concerns.
5. **Stop early:** Once you've found the latest bot review and have enough context, stop reading older comments.
6. **Record verdict** with these fields:
   - **number**: PR number
   - **verdict**: `ready` (no blockers), `almost` (1 minor issue), `blocked` (real blockers), `stale` (abandoned)
   - **review_summary**: 1-2 sentences — who reviewed, what was raised, whether addressed
   - **action_needed**: What a human should do next
   - **action_owner**: `@author`, `@reviewer`, `@maintainer`, or specific username
   - **blockers_from_comments**: List of genuine blockers (empty if none)

**Key judgment calls:**
- A bot review from weeks ago on a different commit is stale — note but don't block
- `CHANGES_REQUESTED` + author pushed fix + no re-approval = needs reviewer re-review, not a comment blocker
- "nit" or style suggestions with `CHANGES_REQUESTED` = not a real blocker
- No comments at all = `ready` (needs first review, not blocked)
- Resolved inline threads = ignore

**Do not rewrite the analysis script.** If you need to adjust a deterministic check, edit `scripts/analyze-prs.py` directly.

## PR Type Classification

The analysis script classifies each PR into a type based on labels, branch name, title, and diff shape:

| Type | Signals | Priority |
|------|---------|----------|
| `bug-fix` | `bug`/`fix` labels, `fix/`/`bugfix/`/`hotfix/` branch, `fix:` title prefix | Highest |
| `feature` | `feature`/`enhancement` labels, `feat/` branch, `feat:` title prefix | High |
| `refactor` | `refactor`/`cleanup` labels, `refactor/` branch, `refactor:` prefix | Medium |
| `chore` | `chore` label, `chore/` branch, CI/config-only changes | Medium |
| `docs` | `docs` label, `docs/` branch, markdown-only changes | Lower |
| `unknown` | No clear signals — sub-agent should refine based on diff content | Lowest |

The sub-agent can override the script's classification if the diff tells a different story.

## Blocker Checklist

For **every** open PR, evaluate each of these categories. Each is either clear or a blocker/warning.

### 1. CI

- Check `check_runs` (primary) and `statusCheckRollup` (fallback).
- **Clear:** all completed check runs have conclusion `success` or `neutral` (ignore `skipped`).
- **Warn:** check runs still in progress (`status` is `queued` or `in_progress`) — CI hasn't finished yet.
- **Blocker:** any completed check run with `failure`, `timed_out`, `cancelled`, or `action_required`. List the failing check names.

### 2. Merge Conflicts

- Check the `mergeable` field.
- **Clear:** `MERGEABLE`.
- **Warn:** `UNKNOWN` — GitHub hasn't computed mergeability yet. Not a blocker.
- **Blocker:** `CONFLICTING`. Note which files overlap with other open PRs if detectable.

### 3. Review Comments

The script handles one deterministic check automatically:
- **CHANGES_REQUESTED** without a subsequent APPROVED or DISMISSED → `FAIL`

**Inline review comments are NOT blockers.** Most are resolved or addressed by subsequent commits. The script notes them for context but does not count them toward `fail_count`.

Everything else — bot reviews, human discussion, comment arcs — is evaluated sequentially in Phase 3. When marking a PR as FAIL in the report, include a brief explanation of the actual issue so the team can act on it.

### 4. Jira Hygiene

- Scan the PR **title**, **body**, and **branch name** (`headRefName`) for Jira ticket patterns:
  - Primary: `RHOAIENG-\d+`
  - General: `[A-Z]{2,}-\d+` — but **exclude** non-Jira prefixes: `CVE`, `GHSA`, `HTTP`, `API`, `URL`, `PR`, `WIP`
- **Clear:** at least one Jira reference found.
- **Blocker:** no Jira reference detected. This is a hygiene issue — it should not prevent merging on its own but must be flagged.

### 5. Fork PR — No Agent Review

- Check the `is_fork` field in the per-PR analysis.
- **Fork PRs do not receive automated agent reviews** (the Amber review bot only runs on internal branches).
- If `is_fork` is `true`: mark as `warn` with "Fork PR — no automated agent review". This is not a merge blocker, but the report must flag it so a maintainer knows manual review is required.

### 6. Staleness

The analysis script flags PRs older than 30 days and detects potential supersession (newer PRs with similar branches/titles). Use your judgment beyond the script's output — the script provides `days_since_update`, `recommend_close`, and `superseded_by` fields as signals, not final verdicts.

Consider recommending closure for PRs that show multiple signs of abandonment:
- Draft PR + merge conflicts + no activity in 3+ weeks
- Multiple blockers + no updates in 30+ days
- Superseded by a newer PR from the same author
- Very old (60+ days) regardless of other signals

Use the condensed "Recommend Closing" table instead of a full blocker breakdown for these.

## Ranking Logic

Produce a single ranked list of all open PRs, ordered by what needs human attention first:

1. **PR type** — bug fixes before features before refactors before docs/chores. Unknown types sort after features.
2. **Blocker count** — within the same type, PRs with zero blockers first.
3. **Readiness** — PRs that just need a human approval rank above PRs that need author work.
4. **Size (smaller first)** — PRs with fewer changed files and smaller diffs rank higher. Small PRs are faster to review.
5. **Priority labels** — `priority/critical`, `bug`, `hotfix` labels boost rank within their tier.
6. **Dependency chains** — if a PR's branch is based on another PR's branch, the base PR must rank higher. Note these explicitly.
7. **Draft PRs last** — drafts always sort to the bottom regardless of other signals.

## Status Indicators

Use these in the **Status** column of the per-PR blocker table:

| Status | Meaning |
|--------|---------|
| `pass` | No issues detected |
| `FAIL` | Blocker — must be resolved before merge |
| `warn` | Hygiene / informational issue — does not block merge |

## Output Format

Use the template at `templates/review-queue.md`. Populate it from `analysis.json` and sub-agent verdicts.

### Dates

Use absolute dates in `YYYY-MM-DD` format (e.g., `2026-02-27`). Do not use relative dates like "2 days ago" — the report is stored in the milestone description and becomes stale.

### At a Glance

A 2-3 sentence summary at the top of the report. Mention how many PRs are ready for review, call out the top 3-4 by number and type, and flag any notable concerns (e.g., "3 PRs recommended for closure", "6 PRs blocked by merge conflicts").

### Ready for Review (condensed table)

PRs with `fail_count == 0` and `isDraft == false` go in the condensed summary table — one row per PR. List them in review order (bug fixes first, smallest first).

For fork PRs (`is_fork == true`), add "Fork — no agent review" to the Notes column.

The **Action Needed** column: what a human reviewer should do (from sub-agent verdict).

### PRs With Blockers (full tables)

PRs with `fail_count > 0` and `isDraft == false` get the full blocker table. PRs flagged with `recommend_close == true` go in the "Recommend Closing" table instead.

### Fork PRs

Fork PRs are **not** separated into their own section. They appear in the same Ready for Review or PRs With Blockers tables as internal PRs, based on their blocker count.

To signal that a PR is from a fork, add "Fork (`fork_owner`) — no agent review" to the **Notes** column.

### Recommend Closing

PRs flagged by the script (`recommend_close == true`) or that you judge to be abandoned. One-row-per-PR table with: PR link, author, reason, last updated.

## Phase 4: Milestone Management

Manage the **"Review Queue"** milestone. This milestone acts as a living bucket of ready-to-review PRs — no due date, never closed, updated every run. The milestone description stores the report.

**Important: complete milestone sync BEFORE writing the final report** so that `{{MILESTONE_COUNT}}` in the report is accurate.

### Step 1: Find or create the milestone

```bash
# Find existing milestone (check both names for backward compat)
MILESTONE_NUM=$(gh api "repos/{owner}/{repo}/milestones" --jq '.[] | select(.title=="Review Queue" or .title=="Merge Queue") | .number')

# If not found, create it
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api "repos/{owner}/{repo}/milestones" \
    -f title="Review Queue" \
    -f state=open \
    -f description="Auto-managed by Review Queue workflow" \
    --jq '.number')
fi
```

### Step 2: Sync PRs to the milestone

First, get the list of PRs currently in the milestone:

```bash
gh api "repos/{owner}/{repo}/issues?milestone=${MILESTONE_NUM}&state=all&per_page=100" \
  --jq '.[] | {number: .number, state: .state, pull_request: .pull_request.merged_at}'
```

Then sync:

- **Remove** PRs that are merged, closed, or now have blockers:
  ```bash
  gh api -X PATCH "repos/{owner}/{repo}/issues/{number}" -F milestone=null
  ```
- **Add** open PRs with **0 blockers** (all statuses are `pass` or `warn`, no `FAIL`):
  ```bash
  gh api -X PATCH "repos/{owner}/{repo}/issues/{number}" -F milestone=${MILESTONE_NUM}
  ```
- **Never** add draft PRs to the milestone.

**Note:** Use the REST API (`gh api -X PATCH .../issues/{number}`) instead of `gh pr edit --milestone`, which requires `read:org` scope that runners typically lack.

After syncing, count the PRs now in the milestone — this is `{{MILESTONE_COUNT}}` for the report.

### Step 3: Reorder PRs in the milestone to match review order

GitHub supports reordering issues within a milestone via a GraphQL mutation. After syncing, reorder the PRs to match the `review_order` from the analysis.

```bash
# Get milestone node ID
MILESTONE_NODE_ID=$(gh api "repos/{owner}/{repo}/milestones/${MILESTONE_NUM}" --jq '.node_id')

# Get PR node IDs (for each PR in review_order)
PR_NODE_ID=$(gh api "repos/{owner}/{repo}/pulls/{number}" --jq '.node_id')

# Reorder
gh api graphql -f query='
  mutation {
    reprioritizeMilestoneIssue(input: {
      id: "{pr_node_id}",
      milestoneId: "{milestone_node_id}",
      prevId: "{previous_pr_node_id}"
    }) {
      clientMutationId
    }
  }
'
```

For the first PR in the order, omit `prevId`. If the mutation fails, skip silently.

### Step 4: Write the final report

Now that milestone sync is complete and `{{MILESTONE_COUNT}}` is known, write the final report to `artifacts/pr-review/review-queue-{YYYY-MM-DD}.md` using the template.

### Step 5: Update milestone description with the report

```bash
REPORT=$(cat artifacts/pr-review/review-queue-{date}.md)
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
- Always include the `Last updated` timestamp at the top.

## Phase 6: Comment on Blocked PRs (best-effort)

After milestone sync, post a blocker summary comment on each PR that has blockers (`fail_count > 0`) and was **not** added to the Review Queue. **If any auth or API error occurs, skip this phase entirely** — the report and milestone are the primary outputs.

**All comments are identified by a hidden HTML marker:** `<!-- review-queue-bot -->` at the end of the comment body.

### Noise reduction rules

1. **Find existing comment:** Look for one containing `<!-- review-queue-bot -->` (also check for legacy `<!-- pr-overview-bot -->` marker).
2. **Check freshness:** Compare the PR's `updatedAt` with the comment's `created_at`.
   - If the PR was **not updated** since the last comment — **skip**.
   - If the PR **was updated** — **delete** the old comment, then **post** a new one.
3. **No existing comment:** Post a new comment.
4. **On any error:** Skip the PR and move on. Do not retry more than once.

### Comment format

```markdown
### Review Queue — Blockers Found

| Check | Status | Detail |
|-------|--------|--------|
| CI | FAIL | `build` failed |
| Merge conflicts | pass | --- |
| Review comments | FAIL | Changes requested by @reviewer |
| Jira hygiene | pass | RHOAIENG-1234 |
| Staleness | pass | --- |
| Diff overlap risk | pass | --- |

**Action needed:** Author needs to fix CI and address review comments.

> This comment is auto-generated by the Review Queue workflow and will be updated when the PR changes.

<!-- review-queue-bot -->
```

Include the **Action needed** line from the sub-agent verdict when available.

### What to skip

- **Clean PRs** (fail_count == 0) — no comment needed, they're in the queue.
- **Draft PRs** — don't comment on drafts.
- **PRs recommended for closing** — don't comment, they'll be flagged in the report.

## Important Notes

- Do NOT approve or merge any PRs. This workflow is read-only (except for milestone management and blocker comments).
- If the fetch script fails, report the error clearly and stop.
- Always include the PR URL as a link: `[#123](url)`.
- Size format: `X files (+A/-D)` where A = additions, D = deletions.
