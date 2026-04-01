# /guidance.generate - Generate PR Guidance Files

## Purpose
Analyze a GitHub repository's fix PR history to generate compact guidance files
for the CVE Fixer (`.cve-fix/examples.md`) and Bugfix (`.bugfix/guidance.md`)
workflows, then open a PR in that repo adding those files.

## Execution Style

Be concise. Brief status per phase, full summary at end.

Example:
```
Fetching PRs from org/repo... 147 total
  CVE bucket: 38 PRs (28 merged, 10 closed)
  Bugfix bucket: 61 PRs (54 merged, 7 closed)

Fetching per-PR details... Done
Synthesizing patterns...
  CVE:    14 rules extracted (threshold: 3 PRs, or 1 if limited data)
  Bugfix: 11 rules extracted

Writing guidance files... Done
Creating PR in org/repo... https://github.com/org/repo/pull/88

Artifacts: artifacts/guidance/org-repo/
```

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated: `gh auth status`
- `jq` installed
- Write access to the target repository (for PR creation)

## Arguments

```
/guidance.generate <repo-url> [<repo-url2> ...] [--cve-only] [--bugfix-only] [--limit N]
/guidance.generate <repo-url>[,<repo-url2>,...] [--cve-only] [--bugfix-only] [--limit N]
/guidance.generate <repo-url> [<repo-url2> ...] --pr <url-or-number>[,<url-or-number>...]
```

- `repo-url`: One or more repos — space-separated or comma-separated (or both).
  Accepts full GitHub URLs (`https://github.com/org/repo`) or `org/repo` slugs.
  Each repo is processed independently and gets its own PR.
- `--cve-only`: Skip bugfix analysis for all repos
- `--bugfix-only`: Skip CVE analysis for all repos
- `--limit N`: Max PRs to fetch per bucket per repo (default: 100, min: 20)
- `--pr <refs>`: PR URLs or numbers — space-separated, comma-separated, or mixed.
  Full URLs (`https://github.com/org/repo/pull/123`) are applied only to their
  matching repo. Plain numbers (`123`) are applied to all repos.

## Process

### 1. Parse Arguments and Validate

Parse all repo references (space-separated, comma-separated, or mixed) and
`--pr` into structured data. Validate `gh` auth once before the loop.

```bash
# Validate gh auth once
gh auth status || { echo "ERROR: gh not authenticated. Run 'gh auth login'"; exit 1; }

# Normalize repo args: replace commas with spaces, strip GitHub URL prefix,
# deduplicate, and collect into REPOS array
normalize_repo() {
  local REF="$1"
  if [[ "$REF" =~ github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$REF" =~ ^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$ ]]; then
    echo "$REF"
  else
    echo "WARNING: Cannot parse repo '$REF' — skipping" >&2
    echo ""
  fi
}

REPOS=()
for RAW in $(echo "$REPO_ARGS" | tr ',' ' '); do
  NORMALIZED=$(normalize_repo "$RAW")
  [ -n "$NORMALIZED" ] && REPOS+=("$NORMALIZED")
done

# Deduplicate
REPOS=($(printf '%s\n' "${REPOS[@]}" | awk '!seen[$0]++'))

if [ ${#REPOS[@]} -eq 0 ]; then
  echo "ERROR: No valid repository references provided."
  echo "Usage: /guidance.generate org/repo1 org/repo2"
  exit 1
fi

echo "Repos to process (${#REPOS[@]}):"
for R in "${REPOS[@]}"; do echo "  - $R"; done

# Parse --pr: full URLs map to their repo; plain numbers apply to all repos
declare -A REPO_SPECIFIC_PRS  # keyed by "org/repo", value = space-separated PR numbers
GLOBAL_PR_NUMBERS=""           # plain numbers — applied to every repo

if [ -n "$PR_REFS" ]; then
  IFS=',' read -ra PR_LIST <<< "$(echo "$PR_REFS" | tr ' ' ',')"
  for PR_REF in "${PR_LIST[@]}"; do
    PR_REF=$(echo "$PR_REF" | tr -d ' ')
    if [[ "$PR_REF" =~ github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)/pull/([0-9]+) ]]; then
      PR_REPO="${BASH_REMATCH[1]}"
      PR_NUM="${BASH_REMATCH[2]}"
      REPO_SPECIFIC_PRS["$PR_REPO"]="${REPO_SPECIFIC_PRS[$PR_REPO]:-} $PR_NUM"
    elif [[ "$PR_REF" =~ ^[0-9]+$ ]]; then
      GLOBAL_PR_NUMBERS="$GLOBAL_PR_NUMBERS $PR_REF"
    else
      echo "WARNING: Could not parse PR reference '$PR_REF' — skipping"
    fi
  done
  GLOBAL_PR_NUMBERS=$(echo "$GLOBAL_PR_NUMBERS" | tr -s ' ' | sed 's/^ //')
fi

# Accumulators for the final summary
PR_RESULTS=()   # "org/repo -> <PR URL>"
FAILED_REPOS=() # "org/repo -> <reason>"
```

---
> **Steps 2–8 repeat for each repo in `${REPOS[@]}`.**

