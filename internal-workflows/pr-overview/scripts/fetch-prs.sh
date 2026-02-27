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
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

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
# Note: reviewRequests is excluded — it requires read:org scope which runners
# typically lack.
PR_NUMBERS=$(jq -r '.[].number' "${OUTPUT_DIR}/index.json")
DETAIL_FIELDS="number,title,author,createdAt,updatedAt,labels,isDraft,baseRefName,headRefName,url,state,additions,deletions,changedFiles,mergeable,body,reviewDecision,statusCheckRollup,comments,assignees,milestone,files"

for PR_NUM in $PR_NUMBERS; do
    echo "  Fetching PR #${PR_NUM}..."

    # Write each API response to a temp file to avoid "argument list too long"
    # errors when PRs have large bodies or many comments.

    gh pr view "$PR_NUM" \
        --repo "$REPO" \
        --json "$DETAIL_FIELDS" \
        2>/dev/null > "${TMPDIR}/pr.json" || echo '{}' > "${TMPDIR}/pr.json"

    gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/reviews" \
        --paginate 2>/dev/null > "${TMPDIR}/reviews.json" || echo '[]' > "${TMPDIR}/reviews.json"

    gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/comments" \
        --paginate 2>/dev/null > "${TMPDIR}/review_comments.json" || echo '[]' > "${TMPDIR}/review_comments.json"

    # Get latest commit SHA for check runs
    HEAD_SHA=$(jq -r '.statusCheckRollup // [] | if length > 0 then .[0].commit.oid // empty else empty end' "${TMPDIR}/pr.json" 2>/dev/null || true)

    echo '[]' > "${TMPDIR}/check_runs.json"
    if [[ -n "$HEAD_SHA" ]]; then
        gh api "repos/${OWNER}/${REPO_NAME}/commits/${HEAD_SHA}/check-runs" \
            --paginate 2>/dev/null \
            | jq '.check_runs // []' > "${TMPDIR}/check_runs.json" 2>/dev/null || echo '[]' > "${TMPDIR}/check_runs.json"
    fi

    # Combine via file-based slurp (avoids --argjson size limits)
    jq -n \
        --slurpfile pr "${TMPDIR}/pr.json" \
        --slurpfile reviews "${TMPDIR}/reviews.json" \
        --slurpfile review_comments "${TMPDIR}/review_comments.json" \
        --slurpfile check_runs "${TMPDIR}/check_runs.json" \
        '{
            pr: $pr[0],
            reviews: $reviews[0],
            review_comments: $review_comments[0],
            check_runs: $check_runs[0],
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

        gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/files" \
            --paginate 2>/dev/null \
            | jq '[.[] | {
                filename: .filename,
                status: .status,
                additions: .additions,
                deletions: .deletions,
                patch: .patch
            }]' > "${TMPDIR}/diff_files.json" 2>/dev/null || echo '[]' > "${TMPDIR}/diff_files.json"

        # Merge diff_files into the existing PR JSON via file-based slurp
        jq --slurpfile diff_files "${TMPDIR}/diff_files.json" '.diff_files = $diff_files[0]' \
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
