# /guidance.update - Update Existing PR Guidance Files

## Purpose
Fetch PRs created since the last analysis, extract new patterns, merge them
into existing guidance files, and open a PR in the repository with the updates.

## Execution Style

Be concise. Brief status per phase, full summary at end.

Example:
```
Reading existing guidance from org/repo...
  .cve-fix/examples.md — last analyzed: 2026-01-15
  .bugfix/guidance.md  — last analyzed: 2026-01-15

Fetching PRs since 2026-01-15... 23 new PRs
  CVE bucket: 8 PRs (6 merged, 2 closed)
  Bugfix bucket: 12 PRs (11 merged, 1 closed)

Synthesizing new patterns...
  CVE:    2 new rules, 3 evidence counts updated, 1 contradiction flagged
  Bugfix: 1 new rule, 2 evidence counts updated

Updating files and creating PR... https://github.com/org/repo/pull/103
```

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- `jq` installed
- Guidance files must already exist in the repo (run `/guidance.generate` first)

## Arguments

```
/guidance.update <repo-url> [<repo-url2> ...] [--cve-only] [--bugfix-only]
/guidance.update <repo-url>[,<repo-url2>,...] [--cve-only] [--bugfix-only]
/guidance.update <repo-url> [<repo-url2> ...] --pr <url-or-number> [<url-or-number> ...]
```

- `repo-url`: One or more repos — space-separated or comma-separated (or both).
  Each repo is updated independently and gets its own PR.
- `--cve-only`: Only update `.cve-fix/examples.md` — skip bugfix guidance.
- `--bugfix-only`: Only update `.bugfix/guidance.md` — skip CVE guidance.
- `--pr <refs>`: PR URLs or numbers — space-separated, comma-separated, or mixed.
  Full URLs are applied only to their matching repo. Plain numbers are applied to
  all repos. The `last-analyzed` date is still updated to today in all files.

## Process

### 1. Parse Arguments and Validate

```bash
# Validate gh auth once
gh auth status || { echo "ERROR: gh not authenticated. Run 'gh auth login'"; exit 1; }

# Normalize repo args: replace commas with spaces, strip GitHub URL prefix, deduplicate
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

REPOS=($(printf '%s\n' "${REPOS[@]}" | awk '!seen[$0]++'))

if [ ${#REPOS[@]} -eq 0 ]; then
  echo "ERROR: No valid repository references provided."
  exit 1
fi

echo "Repos to process (${#REPOS[@]}):"
for R in "${REPOS[@]}"; do echo "  - $R"; done

# Parse --pr: full URLs map to their repo; plain numbers apply to all repos
declare -A REPO_SPECIFIC_PRS
GLOBAL_PR_NUMBERS=""

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

# Parse scope flags (apply to all repos)
CVE_ONLY=false
BUGFIX_ONLY=false
[ "${CVE_ONLY_FLAG:-}" = "true" ] && CVE_ONLY=true
[ "${BUGFIX_ONLY_FLAG:-}" = "true" ] && BUGFIX_ONLY=true
if $CVE_ONLY && $BUGFIX_ONLY; then
  echo "ERROR: --cve-only and --bugfix-only are mutually exclusive."
  exit 1
fi

PR_RESULTS=()
FAILED_REPOS=()
```

---
> **Steps 2–9 repeat for each repo in `${REPOS[@]}`.**

```bash
for REPO in "${REPOS[@]}"; do
  echo ""
  echo "=== $REPO ==="

  if ! gh repo view "$REPO" --json name > /dev/null 2>&1; then
    echo "  ERROR: Cannot access $REPO — skipping"
    FAILED_REPOS+=("$REPO -> cannot access repository")
    continue
  fi

  REPO_SLUG=$(echo "$REPO" | tr '/' '-')

  SPECIFIC_PR_NUMBERS="${REPO_SPECIFIC_PRS[$REPO]:-} $GLOBAL_PR_NUMBERS"
  SPECIFIC_PR_NUMBERS=$(echo "$SPECIFIC_PR_NUMBERS" | tr -s ' ' | sed 's/^ //')
  [ -n "$SPECIFIC_PR_NUMBERS" ] && echo "  Manual PR mode: PR(s) $SPECIFIC_PR_NUMBERS"

  mkdir -p "artifacts/guidance/$REPO_SLUG/raw"
  mkdir -p "artifacts/guidance/$REPO_SLUG/analysis"
  mkdir -p "artifacts/guidance/$REPO_SLUG/output"
  mkdir -p "/tmp/guidance-gen/$REPO_SLUG"
```