```bash
for REPO in "${REPOS[@]}"; do
  echo ""
  echo "=== $REPO ==="

  # Validate this repo is accessible; skip on failure rather than aborting all
  if ! gh repo view "$REPO" --json name > /dev/null 2>&1; then
    echo "  ERROR: Cannot access $REPO — skipping"
    FAILED_REPOS+=("$REPO -> cannot access repository")
    continue
  fi

  REPO_SLUG=$(echo "$REPO" | tr '/' '-')

  # Combine repo-specific --pr numbers with global plain numbers for this repo
  SPECIFIC_PR_NUMBERS="${REPO_SPECIFIC_PRS[$REPO]:-} $GLOBAL_PR_NUMBERS"
  SPECIFIC_PR_NUMBERS=$(echo "$SPECIFIC_PR_NUMBERS" | tr -s ' ' | sed 's/^ //')
  [ -n "$SPECIFIC_PR_NUMBERS" ] && echo "  Manual PR mode: PR(s) $SPECIFIC_PR_NUMBERS"

  mkdir -p "artifacts/guidance/$REPO_SLUG/raw"
  mkdir -p "artifacts/guidance/$REPO_SLUG/analysis"
  mkdir -p "artifacts/guidance/$REPO_SLUG/output"
  mkdir -p "/tmp/guidance-gen/$REPO_SLUG"
```

### 2. Fetch PR Metadata (Pass 1 — lightweight)

**If `--pr` was specified**, skip bulk fetch and build the metadata list directly
from the given PR numbers:

```bash
LIMIT="${LIMIT:-100}"

if [ -n "$SPECIFIC_PR_NUMBERS" ]; then
  # Manual mode: fetch metadata only for the specified PRs
  echo "[]" > "/tmp/guidance-gen/$REPO_SLUG/all-prs.json"
  for NUMBER in $SPECIFIC_PR_NUMBERS; do
    PR_META=$(gh pr view "$NUMBER" --repo "$REPO" \
      --json number,title,state,mergedAt,closedAt,labels,headRefName,latestReviews \
      2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$PR_META" ]; then
      echo "WARNING: Could not fetch PR #$NUMBER — skipping"
      continue
    fi
    jq --argjson meta "$PR_META" '. + [$meta]' \
      "/tmp/guidance-gen/$REPO_SLUG/all-prs.json" \
      > "/tmp/guidance-gen/$REPO_SLUG/all-prs.json.tmp" \
      && mv "/tmp/guidance-gen/$REPO_SLUG/all-prs.json.tmp" \
            "/tmp/guidance-gen/$REPO_SLUG/all-prs.json"
  done
  TOTAL=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/all-prs.json")
  echo "Loaded $TOTAL specified PR(s) from $REPO"
else
  # Auto mode: bulk fetch all recent PRs
  gh pr list \
    --repo "$REPO" \
    --state all \
    --limit 200 \
    --json number,title,state,mergedAt,closedAt,labels,headRefName,latestReviews \
    > "/tmp/guidance-gen/$REPO_SLUG/all-prs.json"
  TOTAL=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/all-prs.json")
  echo "Fetched $TOTAL PRs from $REPO"
fi
```

### 3. Filter into Buckets

Use jq to split into CVE and bugfix buckets based on title and branch patterns.

In **auto mode**: CVE PRs take priority — a PR cannot be in both buckets.
In **manual mode (`--pr`)**: classify normally, but if a specified PR matches
neither pattern, include it in both buckets and let Claude determine during
synthesis which guidance file it informs. Never silently drop a user-specified PR.

