---
name: create-prs
description: Create GitHub pull requests from automatable fix suggestions.
---

# Create Pull Requests Skill

You are creating GitHub pull requests from the fix suggestions produced by
the `/fix` phase. You read the self-contained fixes artifact, apply changes
to the target files, and create PRs using the suggested grouping.

## Your Role

Read `artifacts/fixes.md`, apply the fixes to the actual
documentation files, and create GitHub pull requests. Follow the PR grouping,
titles, descriptions, and automatable classifications exactly as specified
in the fixes file.

## Critical Rules

- **Fixes must exist.** If `artifacts/fixes.md` does not
  exist, inform the user and recommend running `/fix` first.
- **Follow the fixes file exactly.** Use the PR titles, descriptions, and
  groupings as specified. Do not regroup or re-prioritize.
- **Verify context before applying.** Before changing any text, confirm the
  Context block matches the current file contents. If context has drifted
  (file was modified since the review), skip that fix and report it.
- **Create PRs in ready state.** PRs are created as ready for review so
  reviewers are notified and the feedback loop starts immediately.
- **Skip non-automatable fixes.** Only apply fixes with `Automatable: Yes`.
  Skip any fix with `Automatable: No` and record it. If a PR group contains
  only non-automatable fixes, skip the entire PR.
- **One branch per PR.** Each PR group gets its own branch.
- **Idempotent execution.** Before processing any PR groups, snapshot all
  open PRs by the current user in the repository (see Step 2). For each PR
  group, search the snapshot for PRs with overlapping titles or
  descriptions. For any potential matches, compare the PR's diff (saved
  locally during Step 2) against the planned fixes. If the diff already addresses the
  same changes, skip the PR group and record it as "already exists". This
  makes `/create-prs` safe to run multiple times without creating
  duplicates.
- **Do not force-push.** If a branch already exists and has no matching
  open PR, report the conflict and skip that PR.
- **Severity order.** Create PRs containing Critical fixes first, then High,
  then others.
- **Clean working tree.** Do not start if the working tree has uncommitted
  changes. Inform the user and stop.
- **Attribution required.** Every commit must use `-s` for Signed-off-by and
  include a `Co-Authored-By` trailer with the current model name.

## Process

### Step 1: Load the Fixes File

Read `artifacts/fixes.md`. Parse:

- Repository metadata (URL, base branch, base commit)
- All PR groups with their fixes, titles, and descriptions
- Automatable status for each PR and fix

If the file does not exist or is empty, stop and inform the user.

### Step 2: Verify Repository State

Confirm the repository is ready:

```bash
git remote get-url origin 2>/dev/null
git rev-parse --abbrev-ref HEAD 2>/dev/null
git status --porcelain
```

- Verify the remote URL matches the fixes file's **Repository** field
- Verify write access to the repository:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
scripts/check-gh-write-access.sh "$REPO"
```

If the check fails, stop and inform the user — this skill requires write
access to push branches, create PRs, and manage labels.

- Ensure the working tree is clean (no uncommitted changes) — if dirty, stop
  and ask the user to commit or stash
- Fetch the latest base branch:

```bash
git fetch origin <base-branch>
```

- Record the starting branch so you can return to it at the end
- Read the repository's `CONTRIBUTING.md` (if it exists) and note any PR
  requirements — title conventions, commit message format, branch naming,
  required labels, sign-off rules, etc. Apply these conventions when
  creating branches, commits, and PRs in Step 3. If `CONTRIBUTING.md` does
  not exist, use the defaults defined in this skill.
- Snapshot all open PRs by the current user for duplicate detection:

```bash
gh pr list --author "@me" --state open --json number,title,body,headRefName \
  > artifacts/tmp/existing-prs.json
```

Then fetch the diff for each open PR so all data is available locally:

```bash
for pr in $(jq -r '.[].number' artifacts/tmp/existing-prs.json); do
  gh pr diff "$pr" > "artifacts/tmp/pr-${pr}.diff"
done
```

These snapshots are used in Step 3 to detect duplicates before creating each PR.

- Ensure the `acp:document-review` label exists in the repository:

```bash
gh label create "acp:document-review" --description "Created by the document-review workflow" --color "1D76DB" 2>/dev/null || true
```

If label creation fails for permission reasons, continue without the label
and note it in the PR log.

### Step 3: Create Each Pull Request

Process PR groups in severity order (highest-severity fixes first). For each
PR group:

#### 3a. Check for duplicate PRs

Read `artifacts/tmp/existing-prs.json` and search for PRs with overlapping
titles or descriptions. For any potential match, read its diff from
`artifacts/tmp/pr-<number>.diff` and compare it against the fixes planned
for this PR group. If the existing PR already addresses the same changes,
skip this PR group and record it as "already exists" with a reference to
the existing PR number.

#### 3b. Create a branch

```bash
git checkout -b docs/fix-<slug> origin/<base-branch>
```

Derive the slug from the PR title: lowercase, replace spaces and special
characters with hyphens, truncate to 50 characters. If the branch already
exists, skip this PR and record it as skipped.

#### 3c. Apply each fix

For each fix in the PR group:

1. **Read** the target file
2. **Locate** the text using the Context block — search for the surrounding
   lines and find the target between `>>>` and `<<<` markers
3. **Verify** the Current text exists at that location. If it does not match
   (context drift), skip this fix and record the reason
4. If the fix is `Automatable: No`, skip it and record the reason
5. **Apply** the change — replace the Current text with the Replacement

If all fixes in a PR group are skipped (non-automatable or context drift),
delete the branch and skip the PR entirely:

```bash
git checkout <base-branch>
git branch -D docs/fix-<slug>
```

#### 3d. Commit

Stage and commit the changes:

```bash
git add <changed-files>
git commit -s -m "$(cat <<'EOF'
<commit message summarizing the fixes>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Use a commit message that summarizes the fixes applied. For multi-fix PRs,
list each fix briefly.

#### 3e. Push

```bash
git push -u origin docs/fix-<slug>
```

#### 3f. Create the PR

Use the title and description from the fixes file:

```bash
gh pr create \
  --title "<PR title from fixes file>" \
  --body "$(cat <<'EOF'
<PR description from fixes file>

---

*Created by document-review workflow `/create-prs` phase.*
EOF
)" \
  --label "acp:document-review" \
  --base <base-branch> \
  --head docs/fix-<slug>
```

#### 3g. Record the result

Note the PR URL, number of fixes applied, any skipped fixes, and whether it
was created.

#### 3h. Return to base

```bash
git checkout <starting-branch>
```

### Step 4: Write the PR Log

Follow the template at `templates/pr-log.md`. Write to
`artifacts/pr-log.md`.

### Step 5: Update the Report with PR Links

If `artifacts/report.md` exists, update it by adding a **PR** field to each
finding that was addressed by a created PR.

For each PR that was successfully created, match its fixes back to report
findings by comparing the file path and issue description. When a match is
found, add a **PR** field to that finding with the PR link:

```markdown
- **PR:** [#N](url)
```

Insert the **PR** field after the **Fix** field (or after **Evidence** if
there is no **Fix** field). If a finding was not addressed by any PR, leave
it unchanged.

## Output

- `artifacts/pr-log.md`
- `artifacts/report.md` (updated with PR links, if it existed)
- GitHub pull requests (created on the remote)

## When This Phase Is Done

Report:

- Number of PRs created
- Total fixes applied across all PRs
- Fixes skipped (non-automatable, context drift, or branch conflicts)
- Links to all created PRs

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
