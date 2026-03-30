---
name: pr
description: Create a pull request from the current branch. Use this instead of running gh pr create directly — it detects GitHub App vs user auth, finds or creates forks, syncs workflow files, detects the upstream default branch, and falls back to compare URLs when API access is limited.
---

# Create Pull Request Skill

## Dispatch

If you were dispatched by the controller or by speedrun, continue below.
Otherwise, read `.claude/skills/controller/SKILL.md` first — it will send
you back here with the proper workflow context.

---

You are preparing to submit a bug fix as a pull request. This skill provides a
systematic, failure-resistant process for getting code from the working directory
into a PR. It handles the common obstacles: authentication, fork workflows,
remote configuration, and cross-repo PR creation.

## IMPORTANT: Follow This Skill Exactly

This skill exists because ad-hoc PR creation fails in predictable ways.
**Do not improvise.** Follow the numbered steps in order. Do not skip steps.
Do not invent alternative approaches when a step fails — use the documented
fallback ladder at the bottom of this file.

## Your Role

Get the bug fix changes submitted as a draft pull request. Handle the full
git workflow: branch, commit, push, and PR creation. When steps fail, follow
the documented recovery paths instead of guessing.

## Critical Rules

- **Never ask the user for git credentials.** Use `gh auth status` to check.
- **Never push directly to upstream.** Always use a fork remote. This applies
  even if you are authenticated as an org bot or app — do not assume any
  account has push access to upstream. Always go through a fork.
- **Never skip pre-flight checks.** They prevent every common failure.
- **Always create a draft PR.** Let the author mark it ready after review.
- **Always work in the project repo directory**, not the workflow directory.
- **Never attempt `gh repo fork` without asking the user first.**
- **Never fall back to patch files without exhausting all other options.**

## Process

### Placeholders Used in This Skill

These are determined during pre-flight checks. Record each value as you go.

| Placeholder | Source | Example |
| --- | --- | --- |
| `AUTH_TYPE` | Step 0: `gh auth status` + `gh api user` | `user-token` / `github-app` / `none` |
| `GH_USER` | Step 0: `gh api user` or `/installation/repositories` (for bots) | `jsmith` |
| `UPSTREAM_OWNER/REPO` | Step 2c: `gh repo view --json nameWithOwner` | `acme/myproject` |
| `DEFAULT_BRANCH` | Step 2c: detected from upstream repo | `main` / `dev` / `master` |
| `UPSTREAM_REMOTE` | Step 2b: the git remote name pointing to the upstream org | `origin` / `upstream` |
| `FORK_OWNER` | Step 3: owner portion of fork's `nameWithOwner`, or `GH_USER` if newly created | `jsmith` |
| `FORK_REMOTE` | Step 4: the git remote name pointing to the fork | `fork` / `origin` |
| `REPO` | The repository name (without owner) | `myproject` |
| `BRANCH_NAME` | Step 5: the branch you create | `bugfix/issue-42-null-check` |

### Step 0: Determine Auth Context

Run this FIRST, before any other work. The auth type determines the entire
flow — if you skip this, every subsequent step will use the wrong strategy.

```bash
gh auth status
```

Then determine your identity:

```bash
# Works for normal user tokens:
gh api user --jq .login 2>/dev/null

# If that fails (403), you're running as a GitHub App/bot.
# Get the real user from the app installation:
gh api /installation/repositories --jq '.repositories[0].owner.login'
```

The `/installation/repositories` endpoint works because GitHub Apps are
installed on user accounts — the repo owner is the actual user.

Record `GH_USER` and `AUTH_TYPE`:

- If `gh api user` succeeded: `AUTH_TYPE` = `user-token`, `GH_USER` = the login
- If `gh api user` failed but `/installation/repositories` worked:
  `AUTH_TYPE` = `github-app`, `GH_USER` = the repo owner login
- If `gh auth status` itself failed: try recovering from an expired token
  (see below). If recovery fails: `AUTH_TYPE` = `none`

**Recovering from expired tokens:** Platform sessions often start with a
`GITHUB_TOKEN` env var that can expire mid-session. The `refresh_credentials`
MCP tool refreshes the backend but does NOT update the shell env var. If
`gh auth status` fails, check for a git credential helper:

```bash
git config --global credential.helper 2>/dev/null
```

If a credential helper exists (e.g., `/tmp/git-credential-ambient`), query it
for a fresh token:

```bash
FRESH_TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null | grep '^password=' | cut -d= -f2)
```

If that returns a token, export it and re-check auth:

```bash
export GITHUB_TOKEN="$FRESH_TOKEN"
gh auth status
```

**Important:** Each shell invocation gets a fresh environment, so you must
prepend the export to every subsequent `gh` command, or write the token to
`~/.config/gh/hosts.yml` so `gh` picks it up natively:

```bash
gh auth login --with-token <<< "$FRESH_TOKEN"
```

The `gh auth login` approach is preferred — it persists for all subsequent
`gh` commands without per-command exports. After recovery, re-run the identity
checks above to set `AUTH_TYPE` and `GH_USER`.

### Step 1: Locate the Project Repository

The bugfix workflow runs from the workflow directory, but the code changes live
in the project repository. Before doing any git work:

```bash
# Find the project repo — it's typically in /workspace/repos/ or an add_dirs path
ls /workspace/repos/ 2>/dev/null || ls /workspace/artifacts/ 2>/dev/null
```

`cd` into the project repo directory before proceeding. All subsequent git
commands run from there.

If the user provides a path or the repo is obvious from session context
(prior commands, artifacts), use that directly.

### Step 2: Pre-flight Checks

Run ALL of these before doing anything else. Do not skip any.

**2a. Check git configuration:**

```bash
git config user.name
git config user.email
```

- If both are set: proceed.
- If missing and `gh` is authenticated: set them using `GH_USER` from Step 0:

```bash
git config user.name "GH_USER"
git config user.email "GH_USER@users.noreply.github.com"
```

- If missing and `gh` is NOT authenticated: set reasonable defaults so commits
  work. Use `"bugfix-workflow"` / `"bugfix@workflow.local"` as placeholders.

**2b. Inventory existing remotes:**

```bash
git remote -v
```

Note which remote points to the upstream repo and which (if any) points to
the user's fork. Common patterns:

| Remote Name | URL Contains | Likely Role |
| --- | --- | --- |
| `origin` | upstream org | Upstream (read-only) |
| `origin` | user's name | Fork (read-write) |
| `fork` | user's name | Fork (read-write) |
| `upstream` | upstream org | Upstream (read-only) |

**2c. Identify the upstream repo and its default branch:**

If `gh` is authenticated:

```bash
gh repo view --json nameWithOwner,defaultBranchRef --jq '{nameWithOwner, defaultBranch: .defaultBranchRef.name}'
```

This returns both the repo name and its default branch. Record
`UPSTREAM_OWNER/REPO` and `DEFAULT_BRANCH` from the output.

If `gh` is NOT authenticated, extract from the upstream remote (identified in
Step 2b as `UPSTREAM_REMOTE`):

```bash
# Repo name (use UPSTREAM_REMOTE, not necessarily origin — origin may be the fork)
git remote get-url UPSTREAM_REMOTE | sed -E 's#.*/([^/]+/[^/]+?)(\.git)?$#\1#'

# Default branch
git remote show UPSTREAM_REMOTE 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}'
```

Record the results as `UPSTREAM_OWNER/REPO` and `DEFAULT_BRANCH`.

**Do not assume the default branch is `main`.** Many projects use `dev`,
`master`, `develop`, or other branch names. All subsequent steps that
reference the base branch MUST use `DEFAULT_BRANCH`.

**2d. Check current branch and changes:**

```bash
git status
git diff --stat
```

Confirm there are actual changes to commit. If there are no changes, stop
and tell the user.

### Step 2e: Pre-flight Gate (REQUIRED)

**Do not proceed to Step 3 until you have printed the following filled-in
table.** Every row must have a value or an explicit "unknown". If you cannot
fill in a row, that itself is important information that determines the flow.

```text
Pre-flight summary:
| Placeholder          | Value              |
| -------------------- | ------------------ |
| AUTH_TYPE             | ___                |
| GH_USER              | ___                |
| UPSTREAM_OWNER/REPO  | ___                |
| DEFAULT_BRANCH       | ___                |
| UPSTREAM_REMOTE      | ___                |
| EXISTING_REMOTES     | ___                |
| HAS_CHANGES          | yes / no           |
| CURRENT_BRANCH       | ___                |
```

### Expected Flow by Auth Type