```bash
# Explicit CVE/security signals — pass through unconditionally
CVE_EXPLICIT='CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|^[Ss]ecurity:|^fix\(cve\):|^Fix CVE'
# Dependency/version bump patterns — may contain security patches; require body scan
CVE_DEP_PATTERN='^[Bb]ump |^deps\(|^build\(deps\)'
# Combined: either explicit or dep pattern matches the CVE bucket initially
CVE_PATTERN="${CVE_EXPLICIT}|${CVE_DEP_PATTERN}"
CVE_BRANCH_PATTERN='^fix/cve-|^security/cve-|^dependabot/|^renovate/'
BUGFIX_PATTERN='^fix[:(]|^bugfix|^bug[[:space:]]fix|closes[[:space:]]#[0-9]+|fixes[[:space:]]#[0-9]+'
BUGFIX_BRANCH_PATTERN='^(bugfix|fix|bug)/'
# Keyword that confirms a dep-pattern match is security-relevant
SECURITY_BODY='CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|security|vulnerab|security.advisory'

if [ -n "$SPECIFIC_PR_NUMBERS" ]; then
  # Manual mode: classify each PR, fallback to both buckets if unmatched
  jq '[.[] | select(
    (.title | test("'"$CVE_PATTERN"'"; "i")) or
    (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i"))
  )]' "/tmp/guidance-gen/$REPO_SLUG/all-prs.json" \
    > "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json"

  jq '[.[] | select(
    (
      (.title | test("'"$BUGFIX_PATTERN"'"; "i")) or
      (.headRefName | test("'"$BUGFIX_BRANCH_PATTERN"'"; "i"))
    ) and
    (.title | test("'"$CVE_PATTERN"'"; "i") | not) and
    (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i") | not)
  )]' "/tmp/guidance-gen/$REPO_SLUG/all-prs.json" \
    > "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json"

  # Any PR that matched neither bucket: add to both with a warning
  UNMATCHED=$(jq '[.[] | select(
    ((.title | test("'"$CVE_PATTERN"'"; "i")) or (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i")) | not) and
    ((.title | test("'"$BUGFIX_PATTERN"'"; "i")) or (.headRefName | test("'"$BUGFIX_BRANCH_PATTERN"'"; "i")) | not)
  )]' "/tmp/guidance-gen/$REPO_SLUG/all-prs.json")
  UNMATCHED_COUNT=$(echo "$UNMATCHED" | jq 'length')
  if [ "$UNMATCHED_COUNT" -gt 0 ]; then
    UNMATCHED_NUMS=$(echo "$UNMATCHED" | jq -r '.[].number' | tr '\n' ',' | sed 's/,$//')
    echo "  NOTE: PR(s) #$UNMATCHED_NUMS did not match CVE or bugfix patterns — included in both buckets for Claude to classify"
    jq --argjson extra "$UNMATCHED" '. + $extra' \
      "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json" > "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json.tmp" \
      && mv "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json.tmp" "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json"
    jq --argjson extra "$UNMATCHED" '. + $extra' \
      "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json" > "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json.tmp" \
      && mv "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json.tmp" "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json"
  fi
else
  # Auto mode: strict filtering, CVE takes priority
  jq --argjson limit "$LIMIT" '[
    .[] | select(
      (.title | test("'"$CVE_PATTERN"'"; "i")) or
      (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i"))
    )
  ] | .[:$limit]' \
    "/tmp/guidance-gen/$REPO_SLUG/all-prs.json" \
    > "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json"

  jq --argjson limit "$LIMIT" '[
    .[] | select(
      (
        (.title | test("'"$BUGFIX_PATTERN"'"; "i")) or
        (.headRefName | test("'"$BUGFIX_BRANCH_PATTERN"'"; "i"))
      ) and
      (.title | test("'"$CVE_PATTERN"'"; "i") | not) and
      (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i") | not)
    )
  ] | .[:$limit]' \
    "/tmp/guidance-gen/$REPO_SLUG/all-prs.json" \
    > "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json"
fi

# Body scan: for dep-pattern matches without an explicit CVE/GHSA in the title,
# fetch the PR body and verify it contains a security indicator.
# Explicit CVE/GHSA/Security titles pass through unconditionally.
# Only runs in auto mode — manual --pr mode trusts the user's selection.
if [ -z "$SPECIFIC_PR_NUMBERS" ]; then
  DEP_ONLY_NUMS=$(jq -r '[.[] | select(
    (.title | test("'"$CVE_DEP_PATTERN"'"; "i")) and
    (.title | test("'"$CVE_EXPLICIT"'"; "i") | not)
  ) | .number] | .[]' "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json")

  for PR_NUM in $DEP_ONLY_NUMS; do
    BODY=$(gh pr view "$PR_NUM" --repo "$REPO" --json body \
      --jq '.body // ""' 2>/dev/null | sanitize_str)
    if ! echo "$BODY" | grep -qiE "$SECURITY_BODY"; then
      echo "  Dropped PR #$PR_NUM from CVE bucket — dep update with no security signal in body"
      jq --argjson n "$PR_NUM" '[.[] | select(.number != $n)]' \
        "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json" \
        > "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json.tmp" \
        && mv "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json.tmp" \
              "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json"
    fi
  done
fi

CVE_TOTAL=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json")
CVE_MERGED=$(jq '[.[] | select(.state == "MERGED")] | length' "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json")
CVE_CLOSED=$(jq '[.[] | select(.state == "CLOSED")] | length' "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json")

BUGFIX_TOTAL=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json")
BUGFIX_MERGED=$(jq '[.[] | select(.state == "MERGED")] | length' "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json")
BUGFIX_CLOSED=$(jq '[.[] | select(.state == "CLOSED")] | length' "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json")

echo "  CVE bucket:    $CVE_TOTAL PRs ($CVE_MERGED merged, $CVE_CLOSED closed)"
echo "  Bugfix bucket: $BUGFIX_TOTAL PRs ($BUGFIX_MERGED merged, $BUGFIX_CLOSED closed)"
```

If both buckets are empty, report this clearly and exit — the repo may not have
recognizable fix PR naming conventions. Suggest the user check PR title patterns.

### 3.5. Fetch Commit Fallback

For any bucket with fewer than 3 merged PRs, scan recent commits as a supplementary
signal source. Skip this step entirely if `--pr` was specified (user chose the data).