### 2. Read Existing Guidance Files from Repository

Clone the repo and read the existing guidance files. Extract the
`last-analyzed` date from each file's header comment.

```bash
CLONE_DIR="/tmp/guidance-gen/$REPO_SLUG/repo"
git clone "https://github.com/$REPO.git" "$CLONE_DIR"
cd "$CLONE_DIR"
gh auth setup-git 2>/dev/null || true

CVE_FILE="$CLONE_DIR/.cve-fix/examples.md"
BUGFIX_FILE="$CLONE_DIR/.bugfix/guidance.md"

FOUND_CVE=false
FOUND_BUGFIX=false
LAST_DATE=""

$BUGFIX_ONLY && echo "  --bugfix-only: skipping CVE guidance"
$CVE_ONLY    && echo "  --cve-only: skipping bugfix guidance"

if [ -f "$CVE_FILE" ] && ! $BUGFIX_ONLY; then
  FOUND_CVE=true
  # Extract date from: <!-- last-analyzed: YYYY-MM-DD | ... -->
  CVE_DATE=$(grep -m1 'last-analyzed:' "$CVE_FILE" | \
    grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  echo "  .cve-fix/examples.md — last analyzed: ${CVE_DATE:-unknown}"
  LAST_DATE="$CVE_DATE"
fi

if [ -f "$BUGFIX_FILE" ] && ! $CVE_ONLY; then
  FOUND_BUGFIX=true
  BUGFIX_DATE=$(grep -m1 'last-analyzed:' "$BUGFIX_FILE" | \
    grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  echo "  .bugfix/guidance.md  — last analyzed: ${BUGFIX_DATE:-unknown}"
  # Use earlier of the two dates to avoid missing PRs
  if [ -n "$BUGFIX_DATE" ] && [ -n "$LAST_DATE" ]; then
    LAST_DATE=$(echo -e "$LAST_DATE\n$BUGFIX_DATE" | sort | head -1)
  elif [ -n "$BUGFIX_DATE" ]; then
    LAST_DATE="$BUGFIX_DATE"
  fi
fi
```

**If neither file exists**, stop and redirect:

```
Neither .cve-fix/examples.md nor .bugfix/guidance.md found in <repo>.
Run /guidance.generate <repo-url> to create them first.
```

**If `last-analyzed` date cannot be parsed**, warn the user and default to
fetching the last 90 days of PRs, then proceed.

```bash
if [ -z "$LAST_DATE" ]; then
  echo "WARNING: Could not parse last-analyzed date. Defaulting to last 90 days."
  LAST_DATE=$(date -d "90 days ago" +%Y-%m-%d 2>/dev/null || \
              date -v-90d +%Y-%m-%d 2>/dev/null)
fi

echo "Fetching PRs since $LAST_DATE..."
```

### 3. Fetch New PRs (Pass 1)

**If `--pr` was specified**, skip the date-based bulk fetch and load only the given PRs:

```bash
if [ -n "$SPECIFIC_PR_NUMBERS" ]; then
  # Manual mode: fetch only specified PRs
  echo "[]" > "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json"
  for NUMBER in $SPECIFIC_PR_NUMBERS; do
    PR_META=$(gh pr view "$NUMBER" --repo "$REPO" \
      --json number,title,state,mergedAt,closedAt,labels,headRefName,latestReviews \
      2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$PR_META" ]; then
      echo "WARNING: Could not fetch PR #$NUMBER — skipping"
      continue
    fi
    jq --argjson meta "$PR_META" '. + [$meta]' \
      "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json" \
      > "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json.tmp" \
      && mv "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json.tmp" \
            "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json"
  done
  NEW_TOTAL=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json")
  echo "Loaded $NEW_TOTAL specified PR(s)"
else
  # Auto mode: fetch all PRs since last-analyzed date
  gh pr list \
    --repo "$REPO" \
    --state all \
    --limit 200 \
    --search "created:>$LAST_DATE" \
    --json number,title,state,mergedAt,closedAt,labels,headRefName,latestReviews \
    > "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json"
  NEW_TOTAL=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json")
  echo "Fetched $NEW_TOTAL new PRs since $LAST_DATE"
  if [ "$NEW_TOTAL" -eq 0 ]; then
    echo "No new PRs found since $LAST_DATE. Guidance files are already up to date."
    rm -rf "/tmp/guidance-gen/$REPO_SLUG"
    exit 0
  fi
fi
```

