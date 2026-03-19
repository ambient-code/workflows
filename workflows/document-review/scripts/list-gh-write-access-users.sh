#!/usr/bin/env bash
# Usage: ./list-write-users.sh OWNER/REPO
set -euo pipefail

repo="${1:?Usage: $0 OWNER/REPO}"

# Hardcoded whitelist of additional usernames
whitelist=(
    "coderabbitai[bot]"
)

{
    if collab=$(gh api --paginate "repos/${repo}/collaborators?permission=push" -q '.[].login' 2>/dev/null); then
        echo "$collab"
    fi
    printf '%s\n' "${whitelist[@]}"
} | sort -u