```bash
# Fetch commit fallback for a bucket if merged PR count < 3
# Args: BUCKET_LABEL META_FILE OUT_FILE MSG_PATTERN
fetch_commit_fallback() {
  local LABEL="$1"
  local META_FILE="$2"
  local OUT_FILE="$3"
  local MSG_PATTERN="$4"

  echo "[]" > "$OUT_FILE"

  # Skip if manual PR mode — user chose the data explicitly
  [ -n "$SPECIFIC_PR_NUMBERS" ] && return

  local MERGED_COUNT
  MERGED_COUNT=$(jq '[.[] | select(.state == "MERGED")] | length' "$META_FILE")

  if [ "$MERGED_COUNT" -ge 3 ]; then
    return  # Enough PR data — no fallback needed
  fi

  echo "  $LABEL bucket: $MERGED_COUNT merged PRs — scanning commits as fallback..."

  # Fetch up to 100 recent commit messages (lightweight — no file data yet)
  gh api "repos/$REPO/commits?per_page=100" \
    --jq '.[] | {sha: .sha, message: .commit.message}' \
    > "/tmp/guidance-gen/$REPO_SLUG/${LABEL}-commits-raw.jsonl" 2>/dev/null

  local SAMPLED=0
  local MAX_COMMITS=50

  while IFS= read -r LINE && [ "$SAMPLED" -lt "$MAX_COMMITS" ]; do
    local SHA MSG_RAW TITLE

    SHA=$(echo "$LINE" | jq -r '.sha')
    MSG_RAW=$(echo "$LINE" | jq -r '.message' | sanitize_str)
    TITLE=$(echo "$MSG_RAW" | head -1)

    # Filter by message pattern for this bucket
    echo "$TITLE" | grep -qiE "$MSG_PATTERN" || continue

    # For dep/bump commits without an explicit CVE/GHSA in the title,
    # verify the commit body contains a security indicator.
    # MSG_RAW already contains the full message — no extra API call needed.
    if echo "$TITLE" | grep -qiE "^[Bb]ump |^deps\(|^build\(deps\)"; then
      if ! echo "$TITLE" | grep -qiE "CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|^[Ss]ecurity:|^fix\(cve\):"; then
        if ! echo "$MSG_RAW" | grep -qiE "CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|security|vulnerab"; then
          continue  # dep update with no security signal — skip
        fi
      fi
    fi

    # Fetch file list for this commit (targeted — only for matched commits)
    local FILES
    FILES=$(gh api "repos/$REPO/commits/$SHA" \
      --jq '[.files[].filename]' 2>/dev/null || echo "[]")

    local BODY
    BODY=$(echo "$MSG_RAW" | tail -n +2 | tr '\n' ' ' | cut -c1-300)

    local RECORD
    RECORD=$(jq -n \
      --arg sha "$SHA" \
      --arg title "$TITLE" \
      --arg body "$BODY" \
      --argjson files "$FILES" \
      '{source: "commit", sha: $sha, state: "MERGED",
        title: $title, branch: "", labels: [],
        files: $files, changes_requested: [], close_reason: null,
        commit_body: $body}' 2>/tmp/guidance-jq-err.txt)

    if [ $? -ne 0 ]; then
      echo "  WARNING: commit $SHA skipped — $(cat /tmp/guidance-jq-err.txt)"
      continue
    fi

    jq --argjson rec "$RECORD" '. + [$rec]' "$OUT_FILE" > "${OUT_FILE}.tmp" \
      && mv "${OUT_FILE}.tmp" "$OUT_FILE"
    SAMPLED=$((SAMPLED + 1))

  done < "/tmp/guidance-gen/$REPO_SLUG/${LABEL}-commits-raw.jsonl"

  local COMMIT_COUNT
  COMMIT_COUNT=$(jq 'length' "$OUT_FILE")
  echo "  Found $COMMIT_COUNT matching $LABEL commits"

  # Save to artifacts for transparency
  cp "$OUT_FILE" "artifacts/guidance/$REPO_SLUG/raw/${LABEL}-commits.json"
}

fetch_commit_fallback "cve" \
  "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/cve-commits.json" \
  "CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|^[Ss]ecurity:|^fix\(cve\):|^Fix CVE|^[Bb]ump |^deps\(|^build\(deps\)"

fetch_commit_fallback "bugfix" \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-commits.json" \
  "^fix[:(]|^bugfix|^bug fix|fixes[[:space:]]#[0-9]+|closes[[:space:]]#[0-9]+"
```

### 4. Fetch Per-PR Details (Pass 2 — targeted)

For each PR in both buckets, fetch only: file paths changed and review data.
For closed PRs, also fetch the last 2 comments (closing context).

Process each bucket the same way. Replace `$META_FILE` and `$OUT_FILE` accordingly.

