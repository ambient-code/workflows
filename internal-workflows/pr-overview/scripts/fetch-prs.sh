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
# Progress goes to stderr. Final summary goes to stdout.
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

echo "Fetching open PRs for ${REPO}..." >&2

# ── Phase 1: Fetch PR index ──────────────────────────────────────────────────
INDEX_FIELDS="number,title,author,createdAt,updatedAt,labels,isDraft,baseRefName,headRefName,url,state,additions,deletions,changedFiles,mergeable,body"

gh pr list \
    --repo "$REPO" \
    --state open \
    --limit 200 \
    --json "$INDEX_FIELDS" \
    | jq '.' > "${OUTPUT_DIR}/index.json"

PR_COUNT=$(jq 'length' "${OUTPUT_DIR}/index.json")
echo "Found ${PR_COUNT} open PRs." >&2

if [[ "$PR_COUNT" -eq 0 ]]; then
    echo "No open PRs found."
    exit 0
fi

# ── Phase 2: Fetch per-PR detail ─────────────────────────────────────────────
# Note: reviewRequests is excluded — it requires read:org scope which runners
# typically lack.
PR_NUMBERS=$(jq -r '.[].number' "${OUTPUT_DIR}/index.json")
DETAIL_FIELDS="number,title,author,createdAt,updatedAt,labels,isDraft,baseRefName,headRefName,url,state,additions,deletions,changedFiles,mergeable,body,reviewDecision,statusCheckRollup,comments,assignees,milestone,files"
FETCHED=0

for PR_NUM in $PR_NUMBERS; do
    FETCHED=$((FETCHED + 1))
    echo -ne "  Fetching PR details... ${FETCHED}/${PR_COUNT}\r" >&2

    gh pr view "$PR_NUM" \
        --repo "$REPO" \
        --json "$DETAIL_FIELDS" \
        2>/dev/null > "${TMPDIR}/pr.json" || echo '{}' > "${TMPDIR}/pr.json"

    gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/reviews" \
        --paginate 2>/dev/null > "${TMPDIR}/reviews.json" || echo '[]' > "${TMPDIR}/reviews.json"

    gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/comments" \
        --paginate 2>/dev/null > "${TMPDIR}/review_comments.json" || echo '[]' > "${TMPDIR}/review_comments.json"

    HEAD_SHA=$(jq -r '.statusCheckRollup // [] | if length > 0 then .[0].commit.oid // empty else empty end' "${TMPDIR}/pr.json" 2>/dev/null || true)

    echo '[]' > "${TMPDIR}/check_runs.json"
    if [[ -n "$HEAD_SHA" ]]; then
        gh api "repos/${OWNER}/${REPO_NAME}/commits/${HEAD_SHA}/check-runs" \
            --paginate 2>/dev/null \
            | jq '.check_runs // []' > "${TMPDIR}/check_runs.json" 2>/dev/null || echo '[]' > "${TMPDIR}/check_runs.json"
    fi

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
echo "" >&2

# ── Phase 3: Fetch diff hunks for mergeable PRs ─────────────────────────────
MERGEABLE_PRS=$(jq -r '.[] | select(.mergeable == "MERGEABLE" and .isDraft == false) | .number' "${OUTPUT_DIR}/index.json")
MERGEABLE_COUNT=$(echo "$MERGEABLE_PRS" | grep -c '[0-9]' || true)

if [[ "$MERGEABLE_COUNT" -gt 0 ]]; then
    DIFF_FETCHED=0
    echo "Fetching diff hunks for ${MERGEABLE_COUNT} mergeable PRs..." >&2

    for PR_NUM in $MERGEABLE_PRS; do
        DIFF_FETCHED=$((DIFF_FETCHED + 1))
        echo -ne "  Fetching diffs... ${DIFF_FETCHED}/${MERGEABLE_COUNT}\r" >&2

        gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/files" \
            --paginate 2>/dev/null \
            | jq '[.[] | {
                filename: .filename,
                status: .status,
                additions: .additions,
                deletions: .deletions,
                patch: .patch
            }]' > "${TMPDIR}/diff_files.json" 2>/dev/null || echo '[]' > "${TMPDIR}/diff_files.json"

        jq --slurpfile diff_files "${TMPDIR}/diff_files.json" '.diff_files = $diff_files[0]' \
            "${OUTPUT_DIR}/prs/${PR_NUM}.json" > "${OUTPUT_DIR}/prs/${PR_NUM}.json.tmp" \
            && mv "${OUTPUT_DIR}/prs/${PR_NUM}.json.tmp" "${OUTPUT_DIR}/prs/${PR_NUM}.json"

        sleep 0.3
    done
    echo "" >&2
fi

# ── Phase 4: Sanitize Unicode ────────────────────────────────────────────────
SANITIZED=0
if command -v python3 &>/dev/null; then
    SANITIZED=$(python3 -c "
import os, sys
output_dir = sys.argv[1]
count = 0
for root, _, files in os.walk(output_dir):
    for fname in files:
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', errors='surrogateescape') as f:
            raw = f.read()
        clean = raw.encode('utf-8', errors='replace').decode('utf-8')
        if clean != raw:
            with open(fpath, 'w') as f:
                f.write(clean)
            count += 1
print(count)
" "${OUTPUT_DIR}")
fi

# ── Final summary (stdout — this is what the agent sees) ─────────────────────
echo "Fetch complete: ${PR_COUNT} PRs from ${REPO}"
echo "  PR details: ${PR_COUNT} fetched"
echo "  Diff hunks: ${MERGEABLE_COUNT} mergeable PRs"
echo "  Unicode sanitized: ${SANITIZED} files"
echo "  Output: ${OUTPUT_DIR}/"