Now that you know `AUTH_TYPE`, here is what to expect for the rest of this
skill. Read the row that matches your `AUTH_TYPE` so you are prepared for
expected failures instead of surprised by them.

**`user-token`:** Fork check → push to fork → `gh pr create` → done.
This is the happy path.

**`github-app`:** Fork check → push to fork → `gh pr create` MAY fail
with "Resource not accessible by integration" (this is expected when the
bot is installed on the user's account, not the upstream org). If it fails,
provide the user a pre-filled compare URL (Step 8 fallback / Rung 2). Some
repos grant the app sufficient permissions, so always try `gh pr create`
first.

**`none`:** You cannot push or create PRs. Stop and ask the user (see below),
then prepare the branch and PR description for them to submit manually.

---

**If `AUTH_TYPE` is `none` — STOP and ask the user.** Present their
options clearly:

> GitHub CLI authentication is not available in this environment, which means
> I can't push branches or create PRs directly.
>
> I can still prepare everything (branch, commit, PR description). To get it
> submitted, you have a few options:
>
> 1. **Set up `gh auth`** in this environment (`gh auth login`) and I'll
>    handle the rest
> 2. **Tell me your fork URL** if you already have one — I may be able to
>    push to it
> 3. **I'll prepare the branch and PR description**, and give you the exact
>    commands to push and create the PR from your own machine
>
> Which would you prefer?

**Wait for the user to respond.** Then proceed accordingly:

- Option 1: User sets up auth → re-run Step 0, continue normally
- Option 2: User provides fork → set `FORK_OWNER` from it, skip to Step 4
- Option 3: Continue through Steps 5–6 (branch, commit, PR description) but
  skip Steps 7–8 (push, PR creation). At the end, provide the user with
  the exact push and PR creation commands — but only ONE set of clear
  instructions, not a wall of text

**If `AUTH_TYPE` is `user-token` or `github-app`:** Continue to Step 3.
Do NOT skip Step 3 based on the account type — even org bots and GitHub
Apps need a fork.

### Step 3: Ensure a Fork Exists

You almost certainly do NOT have push access to the upstream repo. Use a fork.

**Determining FORK_OWNER:** The fork owner is almost always `GH_USER` (the
authenticated GitHub username from Step 0). When the `gh repo list` command
below returns a fork, its `nameWithOwner` will be in `FORK_OWNER/REPO` format —
use the owner portion. If the user creates a new fork, `FORK_OWNER` = `GH_USER`.

**Check if the user has a fork:**

```bash
gh repo list GH_USER --fork --json nameWithOwner,parent --jq '.[] | select(.parent.owner.login == "UPSTREAM_OWNER" and .parent.name == "REPO") | .nameWithOwner'
```

Replace `GH_USER` with the value from Step 0. Replace `UPSTREAM_OWNER` and
`REPO` with the two parts of `UPSTREAM_OWNER/REPO` from Step 2c (e.g., for
`acme/myproject`, use `UPSTREAM_OWNER` = `acme` and `REPO` = `myproject`).

**Note:** The GitHub API returns the parent as separate `.parent.owner.login`
and `.parent.name` fields — it does NOT have a `.parent.nameWithOwner` field.

The output will be `FORK_OWNER/REPO` (e.g., `jsmith/myproject`). Record
the owner portion as `FORK_OWNER`.

**If a fork exists:** use it — skip ahead to Step 4.

**If NO fork exists — HARD STOP.** You cannot continue without a fork.
Do not try to push to upstream. Do not create a patch file. Do not try
API workarounds. Ask the user:

> I don't see a fork of `UPSTREAM_OWNER/REPO` under your GitHub account
> (`GH_USER`). I need a fork to push the branch and create a PR.
>
> Would you like me to try creating one? If that doesn't work in this
> environment, you can create one yourself at:
> `https://github.com/UPSTREAM_OWNER/REPO/fork`
>
> Let me know when you're ready and I'll continue.

**Then stop. Do not proceed until the user responds.**

Once the user confirms, try creating the fork:

```bash
gh repo fork UPSTREAM_OWNER/REPO --clone=false
```

- If this succeeds: continue to Step 4.
- If this fails (sandbox/permission issue): tell the user to create the fork
  manually using the URL above. **Stop again and wait for the user to confirm
  the fork exists before continuing.**

Do not proceed to Step 4 until a fork actually exists and you have confirmed
it with:

```bash
gh repo view GH_USER/REPO --json nameWithOwner --jq .nameWithOwner
```

### Step 4: Configure the Fork Remote

Once a fork exists (or was found), ensure there's a git remote pointing to it.

```bash
# Check if fork remote already exists
git remote -v | grep FORK_OWNER
```

If not present, add it:

```bash
git remote add fork https://github.com/FORK_OWNER/REPO.git
```

**Set `FORK_REMOTE`** based on what you find:

- If you just added a remote named `fork` → `FORK_REMOTE` = `fork`
- If `origin` already points to the fork (URL contains `FORK_OWNER`) →
  `FORK_REMOTE` = `origin`
- If another existing remote points to the fork → `FORK_REMOTE` = that name

Record `FORK_REMOTE` now. **Use it in all subsequent commands** (push, fetch,
ls-remote) instead of hardcoding `fork` or `origin`.

### Step 4a: Check Fork Sync Status

**Why this check exists:** When a user's fork is out of sync with upstream,
particularly when upstream has added workflow files (`.github/workflows/`) that
don't exist in the fork, pushing a feature branch can fail with a confusing
error like:

```
refusing to allow a GitHub App to create or update workflow `.github/workflows/foo.yml` without `workflows` permission
```

This happens because GitHub sees the push as "creating" workflow files (from
the fork's perspective), even though the feature branch simply includes files
that already exist in upstream. The GitHub App typically doesn't have `workflows`
permission by design.

**Detection:**

```bash
# Fetch both the fork and the upstream remote (identified in Step 2b)
git fetch FORK_REMOTE
git fetch UPSTREAM_REMOTE

# Compare fork's DEFAULT_BRANCH against upstream's DEFAULT_BRANCH
# (don't rely on the local branch — it may be stale)
WORKFLOW_DIFF=$(git diff --name-only FORK_REMOTE/DEFAULT_BRANCH..UPSTREAM_REMOTE/DEFAULT_BRANCH -- .github/workflows/ 2>/dev/null)

if [ -n "$WORKFLOW_DIFF" ]; then
  echo "Fork is out of sync with upstream (workflow files differ):"
  echo "$WORKFLOW_DIFF"
fi
```

`UPSTREAM_REMOTE` is whichever remote was identified as pointing to the
upstream org in Step 2b (typically `origin` when origin is the upstream repo,
or `upstream` if the user added it separately).

**If workflow differences exist — attempt automated sync:**

```bash
# Try to sync the fork's default branch with upstream
gh api --method POST repos/FORK_OWNER/REPO/merge-upstream -f branch=DEFAULT_BRANCH
```

- If this succeeds: fetch the fork again (`git fetch FORK_REMOTE`) and continue
- If this fails (usually due to workflow permission restrictions): guide the
  user to sync manually

**If automated sync fails — STOP and guide the user:**

> Your fork is out of sync with upstream and contains workflow file differences.
> This prevents me from pushing because GitHub would interpret it as creating
> workflow files, which requires special permissions.
>
> Please sync your fork by either:
>
> 1. **Via GitHub web UI:** Visit https://github.com/FORK_OWNER/REPO and click
>    "Sync fork" → "Update branch"
>
> 2. **Via command line** (may require `gh auth refresh -s workflow` first):
>    ```
>    gh repo sync FORK_OWNER/REPO --branch DEFAULT_BRANCH
>    ```
>
> Let me know when the sync is complete and I'll continue with the PR.

**After user confirms sync — rebase and continue:**

```bash
# Fetch the updated fork
git fetch FORK_REMOTE

# Update local DEFAULT_BRANCH before creating the feature branch
git checkout DEFAULT_BRANCH
git rebase FORK_REMOTE/DEFAULT_BRANCH

# Continue to Step 5 (create feature branch from updated DEFAULT_BRANCH)
```

### Step 5: Create a Branch

```bash
git checkout -b BRANCH_NAME
```

Branch naming conventions:

- `bugfix/issue-NUMBER-SHORT_DESCRIPTION` if there's an issue number
- `bugfix/SHORT_DESCRIPTION` if there's no issue number
- Use kebab-case, keep it under 50 characters

If a branch already exists with the changes (from a prior `/fix` phase), use
it instead of creating a new one.

### Step 6: Stage and Commit

Stage changes selectively (`git add path/to/files`, not `git add .`), review
with `git status`, then commit using conventional commit format:

```bash
git commit -m "fix(SCOPE): SHORT_DESCRIPTION

DETAILED_DESCRIPTION

Fixes #ISSUE_NUMBER"
```

Use prior artifacts (root cause analysis, implementation notes) to write an
accurate commit message. Don't make up details.

**Include the PR description in the commit body.** When a PR has a single
commit, GitHub auto-fills the PR description from the commit message. This
ensures the PR form is pre-populated even when `gh pr create` fails (a
common case for bot environments). If `artifacts/bugfix/docs/pr-description.md`
exists, append its content after the `Fixes #N` line. If it doesn't exist,
compose a brief PR body from session context (problem, root cause, fix, testing)
and include that instead.

### Step 7: Push to Fork

```bash
# Ensure git uses gh for authentication
gh auth setup-git

# Push the branch (use FORK_REMOTE from Step 4)
git push -u FORK_REMOTE BRANCH_NAME
```

**If this fails:**

- **Authentication / credential error**: Verify `gh auth status` succeeds and
  that `gh auth setup-git` ran without errors. The user may need to
  re-authenticate or the sandbox may be blocking network access.
- **Remote not found**: Verify the fork remote URL is correct.
- **Permission denied**: The fork remote may be pointing to upstream, not the
  actual fork. Verify with `git remote get-url FORK_REMOTE`.

### Step 8: Create the Draft PR

**Important context on bot permissions:** If you are running as a GitHub App
bot (e.g., `ambient-code[bot]`), `gh pr create --repo UPSTREAM_OWNER/REPO`
may fail with `Resource not accessible by integration`. This happens when the
bot is installed on the **user's** account but not the upstream org. Some repos
grant the app sufficient permissions, so always try `gh pr create` first —
but if it fails with a 403, this is expected. Do not debug further; go
directly to the fallback below.

**Try `gh pr create` first** (works for user tokens; may also work for bots
on some repos):

```bash
gh pr create \
  --draft \
  --repo UPSTREAM_OWNER/REPO \
  --head FORK_OWNER:BRANCH_NAME \
  --base DEFAULT_BRANCH \
  --title "fix(SCOPE): SHORT_DESCRIPTION" \
  --body-file artifacts/bugfix/docs/pr-description.md
```

`--head` must be `FORK_OWNER:BRANCH_NAME` format (with the owner prefix) for
cross-fork PRs. If `--body-file` doesn't exist, use `--body` with content
composed from session artifacts.

**If `gh pr create` fails (403, "Resource not accessible by integration", etc.):**

This is a common and expected outcome when running as a GitHub App bot.
Do NOT retry, do NOT debug further, do NOT fall back to a patch file. Instead:

1. **Write the PR description** to `artifacts/bugfix/docs/pr-description.md`
   (if not already written).

2. **Give the user a pre-filled GitHub compare URL** with `title` and `body`
   query parameters so the PR form opens fully populated:

   ```text
   https://github.com/UPSTREAM_OWNER/REPO/compare/DEFAULT_BRANCH...FORK_OWNER:BRANCH_NAME?expand=1&title=URL_ENCODED_TITLE&body=URL_ENCODED_BODY
   ```

   URL-encode the title and body. If the encoded URL would exceed ~8KB
   (browser limit), omit the `body` parameter — the commit message body
   from Step 6 will still auto-fill the description for single-commit PRs.

3. **Remind the user** to check "Create draft pull request" if they want
   it as a draft.

4. **Provide clone-and-checkout commands** so the user can test locally:

   ```text
   ## Test the branch locally

   # Fresh clone:
   git clone https://github.com/FORK_OWNER/REPO.git
   cd REPO
   git checkout BRANCH_NAME

   # Or if you already have the repo cloned:
   git remote add fork https://github.com/FORK_OWNER/REPO.git   # if not already added
   git fetch fork BRANCH_NAME
   git checkout -b BRANCH_NAME fork/BRANCH_NAME
   ```

**If "branch not found"**: The push in Step 7 may have failed silently.
Verify with `git ls-remote FORK_REMOTE BRANCH_NAME`.

### Step 9: Confirm and Report

After the PR is created (or the URL is provided), summarize:

- PR URL (or manual creation URL with pre-filled title and body)
- What was included in the PR
- What branch it targets
- Clone-and-checkout commands for local testing (if the PR was created via
  compare URL fallback — the user may need to verify the fix on their machine)
- Any follow-up actions needed (mark ready for review, add reviewers, etc.)

## Fallback Ladder

When something goes wrong, work down this list. **Do not skip to lower
rungs** — always try the higher options first.

### Rung 1: Fix and Retry (preferred)

Most failures have a specific cause (wrong remote, auth scope, branch name).
Diagnose it using the Error Recovery table and retry.

### Rung 2: Manual PR via GitHub Compare URL

If `gh pr create` fails but the branch is pushed to the fork (this is a
**common and expected** outcome when running as a GitHub App bot):

1. **Write the PR body** to `artifacts/bugfix/docs/pr-description.md`
2. **Provide the compare URL with `title` and `body` query params** so the
   PR form opens fully populated (see Step 8 failure path for format)
3. **Provide clone-and-checkout commands** for local testing
4. **Note**: between the commit message body (Step 6) and the URL params,
   the user should see the PR description auto-filled with no manual copying

### Rung 3: User creates fork, you push and PR

If no fork exists and automated forking fails:

1. Give the user the fork URL: `https://github.com/UPSTREAM_OWNER/REPO/fork`
2. **Wait for the user to confirm the fork exists**
3. Add the fork remote, push the branch, create the PR

### Rung 4: Patch file (absolute last resort)

Only if ALL of the above fail — for example, the user has no GitHub account,
or network access is completely blocked:

1. Generate a patch: `git diff > bugfix.patch`
2. Write it to `artifacts/bugfix/bugfix.patch`
3. Explain to the user how to apply it: `git apply bugfix.patch`
4. **Acknowledge this is a degraded experience** and explain what prevented
   the normal flow

## Output

- The PR URL (printed to the user)
- Optionally updates `artifacts/bugfix/docs/pr-description.md` if it didn't
  already exist

## Usage Examples

**After completing the workflow:**

```text
/pr
```

**With a specific issue reference:**

```text
/pr Fixes #47 - include all documented tool types in OpenAPI spec
```

**When the fork is already set up:**

```text
/pr --repo openresponses/openresponses
```

## Error Recovery Quick Reference

| Symptom | Cause | Fix |
| --- | --- | --- |
| `gh auth status` fails | Not logged in | User must run `gh auth login` |
| `gh` commands return 401 "Bad credentials" | `GITHUB_TOKEN` expired mid-session | Query git credential helper for fresh token, then `gh auth login --with-token` (see Step 0 recovery) |
| `git push` "could not read Username" | git credential helper not configured | Run `gh auth setup-git` then retry push |
| `git push` permission denied | Pushing to upstream, not fork | Verify remote URL, switch to fork |
| `git push` "refusing to allow...without `workflows` permission" | Fork out of sync with upstream (missing workflow files) | Run Step 4a: sync fork, then rebase and retry push |
| `gh pr create` 403 / "Resource not accessible" | Bot installed on user, not upstream org | Give user the compare URL (Rung 2) — this is expected for most bot setups |
| `gh repo fork` fails | Sandbox blocks forking | User creates fork manually |
| Branch not found on remote | Push failed silently | Re-run `git push`, check network |
| No changes to commit | Changes already committed or not staged | Check `git status`, `git log` |
| Wrong base branch | `DEFAULT_BRANCH` wasn't detected or was overridden | Re-run `gh repo view --json defaultBranchRef` and update `DEFAULT_BRANCH` |

## Notes

- This skill assumes the bug fix work (code changes, tests) is already done.
  Run `/fix` and `/test` first.
- If `/document` was run, the PR description artifact should already exist at
  `artifacts/bugfix/docs/pr-description.md`. This skill will use it.
- If `/document` was NOT run, this skill creates a minimal PR body from
  session context (conversation history, prior artifacts).
- The fork workflow is the standard for open source contributions. Even if the
  user has write access to upstream, using a fork keeps the upstream clean.

## When This Phase Is Done

Report your results:

- PR URL (or manual creation URL if automated creation wasn't possible)
- What was included
- Any follow-up actions needed (mark ready for review, add reviewers, etc.)

Then announce which file you are returning to (e.g., "Returning to `.claude/skills/controller/SKILL.md`." or "Returning to `.claude/skills/speedrun/SKILL.md` for next phase.") and **re-read that file** for next-step guidance.