```bash
# Strip control characters from a string (keeps printable ASCII + tab + newline)
sanitize_str() {
  tr -cd '[:print:]\t\n'
}

fetch_pr_details() {
  local META_FILE="$1"
  local OUT_FILE="$2"
  local COUNT=$(jq 'length' "$META_FILE")
  local FAILED=0

  echo "[]" > "$OUT_FILE"

  for i in $(seq 0 $((COUNT - 1))); do
    NUMBER=$(jq -r ".[$i].number" "$META_FILE")
    STATE=$(jq -r ".[$i].state" "$META_FILE")
    # Sanitize string fields at extraction time to strip control characters
    TITLE=$(jq -r ".[$i].title" "$META_FILE" | sanitize_str)
    BRANCH=$(jq -r ".[$i].headRefName" "$META_FILE" | sanitize_str)
    LABELS=$(jq -c "[.[$i].labels[].name]" "$META_FILE")

    # Fetch files and reviews in one call
    PR_DETAIL=$(gh pr view "$NUMBER" --repo "$REPO" \
      --json files,reviews 2>/dev/null)

    FILES=$(echo "$PR_DETAIL" | jq -c '[.files[].path]')

    # Extract REQUEST_CHANGES review bodies — sanitize inside jq before truncating
    CHANGES_REQ=$(echo "$PR_DETAIL" | jq -c '[
      .reviews[] |
      select(.state == "CHANGES_REQUESTED") |
      .body |
      gsub("[\\u0000-\\u0008\\u000b-\\u001f\\u007f]"; "") |
      gsub("\\n|\\r"; " ") |
      .[0:200]
    ]')

    # For closed PRs: get last 2 comments, sanitize inside jq
    CLOSE_REASON="null"
    if [ "$STATE" = "CLOSED" ]; then
      CLOSE_REASON=$(gh pr view "$NUMBER" --repo "$REPO" \
        --json comments \
        --jq '.comments | .[-2:] | map(
          .body |
          gsub("[\\u0000-\\u0008\\u000b-\\u001f\\u007f]"; "") |
          gsub("\\n|\\r"; " ") |
          .[0:200]
        ) | join(" | ")' \
        2>/dev/null | jq -Rs '.')
    fi

    # Build compact record — capture jq errors per PR instead of silently dropping
    RECORD=$(jq -n \
      --argjson number "$NUMBER" \
      --arg state "$STATE" \
      --arg title "$TITLE" \
      --arg branch "$BRANCH" \
      --argjson labels "$LABELS" \
      --argjson files "$FILES" \
      --argjson changes_requested "$CHANGES_REQ" \
      --argjson close_reason "$CLOSE_REASON" \
      '{number: $number, state: $state, title: $title, branch: $branch,
        labels: $labels, files: $files,
        changes_requested: $changes_requested, close_reason: $close_reason}' \
      2>/tmp/guidance-jq-err.txt)

    if [ $? -ne 0 ]; then
      echo "  WARNING: PR #$NUMBER skipped — jq error: $(cat /tmp/guidance-jq-err.txt)"
      FAILED=$((FAILED + 1))
      continue
    fi

    jq --argjson rec "$RECORD" '. + [$rec]' "$OUT_FILE" > "${OUT_FILE}.tmp" \
      && mv "${OUT_FILE}.tmp" "$OUT_FILE"
  done

  if [ "$FAILED" -gt 0 ]; then
    echo "  WARNING: $FAILED PR(s) skipped due to unparseable content. Check raw data in artifacts."
  fi
}

fetch_pr_details \
  "/tmp/guidance-gen/$REPO_SLUG/cve-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/cve-details.json"

fetch_pr_details \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-details.json"

# Merge commit fallback records into the detail files
jq -s '.[0] + .[1]' \
  "/tmp/guidance-gen/$REPO_SLUG/cve-details.json" \
  "/tmp/guidance-gen/$REPO_SLUG/cve-commits.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/cve-details-merged.json" \
  && mv "/tmp/guidance-gen/$REPO_SLUG/cve-details-merged.json" \
        "/tmp/guidance-gen/$REPO_SLUG/cve-details.json"

jq -s '.[0] + .[1]' \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-details.json" \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-commits.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/bugfix-details-merged.json" \
  && mv "/tmp/guidance-gen/$REPO_SLUG/bugfix-details-merged.json" \
        "/tmp/guidance-gen/$REPO_SLUG/bugfix-details.json"

# Save to artifacts for reference
cp "/tmp/guidance-gen/$REPO_SLUG/cve-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/cve-prs.json"
cp "/tmp/guidance-gen/$REPO_SLUG/bugfix-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/bugfix-prs.json"
```

### 5. Synthesize Patterns

Read `cve-details.json` and `bugfix-details.json` from the artifacts.
Analyze them as the agent — do NOT write a script for this step.

**Records have two sources — treat them differently:**

Records with no `source` field (or `source != "commit"`) are PR records.
Records with `source: "commit"` came from the commit fallback and have no
`changes_requested` or `close_reason` data.

**Inclusion thresholds by source:**

| Source | Min occurrences per rule |
|--------|--------------------------|
| Merged PRs (10+ in bucket) | 3 |
| Merged PRs (3–9 in bucket) | 2 |
| Merged PRs (1–2 in bucket) | 1 |
| Commits only | 5 |
| Mixed (PRs + commits) | 3 total, at least 1 PR |

**What to extract from PR records:**
- **Title format**: What template do titles follow?
- **Branch format**: What naming pattern do branches use?
- **Files changed**: Which files appear together most often?
- **Labels**: What labels are consistently applied?
- **Co-changes**: When package A changes, does package B always change too?
- **From changes_requested**: What reviewers asked for — these become proactive rules.
- **From close_reason + changes_requested**: Why PRs were rejected — these become "don'ts".

**What to extract from commit records (no reviewer signal available):**
- **Message format**: Title line pattern, body structure, trailers (`Co-authored-by:`, `Fixes #`)
- **Files changed**: Which files appear together in fix commits
- **Co-changes**: Package co-upgrade patterns visible in file sets

**Commit-only rules cannot populate the "Don'ts" section** — there is no rejection
signal from commits. If a bucket is commit-only, omit the Don'ts section entirely.

**Evidence notation:**
- PR-sourced: `(8/9 merged PRs)`
- Commit-sourced: `(7 commits)`
- Mixed: `(3/4 merged PRs + 5 commits)`