### 4. Filter New PRs into Buckets

In **auto mode**: CVE PRs take priority. In **manual mode (`--pr`)**: if a
specified PR matches neither pattern, include it in both buckets for Claude to classify.

```bash
# Explicit CVE/security signals — pass through unconditionally
CVE_EXPLICIT='CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|^[Ss]ecurity:|^fix\(cve\):|^Fix CVE'
# Dependency/version bump patterns — require body scan to confirm security relevance
CVE_DEP_PATTERN='^[Bb]ump |^deps\(|^build\(deps\)|^chore.*upgrade|^chore.*bump'
CVE_PATTERN="${CVE_EXPLICIT}|${CVE_DEP_PATTERN}"
CVE_BRANCH_PATTERN='^fix/cve-|^security/cve-|^dependabot/|^renovate/'
BUGFIX_PATTERN='^fix[:(]|^bugfix|^bug[[:space:]]fix|closes[[:space:]]#[0-9]+|fixes[[:space:]]#[0-9]+'
BUGFIX_BRANCH_PATTERN='^(bugfix|fix|bug)/'
SECURITY_BODY='CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|security|vulnerab|security.advisory'

jq '[.[] | select(
  (.title | test("'"$CVE_PATTERN"'"; "i")) or
  (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i"))
)]' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json"

jq '[.[] | select(
  (
    (.title | test("'"$BUGFIX_PATTERN"'"; "i")) or
    (.headRefName | test("'"$BUGFIX_BRANCH_PATTERN"'"; "i"))
  ) and
  (.title | test("'"$CVE_PATTERN"'"; "i") | not) and
  (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i") | not)
)]' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json"

# In manual mode: add unmatched PRs to both buckets
if [ -n "$SPECIFIC_PR_NUMBERS" ]; then
  UNMATCHED=$(jq '[.[] | select(
    ((.title | test("'"$CVE_PATTERN"'"; "i")) or (.headRefName | test("'"$CVE_BRANCH_PATTERN"'"; "i")) | not) and
    ((.title | test("'"$BUGFIX_PATTERN"'"; "i")) or (.headRefName | test("'"$BUGFIX_BRANCH_PATTERN"'"; "i")) | not)
  )]' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json")
  UNMATCHED_COUNT=$(echo "$UNMATCHED" | jq 'length')
  if [ "$UNMATCHED_COUNT" -gt 0 ]; then
    UNMATCHED_NUMS=$(echo "$UNMATCHED" | jq -r '.[].number' | tr '\n' ',' | sed 's/,$//')
    echo "  NOTE: PR(s) #$UNMATCHED_NUMS did not match CVE or bugfix patterns — included in both buckets"
    for META_FILE in "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json" \
                     "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json"; do
      jq --argjson extra "$UNMATCHED" '. + $extra' "$META_FILE" > "${META_FILE}.tmp" \
        && mv "${META_FILE}.tmp" "$META_FILE"
    done
  fi
fi

# Body scan: for dep-pattern matches without an explicit CVE/GHSA title,
# verify the PR body contains a security indicator before keeping it.
# Only runs in auto mode — manual --pr mode trusts the user's selection.
if [ -z "$SPECIFIC_PR_NUMBERS" ]; then
  DEP_ONLY_NUMS=$(jq -r '[.[] | select(
    (.title | test("'"$CVE_DEP_PATTERN"'"; "i")) and
    (.title | test("'"$CVE_EXPLICIT"'"; "i") | not)
  ) | .number] | .[]' "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json")

  for PR_NUM in $DEP_ONLY_NUMS; do
    BODY=$(gh pr view "$PR_NUM" --repo "$REPO" --json body \
      --jq '.body // ""' 2>/dev/null | sanitize_str)
    if ! echo "$BODY" | grep -qiE "$SECURITY_BODY"; then
      echo "  Dropped PR #$PR_NUM from CVE bucket — dep update with no security signal in body"
      jq --argjson n "$PR_NUM" '[.[] | select(.number != $n)]' \
        "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json" \
        > "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json.tmp" \
        && mv "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json.tmp" \
              "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json"
    fi
  done
fi

# Zero out skipped buckets so subsequent steps treat them as empty
$BUGFIX_ONLY && echo "[]" > "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json"
$CVE_ONLY    && echo "[]" > "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json"

NEW_CVE=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json")
NEW_BUGFIX=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json")
echo "  CVE bucket: $NEW_CVE new PRs"
echo "  Bugfix bucket: $NEW_BUGFIX new PRs"
```

