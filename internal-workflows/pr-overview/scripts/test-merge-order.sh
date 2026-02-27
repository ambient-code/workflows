#!/usr/bin/env bash
#
# test-merge-order.sh — Test merge order by locally merging clean PRs in sequence.
#
# Creates a temporary local branch, merges each PR in the given order,
# and stops on the first conflict. Reports which PRs merged cleanly
# and which conflicted. NEVER pushes to any remote.
#
# Usage:
#   ./scripts/test-merge-order.sh --repo owner/repo --repo-dir /path/to/clone --prs "616 715 685 ..."
#
# Output: JSON results to stdout
#
# Requirements:
#   - gh CLI installed and authenticated
#   - git installed
#   - The repo must be cloned at --repo-dir
#

set -euo pipefail

REPO=""
REPO_DIR=""
PR_LIST=""
BRANCH_NAME="tmp/merge-queue-test"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --repo-dir)
            REPO_DIR="$2"
            shift 2
            ;;
        --prs)
            PR_LIST="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --repo owner/repo --repo-dir /path/to/clone --prs '616 715 685 ...'"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$REPO" || -z "$REPO_DIR" || -z "$PR_LIST" ]]; then
    echo "Error: --repo, --repo-dir, and --prs are all required" >&2
    exit 1
fi

cd "$REPO_DIR"

OWNER="${REPO%%/*}"
REPO_NAME="${REPO##*/}"

# ── Safety: ensure we never push ─────────────────────────────────────────────
# Override push URL to a non-existent path so even accidental pushes fail
ORIGINAL_PUSH_URL=$(git remote get-url --push origin 2>/dev/null || true)
git remote set-url --push origin /dev/null/no-push-allowed

cleanup() {
    # Restore push URL and clean up branch
    git merge --abort 2>/dev/null || true
    git checkout main 2>/dev/null || git checkout - 2>/dev/null || true
    git branch -D "$BRANCH_NAME" 2>/dev/null || true
    if [[ -n "$ORIGINAL_PUSH_URL" ]]; then
        git remote set-url --push origin "$ORIGINAL_PUSH_URL" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# ── Stash any local changes ──────────────────────────────────────────────────
STASHED=false
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    git stash push -m "test-merge-order: stashing before merge test" -q
    STASHED=true
fi

# ── Fetch all PR refs ────────────────────────────────────────────────────────
# This fetches every PR head ref in one call, handling forks automatically.
echo "Fetching all PR refs..." >&2
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*' --quiet 2>/dev/null || true

# ── Create tmp branch from main ──────────────────────────────────────────────
git checkout main --quiet 2>/dev/null
git checkout -b "$BRANCH_NAME" --quiet 2>/dev/null

echo "Starting merge test on branch $BRANCH_NAME..." >&2

# ── Merge each PR in order ───────────────────────────────────────────────────
RESULTS="["
MERGED_COUNT=0
FIRST=true

for PR_NUM in $PR_LIST; do
    PR_REF="origin/pr/${PR_NUM}"

    # Check if the ref exists
    if ! git rev-parse --verify "$PR_REF" &>/dev/null; then
        echo "  PR #${PR_NUM}: ref not found, skipping" >&2
        if [[ "$FIRST" == "true" ]]; then FIRST=false; else RESULTS+=","; fi
        RESULTS+="{\"number\":${PR_NUM},\"result\":\"skipped\",\"detail\":\"PR ref not found\"}"
        continue
    fi

    # Attempt the merge
    echo "  Merging PR #${PR_NUM}..." >&2
    if git merge --no-edit --no-ff "$PR_REF" -m "test-merge: PR #${PR_NUM}" &>/dev/null; then
        echo "  PR #${PR_NUM}: merged" >&2
        if [[ "$FIRST" == "true" ]]; then FIRST=false; else RESULTS+=","; fi
        RESULTS+="{\"number\":${PR_NUM},\"result\":\"merged\"}"
        MERGED_COUNT=$((MERGED_COUNT + 1))
    else
        # Conflict — find which files
        CONFLICT_FILES=$(git diff --name-only --diff-filter=U 2>/dev/null | head -5 | tr '\n' ', ' | sed 's/,$//')
        echo "  PR #${PR_NUM}: CONFLICT on ${CONFLICT_FILES}" >&2
        git merge --abort 2>/dev/null || true

        if [[ "$FIRST" == "true" ]]; then FIRST=false; else RESULTS+=","; fi
        RESULTS+="{\"number\":${PR_NUM},\"result\":\"conflict\",\"files\":\"${CONFLICT_FILES}\"}"

        # Mark remaining PRs as not attempted
        REMAINING=false
        for REMAINING_PR in $PR_LIST; do
            if [[ "$REMAINING" == "true" ]]; then
                RESULTS+=",{\"number\":${REMAINING_PR},\"result\":\"not_attempted\",\"detail\":\"Stopped after conflict on #${PR_NUM}\"}"
            fi
            if [[ "$REMAINING_PR" == "$PR_NUM" ]]; then
                REMAINING=true
            fi
        done

        break
    fi
done

RESULTS+="]"

echo "" >&2
echo "Merge test complete: ${MERGED_COUNT} merged cleanly" >&2

# ── Output JSON ──────────────────────────────────────────────────────────────
echo "$RESULTS"

# ── Restore stash ────────────────────────────────────────────────────────────
# (cleanup trap handles branch deletion and push URL restore)
if [[ "$STASHED" == "true" ]]; then
    git checkout main --quiet 2>/dev/null
    git stash pop --quiet 2>/dev/null || true
fi