**Output of synthesis step:**
Write an intermediate analysis file per bucket:

```
artifacts/guidance/<repo-slug>/analysis/cve-patterns.md
artifacts/guidance/<repo-slug>/analysis/bugfix-patterns.md
```

Each analysis file is a structured list:
```
TITLE_FORMAT: "Security: Fix CVE-YYYY-XXXXX (<package>)" (3/4 merged PRs + 6 commits)
BRANCH_FORMAT: "fix/cve-YYYY-XXXXX-<package>-attempt-N" (3/4 merged PRs)
FILES_GO_STDLIB: go.mod + Dockerfile + Dockerfile.konflux (8 commits)
PROACTIVE_go_sum: Include go.sum — flagged missing in N closed PRs
DONT_multiple_cves: One CVE per PR — N closed PRs rejected for combining
...
```

### 6. Generate Guidance Files

From the analysis files, generate the final guidance files.

**Formatting constraints:**
- Target 80 lines per file — this is a guideline for fresh generation, not a hard truncation
- No narrative paragraphs — one rule per line or a tight code block
- Evidence counts are inline and terse: `(N/M merged)`, `(N closed PRs)`
- No full PR examples — only the distilled pattern
- If the synthesized output naturally exceeds 80 lines (many strong patterns),
  include all rules that meet the threshold. Note the line count in the PR description.

**CVE guidance file template** — write to `artifacts/guidance/<repo-slug>/output/cve-fix-guidance.md`.

When in manual PR mode, the header must note which PRs were used:

```markdown
# CVE Fix Guidance — <repo>
<!-- last-analyzed: <YYYY-MM-DD> | cve-merged: N | cve-closed: M | manual-selection: PR#A,PR#B -->
```

When commit fallback was used, add a `commit-fallback` count to the header:

```markdown
# CVE Fix Guidance — <repo>
<!-- last-analyzed: <YYYY-MM-DD> | cve-merged: N | cve-closed: M | cve-commits: K -->
```

In auto mode with no fallback needed, omit the `cve-commits` field:

```markdown
# CVE Fix Guidance — <repo>
<!-- last-analyzed: <YYYY-MM-DD> | cve-merged: N | cve-closed: M -->

## Titles
`<pattern observed>` (N/N)

## Branches
`<pattern observed>` (N/N)

## Files — <language/ecosystem>
<rule about which files to change together> (N/N)
<any co-upgrade rules>

## PR Description
Required sections (missing caused REQUEST_CHANGES in N PRs):
- <section 1>
- <section 2>
...

## Jira / Issue References
<format rule> (N PRs flagged incorrect format)

## Don'ts
- <rule from closed PRs> (N cases)
- <rule from closed PRs> (N cases)
...
```

**Bugfix guidance file template** — write to `artifacts/guidance/<repo-slug>/output/bugfix-guidance.md`:

```markdown
# Bugfix Guidance — <repo>
<!-- last-analyzed: <YYYY-MM-DD> | bugfix-merged: N | bugfix-closed: M -->

## Titles
`<pattern observed>` (N/N)

## Branches
`<pattern observed>` (N/N)

## Scope Values
<list of scopes seen in merged PR titles> (from N PRs)

## Test Requirements
<what tests are expected> (N/N merged PRs included this)

## PR Must Include
- <field/section required by reviewers> (N PRs)
...

## Don'ts
- <rule from closed PRs> (N cases)
...
```

**Threshold rules — adapt based on available data:**
- 10+ merged PRs in bucket → require 3+ PRs per rule (standard threshold)
- 3–9 merged PRs → require 2+ PRs per rule
- 1–2 merged PRs → require 1+ PR per rule; add a `limited-data` warning in the file header

**If a section has no rules meeting the applicable threshold, omit that section entirely.**
Do not write sections with placeholder text or "not enough data" notes — just omit them.

**If a bucket has 0 merged PRs**, skip that guidance file entirely and log why.

**If only one bucket had data** (e.g., no CVE PRs found), only generate the file for
the bucket that had data. Log which file was skipped and why.

### 7. Create Pull Request in Target Repository

Clone the repository, add the guidance files, and open a PR.