### 4.5. Fetch Commit Fallback

For any bucket with fewer than 3 new merged PRs since the last-analyzed date,
scan recent commits as supplementary signal. Skip if `--pr` was specified.

```bash
fetch_commit_fallback() {
  local LABEL="$1"
  local META_FILE="$2"
  local OUT_FILE="$3"
  local MSG_PATTERN="$4"

  echo "[]" > "$OUT_FILE"

  [ -n "$SPECIFIC_PR_NUMBERS" ] && return

  local MERGED_COUNT
  MERGED_COUNT=$(jq '[.[] | select(.state == "MERGED")] | length' "$META_FILE")

  if [ "$MERGED_COUNT" -ge 3 ]; then
    return
  fi

  echo "  $LABEL bucket: $MERGED_COUNT new merged PRs — scanning commits as fallback..."

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

    echo "$TITLE" | grep -qiE "$MSG_PATTERN" || continue

    # For dep/bump commits without explicit CVE/GHSA in title, verify body has security signal.
    # MSG_RAW already contains the full message — no extra API call needed.
    if echo "$TITLE" | grep -qiE "^[Bb]ump |^deps\(|^build\(deps\)|^chore.*upgrade|^chore.*bump"; then
      if ! echo "$TITLE" | grep -qiE "CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|^[Ss]ecurity:|^fix\(cve\):"; then
        if ! echo "$MSG_RAW" | grep -qiE "CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|security|vulnerab"; then
          continue  # dep update with no security signal — skip
        fi
      fi
    fi

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
  cp "$OUT_FILE" "artifacts/guidance/$REPO_SLUG/raw/${LABEL}-commits.json"
}

fetch_commit_fallback "cve" \
  "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/cve-commits.json" \
  "CVE-[0-9]{4}-[0-9]+|GHSA-[a-zA-Z0-9-]+|^[Ss]ecurity:|^fix\(cve\):|^Fix CVE|^[Bb]ump |^deps\(|^build\(deps\)|^chore.*upgrade|^chore.*bump"

fetch_commit_fallback "bugfix" \
  "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-commits.json" \
  "^fix[:(]|^bugfix|^bug fix|fixes[[:space:]]#[0-9]+|closes[[:space:]]#[0-9]+"
```

### 5. Fetch Per-PR Details (Pass 2)

Same as `/guidance.generate` — files + reviews per PR, closing context for closed PRs.

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
  "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/new-cve-details.json"

fetch_pr_details \
  "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details.json"

# Merge commit fallback records into the detail files
jq -s '.[0] + .[1]' \
  "/tmp/guidance-gen/$REPO_SLUG/new-cve-details.json" \
  "/tmp/guidance-gen/$REPO_SLUG/cve-commits.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/new-cve-details-merged.json" \
  && mv "/tmp/guidance-gen/$REPO_SLUG/new-cve-details-merged.json" \
        "/tmp/guidance-gen/$REPO_SLUG/new-cve-details.json"

jq -s '.[0] + .[1]' \
  "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details.json" \
  "/tmp/guidance-gen/$REPO_SLUG/bugfix-commits.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details-merged.json" \
  && mv "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details-merged.json" \
        "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details.json"

cp "/tmp/guidance-gen/$REPO_SLUG/new-cve-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/new-cve-prs.json"
cp "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/new-bugfix-prs.json"
```

### 6. Synthesize New Patterns

Read both the new PR detail files AND the existing guidance files.

As the agent, analyze the new detail records. Records with `source: "commit"`
came from the commit fallback — treat them differently from PR records:

**Thresholds for new rules:**

| Source | Min for a new rule |
|--------|--------------------|
| Merged PRs | 3 (or 2 if bucket had <10, or 1 if <3) |
| Commits only | 5 |
| Mixed (PRs + commits) | 3 total, at least 1 PR |

**What commit records contribute:**
- Message/title format patterns
- File co-change patterns
- Commit body trailer conventions (`Co-authored-by:`, `Fixes #`, etc.)

**What commit records do NOT contribute:**
- Don'ts section (no rejection signal)
- Reviewer expectation rules (no `changes_requested` data)

**Evidence notation for new rules:**
- PR only: `(3/4 merged PRs)`
- Commit only: `(6 commits)`
- Mixed: `(2/3 merged PRs + 4 commits)`

For each pattern found in the combined data:

**A. New rule** — meets the threshold above and does not already exist in the
guidance file. Add it to the appropriate section.

