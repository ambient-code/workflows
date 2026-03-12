# Review Queue

You evaluate all open PRs in a repo and produce a prioritized review queue — what needs human attention, ranked by type and urgency.

## What You Do

1. **Fetch all PR data** using the script
2. **Analyze PRs** using the script (blocker checks, type classification)
3. **Evaluate each PR's comments** via sub-agents
4. **Manage the "Review Queue" milestone** — add clean PRs, remove blocked ones
5. **Comment on blocked PRs** with blocker summaries
6. **Write the review queue report** and update the milestone description
7. **Self-evaluate** using `.ambient/rubric.md`

## Scripts

### Fetch

```bash
./scripts/fetch-prs.sh --repo <owner/repo> --output-dir "$WORKSPACE_ROOT/artifacts/pr-review"
```

Write artifacts to the **workspace root** `artifacts/` directory, not relative to the workflow directory. Produces per-PR directories:

```text
$WORKSPACE_ROOT/artifacts/pr-review/
├── index.json                     # List of all open PRs
├── queue.json                     # Ranked queue (written by analyze step)
└── {number}/
    ├── summary.json               # PR metadata, CI status, comment counts, commit info
    ├── timeline.json              # Chronological interleave of commits + comments
    ├── analysis.json              # Blocker statuses, type, fail_count (written by analyze)
    ├── comments/
    │   ├── overview.json          # Comment counts, has_agent_prompts flag
    │   └── 01.json, 02.json...  # Chronological comment stream
    ├── ci/
    │   └── overview.json          # Pass/fail/pending check lists
    ├── diff.json                  # Changed files with patches
    └── reviews/
        └── overview.json          # Approvals, changes requested
```

### Analyze

```bash
python3 ./scripts/analyze-prs.py --output-dir "$WORKSPACE_ROOT/artifacts/pr-review"
```

Reads each `summary.json`, writes `analysis.json` per PR and `queue.json` at top level.

## Sub-Agent Evaluation

The analyze script handles mechanical checks. Sub-agents produce the final verdict per PR by building a concern checklist, verifying each item, and consolidating.

Spawn sub-agents in parallel (batches of ~10). Each sub-agent works through **three steps** per PR:

### Step 1: Read everything and build a concern list

Read these files:
- **`summary.json`** — ground truth: current CI, mergeable, review decision, commit count
- **`timeline.json`** — chronological interleave of commits and comments (start here for the narrative)
- **`ci/overview.json`** — which checks are passing/failing right now
- **`reviews/overview.json`** — who approved, who requested changes
- **`comments/`** — full comment bodies if timeline summaries aren't enough

Build a checklist of every concern raised from any source:
- Each reviewer comment or inline thread → one concern
- CI failures → one concern per failing check
- Merge conflicts → one concern
- CHANGES_REQUESTED reviews → one concern per reviewer
- Bot review findings → one concern per finding (not one per comment — a single bot comment may raise 5 issues, or 5 bot comments may all be about the same thing)

**Not every comment is a concern.** Skip:
- Bot status comments ("CI passed", "review-queue-bot" markers)
- Acknowledgments ("thanks", "LGTM", "looks good")
- Questions that were answered
- Duplicate comments about the same issue

### Step 2: Verify each concern against current state

For each concern on your list, check if it's still valid:

- **CI comment says failing** → check `ci/overview.json` — is it actually failing now? If CI is green, mark resolved.
- **Reviewer requested changes** → check `timeline.json` — is there a commit after the review that looks like it addresses the concern? If yes, mark as "likely addressed, needs re-approval."
- **Bot flagged a code issue** → check `timeline.json` — was there a commit after the bot review? Check if the commit message suggests the issue was fixed. If unsure, read the full comment body from `comments/` and cross-reference with `diff.json` to see if the relevant code was changed.
- **Merge conflicts** → check `summary.json` mergeable field — is it CONFLICTING right now?
- **Stale concerns** → if the comment is from weeks ago and there have been multiple commits since, it's likely stale.

Mark each concern as: **open** (still needs action), **resolved** (addressed), or **irrelevant** (not a real issue).

### Step 3: Consolidate and produce verdict