```bash
TODAY=$(date +%Y-%m-%d)
BRANCH_NAME="chore/add-pr-guidance-$TODAY"

# Clone to /tmp
CLONE_DIR="/tmp/guidance-gen/$REPO_SLUG/repo"
git clone "https://github.com/$REPO.git" "$CLONE_DIR"
cd "$CLONE_DIR"

# Configure git credentials
gh auth setup-git 2>/dev/null || true

# Create branch
git checkout -b "$BRANCH_NAME"

# Copy generated files
CVE_OUTPUT="$OLDPWD/artifacts/guidance/$REPO_SLUG/output/cve-fix-guidance.md"
BUGFIX_OUTPUT="$OLDPWD/artifacts/guidance/$REPO_SLUG/output/bugfix-guidance.md"

if [ -f "$CVE_OUTPUT" ]; then
  mkdir -p .cve-fix
  cp "$CVE_OUTPUT" .cve-fix/examples.md
fi

if [ -f "$BUGFIX_OUTPUT" ]; then
  mkdir -p .bugfix
  cp "$BUGFIX_OUTPUT" .bugfix/guidance.md
fi

# Commit
git add .cve-fix .bugfix
git commit -m "chore: add automated PR guidance files

Guidance files generated by the PR Guidance Generator workflow.
These files teach automated fix workflows how this repo expects
PRs to be structured, based on analysis of merged and closed PRs.

Files added:
$([ -f "$CVE_OUTPUT" ] && echo "  - .cve-fix/examples.md (CVE fix conventions)")
$([ -f "$BUGFIX_OUTPUT" ] && echo "  - .bugfix/guidance.md (Bugfix conventions)")

Co-Authored-By: PR Guidance Generator <noreply@anthropic.com>"

# Build PR body
CVE_MERGED_COUNT=$(jq '[.[] | select(.state == "MERGED")] | length' \
  "$OLDPWD/artifacts/guidance/$REPO_SLUG/raw/cve-prs.json" 2>/dev/null || echo 0)
CVE_CLOSED_COUNT=$(jq '[.[] | select(.state == "CLOSED")] | length' \
  "$OLDPWD/artifacts/guidance/$REPO_SLUG/raw/cve-prs.json" 2>/dev/null || echo 0)
BUGFIX_MERGED_COUNT=$(jq '[.[] | select(.state == "MERGED")] | length' \
  "$OLDPWD/artifacts/guidance/$REPO_SLUG/raw/bugfix-prs.json" 2>/dev/null || echo 0)
BUGFIX_CLOSED_COUNT=$(jq '[.[] | select(.state == "CLOSED")] | length' \
  "$OLDPWD/artifacts/guidance/$REPO_SLUG/raw/bugfix-prs.json" 2>/dev/null || echo 0)

PR_BODY=$(cat <<EOF
## Summary

Adds guidance files that teach automated fix workflows how this repository
expects pull requests to be structured.

## Files Added

$([ -f "$CVE_OUTPUT" ] && echo "- \`.cve-fix/examples.md\` — CVE fix conventions (used by CVE Fixer workflow)")
$([ -f "$BUGFIX_OUTPUT" ] && echo "- \`.bugfix/guidance.md\` — Bugfix conventions (used by Bugfix workflow)")

## How These Were Generated

Analyzed the repository's PR history:
- CVE PRs: ${CVE_MERGED_COUNT} merged + ${CVE_CLOSED_COUNT} closed
- Bugfix PRs: ${BUGFIX_MERGED_COUNT} merged + ${BUGFIX_CLOSED_COUNT} closed

Rules are only included when observed in 3+ PRs.
Patterns from closed/rejected PRs form the "don'ts" sections.

## How Automated Workflows Use These Files

When the CVE Fixer workflow runs on this repository, it reads \`.cve-fix/examples.md\`
before making any changes and applies the conventions found there — PR title format,
branch naming, which files to update together, co-upgrade requirements, and so on.

The Bugfix workflow reads \`.bugfix/guidance.md\` similarly.

## Maintenance

Run \`/guidance.update <repo-url>\` periodically to refresh with new PRs.

---
Generated by PR Guidance Generator workflow
EOF
)

# Fork-aware push and PR creation
UPSTREAM_OWNER="${REPO%%/*}"
REPO_NAME="${REPO##*/}"
DEFAULT_BRANCH=$(gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')
GH_USER=$(gh api user --jq .login 2>/dev/null || \
          gh api /installation/repositories --jq '.repositories[0].owner.login' 2>/dev/null || \
          echo "")

git config user.name "${GH_USER:-guidance-generator}"
git config user.email "${GH_USER:-guidance}@users.noreply.github.com"

FORK_PUSH=false
FORK_OWNER=""

# Attempt 1: direct push to upstream
if git push origin "$BRANCH_NAME" 2>/tmp/guidance-push-err.txt; then
  echo "  Pushed to upstream directly"
elif [ -n "$GH_USER" ]; then
  # Attempt 2: find or create a fork
  echo "  Direct push failed — checking for fork of $REPO..."
  FORK=$(gh repo list "$GH_USER" --fork --json nameWithOwner,parent \
    --jq ".[] | select(.parent.owner.login == \"$UPSTREAM_OWNER\" and .parent.name == \"$REPO_NAME\") | .nameWithOwner" \
    2>/dev/null)

  if [ -z "$FORK" ]; then
    echo "  No fork found — creating fork..."
    if gh repo fork "$REPO" --clone=false 2>/dev/null; then
      sleep 3  # give GitHub time to provision the fork
      FORK="$GH_USER/$REPO_NAME"
      echo "  Fork created: $FORK"
    else
      echo "  ERROR: Could not create fork automatically."
      echo "  Create one manually at: https://github.com/$REPO/fork"
      echo "  Then re-run: /guidance.generate $REPO"
      FAILED_REPOS+=("$REPO -> fork creation failed; create at https://github.com/$REPO/fork and re-run")
      cd /; rm -rf "/tmp/guidance-gen/$REPO_SLUG"; continue
    fi
  else
    echo "  Found existing fork: $FORK"
  fi

  FORK_OWNER="${FORK%%/*}"
  git remote add fork "https://github.com/$FORK.git" 2>/dev/null || \
    git remote set-url fork "https://github.com/$FORK.git"
  git push fork "$BRANCH_NAME"
  FORK_PUSH=true
else
  # No gh auth and direct push failed — provide manual fallback
  echo "  ERROR: Push failed and gh is not authenticated."
  echo "  Manual steps to submit this PR:"
  echo "    1. Fork https://github.com/$REPO"
  echo "    2. git -C /tmp/guidance-gen/$REPO_SLUG/repo remote add fork https://github.com/YOUR_USER/$REPO_NAME.git"
  echo "    3. git -C /tmp/guidance-gen/$REPO_SLUG/repo push fork $BRANCH_NAME"
  echo "    4. Open PR: https://github.com/$REPO/compare/$BRANCH_NAME"
  FAILED_REPOS+=("$REPO -> push failed, no gh auth; see manual steps above")
  cd /; rm -rf "/tmp/guidance-gen/$REPO_SLUG"; continue
fi

# Create PR
if $FORK_PUSH; then
  PR_URL=$(gh pr create \
    --repo "$REPO" \
    --base "$DEFAULT_BRANCH" \
    --head "$FORK_OWNER:$BRANCH_NAME" \
    --title "chore: add automated PR guidance files" \
    --body "$PR_BODY")
else
  PR_URL=$(gh pr create \
    --repo "$REPO" \
    --base "$DEFAULT_BRANCH" \
    --title "chore: add automated PR guidance files" \
    --body "$PR_BODY")
fi
echo "PR created: $PR_URL"
```

