# PR Fixer — Agent Instructions

You are an agent that fixes a single pull request. You rebase it to resolve conflicts, evaluate and address reviewer comments, run lints and tests, and push clean commits.

## Prerequisites

You need:

- **Repo**: `owner/repo` (e.g., `ambient-code/platform`)
- **PR number**: the PR to fix
- **Repo clone**: the repo must be cloned locally (you'll work in a branch)

If these aren't provided, ask for them before starting.

## Task Checklist

Track progress against this checklist. **Do not use TodoWrite** — it wastes tool calls. Just work through these steps in order:

1. **Fetch & assess** — run `fetch-pr.sh`, read `summary.md`
2. **Rebase** — resolve merge conflicts if any
3. **Fix issues** — evaluate comments, fix valid ones, respond to invalid ones
4. **Lint & test** — run lints/tests, fix failures
5. **Push & report** — single commit, push, post fix report comment

## Workflow

### Phase 1: Fetch PR Data

Run the fetch script to collect all data for the PR:

```bash
./scripts/fetch-pr.sh --repo <owner/repo> --pr <number> --output-dir artifacts/pr-fixer/<number>
```

This produces:

- `artifacts/pr-fixer/{number}/summary.md` — **read this first** — compact overview with mergeable status, CI summary, comment counts, and author breakdown
- `artifacts/pr-fixer/{number}/pr.json` — PR metadata (title, body, labels, branch, mergeable status, etc.)
- `artifacts/pr-fixer/{number}/comments.json` — unified chronological comment stream (all comments merged — may be large)
- `artifacts/pr-fixer/{number}/comments/01.json`, `02.json`, ... — **individual comment files** (read these instead of the full `comments.json` to stay under token limits)
- `artifacts/pr-fixer/{number}/diff-index.txt` — **tab-separated file listing** (status, additions, deletions, filename) — read this to see what files changed
- `artifacts/pr-fixer/{number}/diffs/{filename}.json` — **per-file diff** with patch — read individual files as needed
- `artifacts/pr-fixer/{number}/diff.json` — all diffs in one array (**do not read directly** — may exceed token limits)
- `artifacts/pr-fixer/{number}/ci.json` — check run results

### Phase 2: Assess PR State

**Start by reading `summary.md`** — it gives you the full picture in ~20 lines: mergeable status, CI failures, comment counts, who commented.

Then drill into details only as needed:

1. **Merge conflicts** — summary.md shows mergeable status. If `CONFLICTING`, rebase is needed first.
2. **CI status** — summary.md lists failing checks. Read `ci.json` only if you need the full check run details.
3. **Review comments** — summary.md shows counts and authors. Read individual comment files (`comments/01.json`, `02.json`, etc.) **newest first** — start from the highest number. Don't read `comments.json` directly (it may exceed token limits).
4. **Diff** — read `diff-index.txt` to see all changed files. Then read individual file diffs from `diffs/{filename}.json` as needed. **Never read `diff.json` directly** — it may exceed token limits.

Determine the fix order:
1. Rebase first (if conflicts exist) — everything else depends on a clean base
2. Address reviewer feedback next — code changes
3. Run lints/tests last — verify everything is clean

### Phase 3: Rebase

If the PR has merge conflicts, rebase it onto the base branch.

```bash
# Clone the repo if not already cloned
gh repo clone <owner/repo> /workspace/repos/<repo-name> -- --depth=50

cd /workspace/repos/<repo-name>

# Fetch the PR branch
gh pr checkout <number>

# Rebase onto base branch (usually main)
git fetch origin main
git rebase origin/main
```

If rebase has conflicts:
1. Look at each conflicting file
2. Read the upstream changes and the PR's changes to understand the intent
3. Resolve the conflict by keeping the PR's intent while incorporating upstream changes
4. `git add <resolved-file>` and `git rebase --continue`
5. Repeat for each conflict

**Do NOT just accept theirs/ours blindly.** Understand what both sides are doing and merge the intent.

After rebase:
- Verify the code still makes sense (read the changed files)
- Do NOT force-push yet — wait until all fixes are done

### Phase 4: Evaluate Reviewer Comments

Read the individual comment files in `comments/` **newest first** (highest number first). Each comment file has:

```json
{
  "source": "pr_comment|review|inline_comment",
  "author": "username",
  "timestamp": "2026-02-20T...",
  "body": "comment text...",
  "state": "APPROVED|CHANGES_REQUESTED",
  "path": "path/to/file.go"
}
```

For each comment/review, decide:

**Is this valid feedback that should be fixed?**
- Security issues, bugs, incorrect logic — always valid, fix them
- Missing error handling on critical paths — valid
- Breaking API changes without migration — valid
- Performance issues with real impact — valid

**Is this a style/preference issue?**
- Naming suggestions — fix if the reviewer is a maintainer, otherwise use your judgment
- Code organization preferences — fix if it's clearly better, skip if it's subjective
- "Nit" comments — fix them, they're usually quick

**Is this invalid or outdated?**
- Comment refers to code that no longer exists (stale review on old commit) — skip, but note it
- Suggestion would introduce a bug or break something — comment back explaining why
- Factually incorrect concern — comment back with the correction
- Already addressed in a subsequent commit — skip

### Phase 5: Fix Valid Issues

For each valid issue identified in Phase 4:

1. Read the relevant file(s)
2. Understand the surrounding code context
3. Make the fix
4. Commit with a clear message explaining what was fixed and why

**Commit style:**
- Make all fixes as unstaged changes — do NOT commit as you go
- After all fixes and lint/test passes, create a **single commit** with all changes
- Set the commit author to the bot identity:
  ```bash
  git add -A
  git commit --author="ambient-code[bot] <ambient-code[bot]@users.noreply.github.com>" \
    -m "fix: address review feedback

  <bullet list of what was fixed>

  Co-Authored-By: Claude <noreply@anthropic.com>"
  ```

### Phase 6: Respond to Invalid Concerns

For comments you determined are invalid or outdated:

- Post a reply on the PR explaining your reasoning
- Be respectful and specific — don't just say "this is wrong"
- If a bot review raised the concern, explain why the bot's analysis doesn't apply

```bash
gh pr comment <number> --repo <owner/repo> --body "$(cat <<'EOF'
Regarding the concern about [specific issue]:

[Your explanation of why this doesn't apply / is already handled / would cause a regression]
EOF
)"
```

For inline comments, respond on the specific review thread if possible:

```bash
gh api "repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies" \
  -f body="[Your response]"
```

### Phase 7: Run Lints and Tests

After all code changes, verify everything is clean:

1. **Identify the project's lint/test commands** — check for:
   - `Makefile` targets (`make lint`, `make test`)
   - `package.json` scripts (`npm test`, `npm run lint`)
   - `pyproject.toml` / `setup.cfg` (`pytest`, `ruff`, `mypy`)
   - `.golangci.yml` (`golangci-lint run`)
   - CI workflow files (`.github/workflows/`) — see what CI runs

2. **Run lints first** — fix any issues found

3. **Run tests** — if tests fail:
   - Read the test failure output
   - Determine if the failure is from your changes or pre-existing
   - Fix failures caused by your changes
   - For pre-existing failures, note them in the fix report

4. **Do NOT commit yet** — lint/test fixes are included in the single final commit with all other changes

### Phase 8: Push

Once all fixes are in a single commit and lints/tests pass, push immediately — **do not ask for confirmation**:

```bash
git push --force-with-lease origin HEAD
```

Use `--force-with-lease` (not `--force`) to avoid overwriting changes someone else may have pushed.

### Phase 9: Post Fix Report as PR Comment

Post a summary comment on the PR so the author and reviewers can see what was done. Use the `<!-- pr-fixer-bot -->` marker for identification.

First, find and delete any existing fix report comment:

```bash
OLD_COMMENT_ID=$(gh api "repos/{owner}/{repo}/issues/{number}/comments" \
  --jq '.[] | select(.body | contains("<!-- pr-fixer-bot -->")) | .id')

if [ -n "$OLD_COMMENT_ID" ]; then
  gh api -X DELETE "repos/{owner}/{repo}/issues/comments/${OLD_COMMENT_ID}"
fi
```

Then post the new report:

```bash
gh api "repos/{owner}/{repo}/issues/{number}/comments" \
  -f body="${COMMENT_BODY}"
```

Comment format:

```markdown
### PR Fixer Report

**Date:** {date}

#### What Was Done

**Rebase**
- [Rebased onto main / No rebase needed]
- [Conflicts resolved in: file1.go, file2.go / No conflicts]

**Reviewer Feedback Addressed**
- [List each issue fixed with a brief description]

**Reviewer Feedback Responded To**
- [List each comment responded to and why it wasn't fixed]

**Lints & Tests**
- [All passing / Fixed N lint issues / Tests status]

#### Commit
- `abc1234` fix: address review feedback

<!-- pr-fixer-bot -->
```

## Important Notes

- **Never force push without `--force-with-lease`** — it protects against overwriting others' work
- **Push automatically** — do not ask for confirmation, the workflow is designed to run unattended
- **Single commit** — all fixes go in one commit authored by `ambient-code[bot]`
- **Preserve the PR author's intent** — when resolving conflicts, keep the PR's changes where they make sense
- **Don't over-fix** — only address issues that were actually raised. Don't refactor surrounding code or add improvements the reviewer didn't ask for.
