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
/guidance.generate <repo-url> [--cve-only] [--bugfix-only] [--limit N]
/guidance.generate <repo-url> --pr <url-or-number>[,<url-or-number>...]
```

- `repo-url`: Full GitHub URL (e.g., `https://github.com/org/repo`) or `org/repo`
- `--cve-only`: Skip bugfix analysis
- `--bugfix-only`: Skip CVE analysis
- `--limit N`: Max PRs to fetch per bucket (default: 100, min: 20)
- `--pr <refs>`: Comma-separated PR URLs or numbers to analyze instead of fetching all PRs.
  Skips bulk fetch entirely. Accepts full URLs (`https://github.com/org/repo/pull/123`)
  or plain numbers (`123`). The generated file will include a `manual-selection` note
  in its header.

## Process

### 1. Parse Arguments and Validate

Extract `REPO` in `org/repo` format from the provided URL or slug.
If not provided, ask: "What is the GitHub repository URL?"

Parse `--pr` into a comma-separated list of PR numbers. Accept both full GitHub
PR URLs and plain numbers:

```bash
# Validate gh auth
gh auth status || { echo "ERROR: gh not authenticated. Run 'gh auth login'"; exit 1; }

# Validate repo exists and is accessible
gh repo view "$REPO" --json name > /dev/null 2>&1 || {
  echo "ERROR: Cannot access $REPO. Check URL and permissions."
  exit 1
}

# Derive a safe slug for directory names (replace / with -)
REPO_SLUG=$(echo "$REPO" | tr '/' '-')

# Parse --pr flag: extract PR numbers from URLs or plain numbers
SPECIFIC_PR_NUMBERS=""
if [ -n "$PR_REFS" ]; then
  IFS=',' read -ra PR_LIST <<< "$PR_REFS"
  for PR_REF in "${PR_LIST[@]}"; do
    PR_REF=$(echo "$PR_REF" | tr -d ' ')
    if [[ "$PR_REF" =~ github\.com/[^/]+/[^/]+/pull/([0-9]+) ]]; then
      SPECIFIC_PR_NUMBERS="$SPECIFIC_PR_NUMBERS ${BASH_REMATCH[1]}"
    elif [[ "$PR_REF" =~ ^[0-9]+$ ]]; then
      SPECIFIC_PR_NUMBERS="$SPECIFIC_PR_NUMBERS $PR_REF"
    else
      echo "WARNING: Could not parse PR reference '$PR_REF' — skipping"
    fi
  done
  SPECIFIC_PR_NUMBERS=$(echo "$SPECIFIC_PR_NUMBERS" | tr -s ' ' | sed 's/^ //')
  echo "Manual PR mode: analyzing PR(s) $SPECIFIC_PR_NUMBERS"
fi

# Setup directories
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
CVE_PATTERN='CVE-[0-9]{4}-[0-9]+|^[Ss]ecurity:|^fix\(cve\):|^Fix CVE'
CVE_BRANCH_PATTERN='^fix/cve-|^security/cve-'
BUGFIX_PATTERN='^fix[:(]|^bugfix|^bug[[:space:]]fix|closes[[:space:]]#[0-9]+|fixes[[:space:]]#[0-9]+'
BUGFIX_BRANCH_PATTERN='^(bugfix|fix|bug)/'

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
    (.title | test("CVE-[0-9]{4}-[0-9]+"; "i") | not) and
    (.headRefName | test("^fix/cve-"; "i") | not)
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
      (.title | test("CVE-[0-9]{4}-[0-9]+"; "i") | not) and
      (.headRefName | test("^fix/cve-"; "i") | not)
    )
  ] | .[:$limit]' \
    "/tmp/guidance-gen/$REPO_SLUG/all-prs.json" \
    > "/tmp/guidance-gen/$REPO_SLUG/bugfix-meta.json"
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

# Save raw data to artifacts for reference
cp "/tmp/guidance-gen/$REPO_SLUG/cve-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/cve-prs.json"
cp "/tmp/guidance-gen/$REPO_SLUG/bugfix-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/bugfix-prs.json"
```

### 5. Synthesize Patterns

Read `cve-details.json` and `bugfix-details.json` from the artifacts.
Analyze them as the agent — do NOT write a script for this step.

**For each bucket, identify patterns across the PR records. Apply these rules:**

**Inclusion threshold**: Only include a rule if it appears in 3 or more PRs.
State the evidence count inline: `(8/9 merged PRs)`.

**What to extract:**

From merged PRs:
- **Title format**: What template do titles follow? Extract the pattern.
  Example: `Security: Fix CVE-YYYY-XXXXX (<package>)` or `fix(<scope>): <description>`
- **Branch format**: What naming pattern do branches use?
- **Files changed**: Which files appear together most often? Are there always-together groups?
- **Labels**: What labels are consistently applied?
- **Co-changes**: When package A changes, does package B always change too?
- **From changes_requested**: What did reviewers ask for that wasn't there? These are proactive rules.

From closed PRs:
- **close_reason + changes_requested**: Why was the PR closed/rejected? Each reason becomes a "don't".
- Look for patterns across multiple closed PRs — single-occurrence rejections are excluded.

**Output of synthesis step:**
Write an intermediate analysis file per bucket:

```
artifacts/guidance/<repo-slug>/analysis/cve-patterns.md
artifacts/guidance/<repo-slug>/analysis/bugfix-patterns.md
```

Each analysis file is a structured list:
```
TITLE_FORMAT: "Security: Fix CVE-YYYY-XXXXX (<package>)" (N/N merged)
BRANCH_FORMAT: "fix/cve-YYYY-XXXXX-<package>-attempt-N" (N/N merged)
FILES_GO_STDLIB: go.mod + Dockerfile + Dockerfile.konflux (N/N Go CVE PRs)
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

In auto mode, omit the `manual-selection` field:

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

# Push
git push origin "$BRANCH_NAME"
```

**Create PR using gh:**

```bash
# Count stats for PR body
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

PR_URL=$(gh pr create \
  --repo "$REPO" \
  --base "$(gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')" \
  --title "chore: add automated PR guidance files" \
  --body "$PR_BODY")

echo "PR created: $PR_URL"
```

**If PR creation fails** (no push access, auth issue), save the branch state and
report the error clearly. Tell the user to create the PR manually and provide the
branch name.

### 8. Cleanup

```bash
cd /
rm -rf "/tmp/guidance-gen/$REPO_SLUG"
echo "Cleaned up /tmp/guidance-gen/$REPO_SLUG"
```

### 9. Print Summary

```
Done.

Repository: https://github.com/<repo>
Analyzed:   <N> CVE PRs (<M> merged, <K> closed)
            <N> Bugfix PRs (<M> merged, <K> closed)
Rules:      <N> CVE rules, <M> bugfix rules (adaptive threshold applied)

Files generated:
  artifacts/guidance/<repo-slug>/output/cve-fix-guidance.md
  artifacts/guidance/<repo-slug>/output/bugfix-guidance.md

PR: <full URL>

Artifacts: artifacts/guidance/<repo-slug>/
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

- [ ] Both buckets filtered from PR metadata
- [ ] Per-PR details fetched (files + review REQUEST_CHANGES)
- [ ] Closed PRs have closing context fetched
- [ ] Patterns synthesized with 3-PR minimum applied
- [ ] Guidance files aim for ~80 lines (all threshold-passing rules included regardless)
- [ ] Files written to artifacts/output/
- [ ] PR created in target repo with correct files in .cve-fix/ and .bugfix/
- [ ] /tmp cleaned up
- [ ] PR URL printed to console

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
