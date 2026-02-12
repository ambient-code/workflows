---
name: pr
description: Create a pull request for a bug fix, handling fork workflows, authentication, and remote setup systematically.
---

# Create Pull Request Skill

You are preparing to submit a bug fix as a pull request. This skill provides a
systematic, failure-resistant process for getting code from the working directory
into a PR. It handles the common obstacles: authentication, fork workflows,
remote configuration, and cross-repo PR creation.

## Your Role

Get the bug fix changes submitted as a draft pull request. Handle the full
git workflow: branch, commit, push, and PR creation. When steps fail, follow
the documented recovery paths instead of guessing.

## Critical Rules

- **Never ask the user for git credentials.** Use `gh auth status` to check.
- **Never push directly to upstream.** Always use a fork remote.
- **Never skip pre-flight checks.** They prevent every common failure.
- **Always create a draft PR.** Let the author mark it ready after review.
- **Always work in the project repo directory**, not the workflow directory.

## Process

### Placeholders Used in This Skill

These are determined during pre-flight checks. Record each value as you go.

| Placeholder | Source | Example |
| --- | --- | --- |
| `GH_USER` | Step 1a: `gh api user --jq .login` | `jsmith` |
| `UPSTREAM_OWNER/REPO` | Step 1d: `gh repo view --json nameWithOwner` | `acme/myproject` |
| `FORK_OWNER` | Step 2: owner portion of fork's `nameWithOwner`, or `GH_USER` if newly created | `jsmith` |
| `REPO` | The repository name (without owner) | `myproject` |
| `BRANCH_NAME` | Step 4: the branch you create | `bugfix/issue-42-null-check` |

### Step 0: Locate the Project Repository

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

### Step 1: Pre-flight Checks

Run ALL of these before doing anything else. Do not skip any.

**1a. Check GitHub CLI authentication:**

```bash
gh auth status
```

- If authenticated: **record the GitHub username** — you will need it later as
  `GH_USER`. You can also extract it reliably with:

```bash
gh api user --jq .login
```

- If not authenticated: STOP. Tell the user `gh auth login` is required and
  explain why. Do not attempt workarounds.

**1b. Check git configuration:**

```bash
git config user.name
git config user.email
```

- If both are set: proceed.
- If missing: set them from the `gh` auth context:

```bash
git config user.name "$(gh api user --jq .login)"
git config user.email "$(gh api user --jq '.email // (.login + "@users.noreply.github.com")')"
```

**1c. Inventory existing remotes:**

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

**1d. Identify the upstream repo:**

```bash
# Get the upstream repo in owner/repo format
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Record this — you'll need it for `gh pr create --repo`.

**1e. Check current branch and changes:**

```bash
git status
git diff --stat
```

Confirm there are actual changes to commit. If there are no changes, stop
and tell the user.

### Step 2: Ensure a Fork Exists

You almost certainly do NOT have push access to the upstream repo. Use a fork.

**Determining FORK_OWNER:** The fork owner is almost always `GH_USER` (the
authenticated GitHub username from Step 1a). When the `gh repo list` command
below returns a fork, its `nameWithOwner` will be in `FORK_OWNER/REPO` format —
use the owner portion. If the user creates a new fork, `FORK_OWNER` = `GH_USER`.

**Check if a fork already exists:**

```bash
gh repo list --fork --json nameWithOwner,parent --jq '.[] | select(.parent.nameWithOwner == "UPSTREAM_OWNER/REPO") | .nameWithOwner'
```

Replace `UPSTREAM_OWNER/REPO` with the value from Step 1d. The output will be
`FORK_OWNER/REPO` (e.g., `jsmith/myproject`). Record the owner portion as
`FORK_OWNER`.

**If a fork exists:** use it — skip ahead to Step 3.

**If NO fork exists — STOP and ask the user.** Do not silently skip ahead or
fall back to a patch file. Say something like:

> I don't see a fork of UPSTREAM_OWNER/REPO under your GitHub account.
> To create a PR, you'll need a fork. Would you like me to try creating one?
> If that doesn't work in this environment, you can create one at:
> `https://github.com/UPSTREAM_OWNER/REPO/fork`

Wait for the user to respond. Once they confirm:

1. Try creating the fork:

```bash
gh repo fork UPSTREAM_OWNER/REPO --clone=false
```

1. If this succeeds, continue to Step 3.
1. If this fails (sandbox/permission issue), tell the user to create the fork
   manually using the URL above and to let you know when it's ready. **Wait
   for the user to confirm before continuing.**

Only proceed to Step 3 once a fork actually exists.

### Step 3: Configure the Fork Remote

Once a fork exists (or was found), ensure there's a git remote pointing to it.

```bash
# Check if fork remote already exists
git remote -v | grep FORK_OWNER
```

If not present, add it:

```bash
git remote add fork https://github.com/FORK_OWNER/REPO.git
```

Use `fork` as the remote name. If `origin` already points to the fork, that's
fine — just use `origin` in subsequent commands instead of `fork`.

### Step 4: Create a Branch

```bash
git checkout -b bugfix/BRANCH_NAME
```

Branch naming conventions:

- `bugfix/issue-NUMBER-SHORT_DESCRIPTION` if there's an issue number
- `bugfix/SHORT_DESCRIPTION` if there's no issue number
- Use kebab-case, keep it under 50 characters

