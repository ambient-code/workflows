# Documentation Fix Suggestions

**Project:** [name]
**Repository:** [remote URL]
**Base branch:** [branch name]
**Base commit:** [short SHA]
**Generated:** [date]
**Total suggestions:** N
**Automatable:** N
**Needs human input:** N

## Summary

| Severity | Automatable | Needs Input | Total |
|----------|-------------|-------------|-------|
| Critical | N | N | N |
| High | N | N | N |
| Medium | N | N | N |
| Low | N | N | N |
| **Total** | **N** | **N** | **N** |

## Suggested Pull Requests

### PR 1: [title under 70 chars]

**Files:** `path/to/doc.md`
**Automatable:** Yes | Partial | No

#### Fix 1: [brief description]

**File:** `path/to/document.md`
**Severity:** Critical
**Automatable:** Yes
**Location:** Section "[heading]", line N

**Context** (target text is between `>>>` and `<<<`):

```
line before the target
another line before
>>> The `--port` flag sets the listening port (default: 3000). <<<
line after the target
another line after
```

**Current text:**

> The `--port` flag sets the listening port (default: 3000).

**Replacement:**

> The `--listen-port` flag sets the listening port (default: 8080).

**Rationale:** The flag was renamed from `--port` to `--listen-port` in v2.0
and the default changed from 3000 to 8080. Confirmed in `src/cli.py:45`:
`parser.add_argument('--listen-port', default=8080)`.

---

#### Fix 2: [brief description — needs input]

**File:** `path/to/document.md`
**Severity:** High
**Automatable:** No
**Location:** After section "[heading]", line N

**Context** (insert after this block):

```
line before insertion point
another line before insertion point
```

**Draft content:**

```markdown
## Troubleshooting

### Connection refused on port 8080

If you see `connection refused` when accessing the service:

1. Verify the pod is running: `oc get pods -n my-namespace`
2. Check the service port: `oc get svc my-service -n my-namespace`
3. [TODO: maintainer — document the correct port-forward command for this service]
```

**Human input needed:** What is the correct port-forward command? The service
exposes multiple ports and the documentation doesn't specify which one to use
for local access.

**Rationale:** During install-test, users encountered "connection refused"
errors at step 5 of the quickstart with no troubleshooting guidance. The exact
port-forward command depends on which port the maintainers intend users to
access.

---

**PR description:**

```markdown
## Summary

- Fix 1: Correct `--port` flag name and default value
- Fix 2: Add troubleshooting section for connection errors — **needs reviewer input**

## Human Input Needed

- [ ] Fix 2: Specify the correct port-forward command for local access
```

### PR 2: [title]

...

## Instructions for PR Agent

This section tells an independent agent how to use this file to create GitHub
pull requests autonomously.

### Repository setup

Clone the repository using the **Repository** URL above. Create branches from
the **Base branch**. The **Base commit** is the revision this review was
conducted against — if the base branch has advanced significantly since that
commit, verify that the **Context** blocks still match the current file
contents before applying fixes.

### Which fixes to apply

- **Automatable: Yes** — apply the fix.
- **Automatable: No** — skip the fix entirely. Do not create a PR for it.
  These fixes require human decisions or missing information that cannot be
  resolved autonomously. If every fix in a PR group is `Automatable: No`,
  skip the entire PR.

### How to apply each fix

1. Open the target **File**
2. Use the **Context** block to locate the exact text — search for the
   surrounding lines and find the target between `>>>` and `<<<` markers
3. Replace the **Current text** with the **Replacement**

### PR creation rules

- **Always create PRs as drafts.** Every PR must be a draft so a human
  reviewer can verify the changes before merging.
- Only include `Automatable: Yes` fixes in PRs.

### PR creation checklist

- [ ] Branch name follows `docs/fix-[brief-slug]` convention
- [ ] Branch is based on the latest base branch
- [ ] Only `Automatable: Yes` fixes are included
- [ ] Each fix is verified against its context block before applying
- [ ] Commit messages reference the fix descriptions
- [ ] PR title matches the suggested title
- [ ] PR description includes the suggested description
- [ ] PR is created as a draft
- [ ] No unrelated changes are included

### Ordering

Create PRs in severity order — PRs containing Critical fixes first, then High,
then others. This ensures the highest-impact changes are reviewed first.