### 8. Cleanup (per repo)

```bash
  cd /
  rm -rf "/tmp/guidance-gen/$REPO_SLUG"

  # Collect result for final summary
  if [ -n "${PR_URL:-}" ]; then
    PR_RESULTS+=("$REPO -> $PR_URL")
  else
    FAILED_REPOS+=("$REPO -> PR creation failed (see output above)")
  fi

done  # end of per-repo loop
```

### 9. Print Summary

Print one entry per repo, then a totals line.

```
Done. Processed <N> repo(s).

org/repo1
  CVE:    12 rules | Bugfix: 9 rules
  PR:     https://github.com/org/repo1/pull/88

org/repo2
  CVE:    skipped (0 merged CVE PRs)
  Bugfix: 7 rules
  PR:     https://github.com/org/repo2/pull/41

org/repo3 — FAILED: cannot access repository

---
PRs created: <N>  |  Failed: <M>
```

## Output

- `artifacts/guidance/<repo-slug>/raw/cve-prs.json` — raw compact PR data
- `artifacts/guidance/<repo-slug>/raw/bugfix-prs.json`
- `artifacts/guidance/<repo-slug>/analysis/cve-patterns.md` — intermediate patterns
- `artifacts/guidance/<repo-slug>/analysis/bugfix-patterns.md`
- `artifacts/guidance/<repo-slug>/output/cve-fix-guidance.md` — final CVE guidance
- `artifacts/guidance/<repo-slug>/output/bugfix-guidance.md` — final bugfix guidance
- Pull request in target repository

## Success Criteria

- [ ] All repos parsed from input (space and comma separated)
- [ ] gh auth validated once before the loop
- [ ] Each repo processed independently — one failure does not abort others
- [ ] Per-repo: both buckets filtered from PR metadata
- [ ] Per-repo: per-PR details fetched (files + review REQUEST_CHANGES)
- [ ] Per-repo: patterns synthesized with adaptive threshold
- [ ] Per-repo: guidance files written to artifacts/guidance/<repo-slug>/output/
- [ ] Per-repo: PR created in target repo
- [ ] Per-repo: /tmp cleaned up after PR creation
- [ ] Final summary lists all repos with PR URLs and any failures

## Notes

### Limited Data
Never skip a guidance file just because a bucket has few merged PRs.
Only skip if the bucket has **0 merged PRs**.

For small datasets, apply an adaptive threshold and add a warning to the file header:

```markdown
<!-- last-analyzed: YYYY-MM-DD | cve-merged: 1 | cve-closed: 0 | WARNING: limited data — patterns based on 1 merged PR, verify before relying on these -->
```

This gives the workflow something to work with while signalling to reviewers
that the file should be revisited once more PRs accumulate.

Log: "CVE bucket has N merged PR(s) — generating with limited-data warning."

### Repos with No Matching PRs
If neither bucket has data, the repo likely uses non-standard PR naming.
Report this and ask the user to provide example PR numbers or title patterns
so the filters can be adjusted.

### GitHub API Rate Limits
`gh` uses authenticated calls (5000 req/hr). The per-PR detail fetch makes
2 API calls per PR (files+reviews, and comments for closed PRs).
At the default limit of 100 per bucket, worst case is ~400 API calls — well
within limits. If the user hits rate limits, reduce with `--limit 50`.

### If .cve-fix/ or .bugfix/ Already Exist in Repo
If these directories already exist in the default branch, do not overwrite silently.
Warn the user: "Existing guidance files found in repo. Use /guidance.update instead,
or pass --force to overwrite."
Check with:
```bash
gh api repos/$REPO/contents/.cve-fix/examples.md > /dev/null 2>&1 && EXISTING_CVE=true
gh api repos/$REPO/contents/.bugfix/guidance.md > /dev/null 2>&1 && EXISTING_BUGFIX=true
```
