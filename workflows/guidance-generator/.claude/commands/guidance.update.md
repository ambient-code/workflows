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
/guidance.update <repo-url>
```

- `repo-url`: Full GitHub URL or `org/repo` slug

## Process

### 1. Parse Arguments and Validate

```bash
gh auth status || { echo "ERROR: gh not authenticated. Run 'gh auth login'"; exit 1; }

gh repo view "$REPO" --json name > /dev/null 2>&1 || {
  echo "ERROR: Cannot access $REPO"
  exit 1
}

REPO_SLUG=$(echo "$REPO" | tr '/' '-')
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

if [ -f "$CVE_FILE" ]; then
  FOUND_CVE=true
  # Extract date from: <!-- last-analyzed: YYYY-MM-DD | ... -->
  CVE_DATE=$(grep -m1 'last-analyzed:' "$CVE_FILE" | \
    grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  echo "  .cve-fix/examples.md — last analyzed: ${CVE_DATE:-unknown}"
  LAST_DATE="$CVE_DATE"
fi

if [ -f "$BUGFIX_FILE" ]; then
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

### 3. Fetch New PRs Since Last Analysis (Pass 1)

```bash
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
```

### 4. Filter New PRs into Buckets

Apply the same filters as `/guidance.generate`:

```bash
# CVE bucket
jq '[
  .[] | select(
    (.title | test("CVE-[0-9]{4}-[0-9]+|^[Ss]ecurity:|^fix\\(cve\\):|^Fix CVE"; "i")) or
    (.headRefName | test("^fix/cve-|^security/cve-"; "i"))
  )
]' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json"

# Bugfix bucket (excluding CVE)
jq '[
  .[] | select(
    (
      (.title | test("^fix[:(]|^bugfix|^bug[[:space:]]fix|closes[[:space:]]#[0-9]+|fixes[[:space:]]#[0-9]+"; "i")) or
      (.headRefName | test("^(bugfix|fix|bug)/"; "i"))
    ) and
    (.title | test("CVE-[0-9]{4}-[0-9]+"; "i") | not) and
    (.headRefName | test("^fix/cve-"; "i") | not)
  )
]' "/tmp/guidance-gen/$REPO_SLUG/new-all-prs.json" \
  > "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json"

NEW_CVE=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json")
NEW_BUGFIX=$(jq 'length' "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json")
echo "  CVE bucket: $NEW_CVE new PRs"
echo "  Bugfix bucket: $NEW_BUGFIX new PRs"
```

### 5. Fetch Per-PR Details (Pass 2)

Same as `/guidance.generate` — files + reviews per PR, closing context for closed PRs.

```bash
fetch_pr_details() {
  local META_FILE="$1"
  local OUT_FILE="$2"
  local COUNT=$(jq 'length' "$META_FILE")

  echo "[]" > "$OUT_FILE"

  for i in $(seq 0 $((COUNT - 1))); do
    NUMBER=$(jq -r ".[$i].number" "$META_FILE")
    STATE=$(jq -r ".[$i].state" "$META_FILE")
    TITLE=$(jq -r ".[$i].title" "$META_FILE")
    BRANCH=$(jq -r ".[$i].headRefName" "$META_FILE")
    LABELS=$(jq -c "[.[$i].labels[].name]" "$META_FILE")

    PR_DETAIL=$(gh pr view "$NUMBER" --repo "$REPO" \
      --json files,reviews 2>/dev/null)

    FILES=$(echo "$PR_DETAIL" | jq -c '[.files[].path]')
    CHANGES_REQ=$(echo "$PR_DETAIL" | jq -c '[
      .reviews[] |
      select(.state == "CHANGES_REQUESTED") |
      .body | gsub("\\n"; " ") | .[0:200]
    ]')

    CLOSE_REASON="null"
    if [ "$STATE" = "CLOSED" ]; then
      CLOSE_REASON=$(gh pr view "$NUMBER" --repo "$REPO" \
        --json comments \
        --jq '.comments | .[-2:] | map(.body | gsub("\\n"; " ") | .[0:200]) | join(" | ")' \
        2>/dev/null | jq -Rs '.')
    fi

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
        changes_requested: $changes_requested, close_reason: $close_reason}')

    jq --argjson rec "$RECORD" '. + [$rec]' "$OUT_FILE" > "${OUT_FILE}.tmp" \
      && mv "${OUT_FILE}.tmp" "$OUT_FILE"
  done
}

fetch_pr_details \
  "/tmp/guidance-gen/$REPO_SLUG/new-cve-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/new-cve-details.json"

fetch_pr_details \
  "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-meta.json" \
  "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details.json"

cp "/tmp/guidance-gen/$REPO_SLUG/new-cve-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/new-cve-prs.json"
cp "/tmp/guidance-gen/$REPO_SLUG/new-bugfix-details.json" \
   "artifacts/guidance/$REPO_SLUG/raw/new-bugfix-prs.json"
```

### 6. Synthesize New Patterns

Read both the new PR detail files AND the existing guidance files.

As the agent, analyze the new PR data for patterns. For each pattern found:

**A. New rule** — a pattern seen in 3+ of the new PRs that does not already
exist in the guidance file. Add it to the appropriate section.

**B. Reinforced rule** — a pattern that already exists in the guidance file.
Update its evidence count. For example: `(8/9 merged)` → `(14/15 merged)`.

**C. Contradicting rule** — a pattern in new merged PRs that directly contradicts
a "don't" in the existing guidance file (e.g., a merged PR combined two CVEs despite
the guidance saying not to). Flag this with a comment in the guidance file:
```
- [REVIEW NEEDED] Multiple CVEs per PR — previously flagged as a don't,
  but PR #N was merged combining CVEs. Policy may have changed. (N/N new merged)
```

**D. New don't** — a pattern from newly closed PRs (3+ cases) not already in the
don'ts section. Add it.

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

After editing, verify the file is still under 80 lines. If adding new rules
would push it over 80 lines, prioritize: keep all don'ts, keep rules with
highest evidence counts, drop rules with lowest counts (below 5%).

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

### 9. Cleanup

```bash
cd /
rm -rf "/tmp/guidance-gen/$REPO_SLUG"
```

### 10. Print Summary

```
Done.

Repository:  https://github.com/<repo>
New PRs:     <N> CVE PRs, <M> bugfix PRs (since <last-date>)
Changes:     <N> new rules, <M> counts updated, <K> contradictions flagged

PR: <full URL>

Artifacts: artifacts/guidance/<repo-slug>/
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

- [ ] Existing guidance files found and last-analyzed date extracted
- [ ] New PRs fetched since last-analyzed date
- [ ] Per-PR details fetched for new PRs
- [ ] New patterns synthesized (new rules, updated counts, contradictions flagged)
- [ ] Existing files updated in-place (no rewrites, structure preserved)
- [ ] Both files remain under 80 lines
- [ ] Header timestamps updated
- [ ] PR created in target repo
- [ ] /tmp cleaned up
- [ ] PR URL printed to console

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