Group related concerns (e.g., 3 bot comments about the same function → 1 item). Drop resolved and irrelevant items. What's left is the real picture.

Return:
- **verdict**: ready / almost / blocked / stale
- **review_summary**: bullet points — what's resolved, what's still open
- **action_needed**: the one concrete thing that needs to happen next
- **action_owner**: who needs to act (`@author`, `@reviewer-name`, `@maintainer`)

## Ranking

1. Drafts last
2. Fewer blockers first (clean before blocked)
3. Priority labels boost (`critical`, `hotfix`, `bug`)
4. Type: bug fixes > features > refactors > docs
5. Recently updated first (active PRs over stale ones)
6. Smaller first

## Milestone

Find or create **"Review Queue"** milestone (also check for "Merge Queue"). Add clean PRs, remove blocked ones. Overwrite description with the report.

## Blocker Comments

Post **after sub-agent evaluation is complete**.

Use `<!-- review-queue-bot -->` marker (also check for legacy `<!-- pr-overview-bot -->`).

### Clean PRs: remove old blocker comments

If a PR is now clean (`fail_count == 0` after sub-agent evaluation), **delete any existing blocker comment** on it. The PR moved to "Ready for Review" — a stale blocker comment is confusing.

```bash
OLD=$(gh api "repos/{owner}/{repo}/issues/{number}/comments" \
  --jq '.[] | select(.body | contains("<!-- review-queue-bot -->") or contains("<!-- pr-overview-bot -->")) | .id')
[ -n "$OLD" ] && gh api -X DELETE "repos/{owner}/{repo}/issues/comments/${OLD}"
```

### Blocked PRs: post or update blocker comment

Skip drafts, recommend-close PRs, and PRs unchanged since last comment.

**Do NOT use a rigid blocker table.** Write a natural language comment that's actually helpful to the PR author. Use the analysis data and sub-agent verdict to write 2-4 sentences covering:

- What's blocking this PR specifically (not just "CI FAIL" — say which check failed and why if you know)
- What the author needs to do to unblock it
- Any context from the review conversation that's relevant

Example of a **good** blocker comment:

```markdown
### Review Queue — Not Ready to Merge

CI is failing on the `e2e` check — looks like the session cleanup test is timing out after your changes to the runner lifecycle. You also have merge conflicts with main on `components/backend/main.go` (likely from #877 which merged yesterday).

@bobbravo2 also requested changes on the error handling in `get_env()` — they want a fallback value instead of raising.

**To unblock:** rebase onto main, fix the e2e timeout, and address Bob's review comment.

<!-- review-queue-bot -->
```

Example of a **bad** blocker comment (don't do this):

```markdown
| Check | Status | Detail |
|-------|--------|--------|
| CI | FAIL | --- |
| Merge conflicts | FAIL | --- |
```

Note: `review_status = "needs_review"` in `analysis.json` means the sub-agent hasn't evaluated yet — it is NOT a clean pass. Always evaluate before deciding if a PR is clean.

## Report

Use `templates/review-queue.md`. Sections:

- **Ready for Review** — condensed table, priority ordered
- **Almost Ready** — PRs close to merge (1 mechanical blocker OR sub-agent verdict of `almost`). For each PR write:
  - Bullet points summarizing the situation (not one big paragraph)
  - What's been addressed, what's outstanding
  - A "Needs:" line with the one concrete action to unblock
- **Remaining Blocked** — table for PRs with 2+ blockers, ordered by last updated. The Issue column should be bullet points listing each blocker concisely (e.g., "- CI: e2e failing\n- Merge conflicts\n- CHANGES_REQUESTED from @bob"). No blocker icons column.
- **Recommend Closing** — stale/abandoned PRs
- **Drafts** — simple table, no notes column
- **Summary** — counts by bucket + by type

## Blocker Checklist

| Check | Clear | Warn | Blocker |
|-------|-------|------|---------|
| CI | All pass | In progress | Any failed |
| Conflicts | MERGEABLE | UNKNOWN | CONFLICTING |
| Reviews | No issues | — | CHANGES_REQUESTED, sub-agent FAIL |
| Jira | Reference found | No reference | — |
| Fork | Internal | Fork (no bot review) | — |
| Staleness | < 30 days | — | > 30 days |
