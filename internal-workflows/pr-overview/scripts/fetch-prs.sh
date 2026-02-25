#!/usr/bin/env bash
#
# fetch-prs.sh — Fetch all open PR data from a GitHub repo into structured JSON files.
#
# Usage:
#   ./scripts/fetch-prs.sh --repo owner/repo [--output-dir artifacts/pr-review]
#
# Requirements:
#   - gh CLI installed and authenticated
#   - jq installed
#

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
REPO=""
OUTPUT_DIR="artifacts/pr-review"

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --repo owner/repo [--output-dir artifacts/pr-review]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$REPO" ]]; then
    echo "Error: --repo is required (e.g., --repo ambient-code/platform)" >&2
    exit 1
fi

# ── Preflight checks ─────────────────────────────────────────────────────────
if ! command -v gh &>/dev/null; then
    echo "Error: gh CLI is not installed. Install it from https://cli.github.com/" >&2
    exit 1
fi

if ! gh auth status &>/dev/null; then
    echo "Error: gh CLI is not authenticated. Run 'gh auth login' first." >&2
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "Error: jq is not installed." >&2
    exit 1
fi

OWNER="${REPO%%/*}"
REPO_NAME="${REPO##*/}"

# ── Setup output dirs ────────────────────────────────────────────────────────
mkdir -p "${OUTPUT_DIR}/prs"

echo "Fetching open PRs for ${REPO}..."

# ── Phase 1: Fetch PR index ──────────────────────────────────────────────────
INDEX_FIELDS="number,title,author,createdAt,updatedAt,labels,isDraft,baseRefName,headRefName,url,state,additions,deletions,changedFiles,mergeable,body"

gh pr list \
    --repo "$REPO" \
    --state open \
    --limit 200 \
    --json "$INDEX_FIELDS" \
    | jq '.' > "${OUTPUT_DIR}/index.json"

PR_COUNT=$(jq 'length' "${OUTPUT_DIR}/index.json")
echo "Found ${PR_COUNT} open PRs."

if [[ "$PR_COUNT" -eq 0 ]]; then
    echo "No open PRs found. Done."
    exit 0
fi

# ── Phase 2: Fetch per-PR detail ─────────────────────────────────────────────
PR_NUMBERS=$(jq -r '.[].number' "${OUTPUT_DIR}/index.json")

for PR_NUM in $PR_NUMBERS; do
    echo "  Fetching PR #${PR_NUM}..."

    # Get detailed PR data
    PR_DETAIL=$(gh pr view "$PR_NUM" \
        --repo "$REPO" \
        --json "number,title,author,createdAt,updatedAt,labels,isDraft,baseRefName,headRefName,url,state,additions,deletions,changedFiles,mergeable,body,reviewDecision,statusCheckRollup,comments,reviewRequests,assignees,milestone,files" \
        2>/dev/null || echo '{}')

    # Get reviews via API
    REVIEWS=$(gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/reviews" \
        --paginate 2>/dev/null || echo '[]')

    # Get review comments (threads)
    REVIEW_COMMENTS=$(gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/comments" \
        --paginate 2>/dev/null || echo '[]')

    # Get latest commit SHA for check runs
    HEAD_SHA=$(echo "$PR_DETAIL" | jq -r '.statusCheckRollup // [] | if length > 0 then .[0].commit.oid // empty else empty end' 2>/dev/null || true)

    CHECK_RUNS='[]'
    if [[ -n "$HEAD_SHA" ]]; then
        CHECK_RUNS=$(gh api "repos/${OWNER}/${REPO_NAME}/commits/${HEAD_SHA}/check-runs" \
            --paginate 2>/dev/null | jq '.check_runs // []' 2>/dev/null || echo '[]')
    fi

    # Combine into a single JSON file (diff_files added in Phase 3 for mergeable PRs)
    jq -n \
        --argjson pr "$PR_DETAIL" \
        --argjson reviews "$REVIEWS" \
        --argjson review_comments "$REVIEW_COMMENTS" \
        --argjson check_runs "$CHECK_RUNS" \
        '{
            pr: $pr,
            reviews: $reviews,
            review_comments: $review_comments,
            check_runs: $check_runs,
            diff_files: []
        }' > "${OUTPUT_DIR}/prs/${PR_NUM}.json"

    sleep 0.3
done

# ── Phase 3: Fetch diff hunks for mergeable PRs ─────────────────────────────
# Only spend API calls on PRs that are actually mergeable (not CONFLICTING,
# not drafts). The diff_files array contains per-file patch data with hunk
# line ranges so the agent can detect real line-level overlaps between PRs
# when optimising merge order.

MERGEABLE_PRS=$(jq -r '.[] | select(.mergeable == "MERGEABLE" and .isDraft == false) | .number' "${OUTPUT_DIR}/index.json")
MERGEABLE_COUNT=$(echo "$MERGEABLE_PRS" | grep -c '[0-9]' || true)

if [[ "$MERGEABLE_COUNT" -gt 0 ]]; then
    echo ""
    echo "Fetching diff hunks for ${MERGEABLE_COUNT} mergeable PRs..."

    for PR_NUM in $MERGEABLE_PRS; do
        echo "  Fetching diffs for PR #${PR_NUM}..."

        DIFF_FILES=$(gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/files" \
            --paginate 2>/dev/null \
            | jq '[.[] | {
                filename: .filename,
                status: .status,
                additions: .additions,
                deletions: .deletions,
                patch: .patch
            }]' 2>/dev/null || echo '[]')

        # Merge diff_files into the existing PR JSON
        jq --argjson diff_files "$DIFF_FILES" '.diff_files = $diff_files' \
            "${OUTPUT_DIR}/prs/${PR_NUM}.json" > "${OUTPUT_DIR}/prs/${PR_NUM}.json.tmp" \
            && mv "${OUTPUT_DIR}/prs/${PR_NUM}.json.tmp" "${OUTPUT_DIR}/prs/${PR_NUM}.json"

        sleep 0.3
    done
else
    echo ""
    echo "No mergeable (non-draft) PRs found — skipping diff fetch."
fi

echo ""
echo "Done. Output written to ${OUTPUT_DIR}/"
echo "  - index.json          (${PR_COUNT} PR summaries)"
echo "  - prs/*.json          (detailed data per PR)"
echo "  - diff hunks fetched  (${MERGEABLE_COUNT} mergeable PRs)"
