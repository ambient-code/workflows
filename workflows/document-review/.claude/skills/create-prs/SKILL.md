---
name: create-prs
description: Create GitHub pull requests from automatable fix suggestions.
---

# Create Pull Requests Skill

You are creating GitHub pull requests from the fix suggestions produced by
the `/fix` phase. You read the self-contained fixes artifact, apply changes
to the target files, and create PRs using the suggested grouping.

## Your Role

Read `artifacts/document-review/fixes.md`, apply the fixes to the actual
documentation files, and create GitHub pull requests. Follow the PR grouping,
titles, descriptions, and automatable classifications exactly as specified
in the fixes file.

## Critical Rules

- **Fixes must exist.** If `artifacts/document-review/fixes.md` does not
  exist, inform the user and recommend running `/fix` first.
- **Follow the fixes file exactly.** Use the PR titles, descriptions, and
  groupings as specified. Do not regroup or re-prioritize.
- **Verify context before applying.** Before changing any text, confirm the
  Context block matches the current file contents. If context has drifted
  (file was modified since the review), skip that fix and report it.
- **Always create drafts.** Every PR must be created as a draft so a human
  reviewer can verify the changes before merging.
- **Skip non-automatable fixes.** Only apply fixes with `Automatable: Yes`.
  Skip any fix with `Automatable: No` and record it. If a PR group contains
  only non-automatable fixes, skip the entire PR.
- **One branch per PR.** Each PR group gets its own branch.
- **Do not force-push.** If a branch already exists, report the conflict
  and skip that PR.
- **Severity order.** Create PRs containing Critical fixes first, then High,
  then others.
- **Clean working tree.** Do not start if the working tree has uncommitted
  changes. Inform the user and stop.

## Process

### Step 1: Load the Fixes File

Read `artifacts/document-review/fixes.md`. Parse:

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
- Ensure the working tree is clean (no uncommitted changes) — if dirty, stop
  and ask the user to commit or stash
- Fetch the latest base branch:

```bash
git fetch origin <base-branch>
```

- Record the starting branch so you can return to it at the end

### Step 3: Create Each Pull Request

Process PR groups in severity order (highest-severity fixes first). For each
PR group:

#### 3a. Create a branch

```bash
git checkout -b docs/fix-<slug> origin/<base-branch>
```

Derive the slug from the PR title: lowercase, replace spaces and special
characters with hyphens, truncate to 50 characters. If the branch already
exists, skip this PR and record it as skipped.

#### 3b. Apply each fix

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

#### 3c. Commit

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

#### 3d. Push

```bash
git push -u origin docs/fix-<slug>
```

#### 3e. Create the PR

Use the title and description from the fixes file:

```bash
gh pr create --draft \
  --title "<PR title from fixes file>" \
  --body "$(cat <<'EOF'
<PR description from fixes file>

---

*Created by document-review workflow `/create-prs` phase.*
EOF
)" \
  --base <base-branch> \
  --head docs/fix-<slug>
```

#### 3f. Record the result

Note the PR URL, number of fixes applied, any skipped fixes, and whether it
was created as a draft.

#### 3g. Return to base

```bash
git checkout <starting-branch>
```

### Step 4: Write the PR Log

Follow the template at `templates/pr-log.md`. Write to
`artifacts/document-review/pr-log.md`.

## Output

- `artifacts/document-review/pr-log.md`
- GitHub pull requests (created on the remote)

## When This Phase Is Done

Report:

- Number of draft PRs created
- Total fixes applied across all PRs
- Fixes skipped (non-automatable, context drift, or branch conflicts)
- Links to all created PRs

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