**B. Reinforced rule** — already exists in the guidance file.
Update evidence count: `(8/9 merged)` → `(14/15 merged)` or add commit count:
`(8/9 merged)` → `(8/9 merged PRs + 5 commits)`.

**C. Contradicting rule** — a pattern in new merged PRs that directly contradicts
a "don't". Flag it:
```
- [REVIEW NEEDED] Multiple CVEs per PR — previously flagged as a don't,
  but PR #N was merged combining CVEs. Policy may have changed. (N/N new merged)
```

**D. New don't** — pattern from newly closed PRs (3+ cases). Commits cannot
produce new don'ts. Add only PR-sourced rejections here.

Write findings to:
- `artifacts/guidance/<repo-slug>/analysis/cve-update-patterns.md`
- `artifacts/guidance/<repo-slug>/analysis/bugfix-update-patterns.md`

Format: same structured list as in `/guidance.generate` step 5.

### 7. Merge Patterns into Existing Guidance Files

Read the cloned guidance files and apply the changes from step 6.

**Editing rules:**
- Update evidence counts in-place: find the line, update the `(N/M ...)` count
- Append new rules to the bottom of the appropriate section
- Append new don'ts to the Don'ts section
- Add `[REVIEW NEEDED]` lines at the bottom of the relevant section for contradictions
- Update the `last-analyzed` date in the header comment
- Update the merged/closed counts in the header comment
- Do NOT reorder existing rules — preserve the file structure

After editing, count the lines in each file. Never drop existing rules to
make room — always append new rules in full. If the file now exceeds 80 lines,
note it but do not truncate:

```bash
CVE_LINES=$(wc -l < "$CVE_FILE")
BUGFIX_LINES=$(wc -l < "$BUGFIX_FILE")

OVERSIZE_NOTE=""
if [ "$CVE_LINES" -gt 80 ]; then
  echo "  NOTE: .cve-fix/examples.md is now ${CVE_LINES} lines (target: 80)"
  OVERSIZE_NOTE="${OVERSIZE_NOTE}\n- \`.cve-fix/examples.md\` is ${CVE_LINES} lines. Consider running \`/guidance.generate\` to rebuild and consolidate."
fi
if [ "$BUGFIX_LINES" -gt 80 ]; then
  echo "  NOTE: .bugfix/guidance.md is now ${BUGFIX_LINES} lines (target: 80)"
  OVERSIZE_NOTE="${OVERSIZE_NOTE}\n- \`.bugfix/guidance.md\` is ${BUGFIX_LINES} lines. Consider running \`/guidance.generate\` to rebuild and consolidate."
fi
```

Include `$OVERSIZE_NOTE` in the PR description if non-empty so the reviewer
knows the file has grown and can decide whether to trigger a full rebuild.

**Update the header:**
```
<!-- last-analyzed: <TODAY> | cve-merged: <total-now> | cve-closed: <total-now> -->
```

Copy the updated files to artifacts output:
```bash
cp "$CVE_FILE" "artifacts/guidance/$REPO_SLUG/output/cve-fix-guidance.md"
cp "$BUGFIX_FILE" "artifacts/guidance/$REPO_SLUG/output/bugfix-guidance.md"
```

### 8. Create Pull Request with Updates

```bash
TODAY=$(date +%Y-%m-%d)
BRANCH_NAME="chore/update-pr-guidance-$TODAY"

cd "$CLONE_DIR"
git checkout -b "$BRANCH_NAME"

# Files are already updated in-place in the clone from step 7
git add .cve-fix .bugfix
git commit -m "chore: update PR guidance files ($TODAY)

Refreshed guidance based on PRs merged/closed since last analysis.

Changes:
- Updated evidence counts for existing rules
- Added new rules (if any new patterns emerged)
- Updated last-analyzed date to $TODAY

Co-Authored-By: PR Guidance Generator <noreply@anthropic.com>"

git push origin "$BRANCH_NAME"
```

Construct PR body summarizing what changed:

```bash
PR_BODY=$(cat <<EOF
## Summary

Updates guidance files with patterns from PRs merged/closed since the last analysis.

## What Changed

### CVE Guidance (.cve-fix/examples.md)
$(cat "artifacts/guidance/$REPO_SLUG/analysis/cve-update-patterns.md" | \
  grep -E "^(NEW_RULE|UPDATED_COUNT|CONTRADICTION|NEW_DONT):" | \
  sed 's/NEW_RULE:/- New rule:/' | \
  sed 's/UPDATED_COUNT:/- Updated evidence count:/' | \
  sed 's/CONTRADICTION:/- ⚠️ Contradiction flagged:/' | \
  sed 's/NEW_DONT:/- New don'\''t:/')

### Bugfix Guidance (.bugfix/guidance.md)
$(cat "artifacts/guidance/$REPO_SLUG/analysis/bugfix-update-patterns.md" | \
  grep -E "^(NEW_RULE|UPDATED_COUNT|CONTRADICTION|NEW_DONT):" | \
  sed 's/NEW_RULE:/- New rule:/' | \
  sed 's/UPDATED_COUNT:/- Updated evidence count:/' | \
  sed 's/CONTRADICTION:/- ⚠️ Contradiction flagged:/' | \
  sed 's/NEW_DONT:/- New don'\''t:/')

## New PRs Analyzed
- CVE PRs: ${NEW_CVE} (since ${LAST_DATE})
- Bugfix PRs: ${NEW_BUGFIX} (since ${LAST_DATE})

---
Generated by PR Guidance Generator workflow
EOF
)

PR_URL=$(gh pr create \
  --repo "$REPO" \
  --base "$(gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')" \
  --title "chore: update PR guidance files ($TODAY)" \
  --body "$PR_BODY")

echo "PR created: $PR_URL"
```

### 9. Cleanup (per repo)

```bash
  cd /
  rm -rf "/tmp/guidance-gen/$REPO_SLUG"

  if [ -n "${PR_URL:-}" ]; then
    PR_RESULTS+=("$REPO -> $PR_URL")
  else
    FAILED_REPOS+=("$REPO -> PR creation failed (see output above)")
  fi

done  # end of per-repo loop
```

### 10. Print Summary

```
Done. Processed <N> repo(s).

org/repo1
  New PRs analyzed: 8 CVE, 12 bugfix (since 2026-01-15)
  Changes: 2 new rules, 3 counts updated, 1 contradiction flagged
  PR: https://github.com/org/repo1/pull/103

org/repo2
  No guidance files found — run /guidance.generate first
  SKIPPED

org/repo3 — FAILED: cannot access repository

---
PRs created: <N>  |  Skipped: <M>  |  Failed: <K>
```

## Output

- `artifacts/guidance/<repo-slug>/raw/new-cve-prs.json`
- `artifacts/guidance/<repo-slug>/raw/new-bugfix-prs.json`
- `artifacts/guidance/<repo-slug>/analysis/cve-update-patterns.md`
- `artifacts/guidance/<repo-slug>/analysis/bugfix-update-patterns.md`
- `artifacts/guidance/<repo-slug>/output/cve-fix-guidance.md` (updated)
- `artifacts/guidance/<repo-slug>/output/bugfix-guidance.md` (updated)
- Pull request in target repository

## Success Criteria

- [ ] All repos parsed from input (space and comma separated)
- [ ] gh auth validated once before the loop
- [ ] Each repo processed independently — one failure does not abort others
- [ ] Per-repo: existing guidance files found and last-analyzed date extracted
- [ ] Per-repo: new PRs fetched (date-based or --pr specific)
- [ ] Per-repo: new patterns synthesized (new rules, updated counts, contradictions flagged)
- [ ] Per-repo: files updated in-place, no existing rules dropped
- [ ] Per-repo: files exceeding 80 lines flagged in PR description
- [ ] Per-repo: header timestamps updated
- [ ] Per-repo: PR created in target repo
- [ ] Per-repo: /tmp cleaned up
- [ ] Final summary lists all repos with PR URLs, skips, and failures

## Notes

### No New PRs Found
If 0 new PRs since the last-analyzed date, report this and exit cleanly.
Do not create a PR with no changes.

### Only One File Exists
If only `.cve-fix/examples.md` exists (no `.bugfix/guidance.md`), update only
the CVE file. Log that bugfix guidance was skipped.

### Contradictions Require Human Review
Do not automatically remove a "don't" rule just because a new merged PR
contradicts it. Flag it with `[REVIEW NEEDED]` and let the repo owner decide
if the convention changed. The PR reviewer will see the flag and can edit
the file before merging.

### Date Parsing Cross-Platform
`date -d` (Linux) and `date -v` (macOS) differ. Use both with fallback:
```bash
LAST_DATE=$(date -d "90 days ago" +%Y-%m-%d 2>/dev/null || \
            date -v-90d +%Y-%m-%d 2>/dev/null || \
            echo "2000-01-01")
```