If a branch already exists with the changes (from a prior `/fix` phase), use
it instead of creating a new one.

### Step 5: Stage and Commit

**Stage changes selectively** — don't blindly `git add .`:

```bash
# Review what would be staged
git diff --stat

# Stage the relevant files
git add path/to/changed/files

# Verify staging
git status
```

**Commit with a structured message:**

```bash
git commit -m "fix(SCOPE): SHORT_DESCRIPTION

DETAILED_DESCRIPTION

Fixes #ISSUE_NUMBER"
```

Follow conventional commit format. The scope should identify the affected
component. Reference the issue number if one exists.

If prior artifacts exist (root cause analysis, implementation notes), use them
to write an accurate commit message. Don't make up details.

### Step 6: Push to Fork

```bash
git push -u fork bugfix/BRANCH_NAME
```

**If this fails:**

- **Authentication error**: Check `gh auth status` again. The user may need
  to re-authenticate or the sandbox may be blocking network access.
- **Remote not found**: Verify the fork remote URL is correct.
- **Permission denied**: The fork remote may be pointing to upstream, not the
  actual fork. Verify with `git remote get-url fork`.

If push requires sandbox permissions, tell the user: "The push needs network
access. Please run: `git push -u fork BRANCH_NAME`"

### Step 7: Create the Draft PR

```bash
gh pr create \
  --draft \
  --repo UPSTREAM_OWNER/REPO \
  --head FORK_OWNER:bugfix/BRANCH_NAME \
  --base main \
  --title "fix(SCOPE): SHORT_DESCRIPTION" \
  --body-file artifacts/bugfix/docs/pr-description.md
```

**Key flags explained:**

- `--repo`: The upstream repository (where the PR goes). REQUIRED for cross-fork PRs.
- `--head`: Must be `FORK_OWNER:BRANCH_NAME` format for fork-based PRs. Without the
  owner prefix, GitHub looks for the branch on the upstream repo and fails.
- `--base`: The target branch on upstream (usually `main`).
- `--draft`: Always submit as draft first.
- `--body-file`: Use the PR description artifact if `/document` was run.

**If `--body-file` artifact doesn't exist**, use `--body` with inline content:

```bash
gh pr create \
  --draft \
  --repo UPSTREAM_OWNER/REPO \
  --head FORK_OWNER:bugfix/BRANCH_NAME \
  --base main \
  --title "fix(SCOPE): SHORT_DESCRIPTION" \
  --body "## Problem
WHAT_WAS_BROKEN

## Root Cause
WHY_IT_WAS_BROKEN

## Fix
WHAT_THIS_PR_CHANGES

## Testing
HOW_THE_FIX_WAS_VERIFIED

## Confidence
HIGH_MEDIUM_LOW — BRIEF_JUSTIFICATION

## Rollback
HOW_TO_REVERT_IF_SOMETHING_GOES_WRONG

## Risk Assessment
LOW_MEDIUM_HIGH — WHAT_COULD_BE_AFFECTED

Fixes #ISSUE_NUMBER"
```

**If `gh pr create` fails:**

- **"permission denied" or "403"**: The bot cannot create PRs on the upstream
  repo. Provide the user with the direct URL instead:

  ```text
  https://github.com/FORK_OWNER/REPO/pull/new/bugfix/BRANCH_NAME
  ```

  And give them the PR title and body to paste.
- **"branch not found"**: The push in Step 6 may have failed silently.
  Verify with `git ls-remote fork bugfix/BRANCH_NAME`.

### Step 8: Confirm and Report

After the PR is created (or the URL is provided), summarize:

- PR URL (or manual creation URL)
- What was included in the PR
- What branch it targets
- Any follow-up actions needed (mark ready for review, add reviewers, etc.)

## Fallback Ladder

When something goes wrong, work down this list. **Do not skip to lower
rungs** — always try the higher options first.

### Rung 1: Fix and Retry (preferred)

Most failures have a specific cause (wrong remote, auth scope, branch name).
Diagnose it using the Error Recovery table and retry.

### Rung 2: Manual PR URL

If `gh pr create` fails but the branch is pushed to the fork:

1. **Provide the URL**: `https://github.com/FORK_OWNER/REPO/pull/new/BRANCH`
2. **Provide the PR title and body** so the user can paste them in
3. **Note the base branch** (usually `main`)

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
| `git push` permission denied | Pushing to upstream, not fork | Verify remote URL, switch to fork |
| `gh pr create` 403 | Bot can't create PRs upstream | Give user the manual PR URL |
| `gh repo fork` fails | Sandbox blocks forking | User creates fork manually |
| Branch not found on remote | Push failed silently | Re-run `git push`, check network |
| No changes to commit | Changes already committed or not staged | Check `git status`, `git log` |
| Wrong base branch | Upstream default isn't `main` | Check with `gh repo view --json defaultBranchRef` |

## Notes

- This skill assumes the bug fix work (code changes, tests) is already done.
  Run `/fix` and `/test` first.
- If `/document` was run, the PR description artifact should already exist at
  `artifacts/bugfix/docs/pr-description.md`. This skill will use it.
- If `/document` was NOT run, this skill creates a minimal PR body from
  session context (conversation history, prior artifacts).
- The fork workflow is the standard for open source contributions. Even if the
  user has write access to upstream, using a fork keeps the upstream clean.
