---
name: jira
description: Create a Jira epic from the documentation review report with child bugs and tasks for each finding.
---

# Jira Skill

You are creating Jira issues from the documentation review report. Each finding
becomes a child issue under a parent epic so the team can track remediation.

## Prerequisites

- `artifacts/report.md` must exist (run `/report` first)
- `pandoc` must be installed (used to convert Markdown to Jira wiki markup).
  Install via `pip install pypandoc_binary` (bundles the pandoc binary).
- The following environment variables must be set for Jira API access:
  - `JIRA_URL` — base URL of the Jira instance (e.g., `https://myorg.atlassian.net`)
  - `JIRA_EMAIL` — email address for authentication
  - `JIRA_API_TOKEN` — API token for authentication
- A Jira project key must be provided as an argument or via the `JIRA_PROJECT`
  environment variable

## Inputs

Every field below must be explicitly specified by the user before issue creation
begins. A field can be set to a value or explicitly marked as "none" / left
blank — but the user must state this. Do not assume defaults or skip fields that
were not mentioned. If any field is missing from the arguments and environment
variables, prompt the user for it.

Arguments passed to the `/jira` command take precedence over environment
variables.

| Parameter | Argument | Env Var |
|-----------|----------|---------|
| Project key | first positional arg | `JIRA_PROJECT` |
| Component | `component=<name>` | `JIRA_COMPONENT` |
| Labels | `labels=<a,b,c>` | `JIRA_LABELS` |
| Team | `team=<name>` | `JIRA_TEAM` |
| Initial status | `status=<name>` | `JIRA_INITIAL_STATUS` |

The **Initial status** is the workflow transition to apply after creating each
issue (e.g., `Backlog`, `New`, `To Do`). If set, transition each issue to this
status immediately after creation. If explicitly left blank, issues stay in the
workflow's default initial state.

## Process

### Step 1: Read the Report

Read `artifacts/report.md`. Extract:

- **Header metadata**: date, repository, commit SHA, instruction
- **Summary table**: dimension x severity counts and ratings
- **All findings**: each finding under its severity heading (Critical, High,
  Medium, Low)

For each finding, capture:

- **ID**: the severity-prefixed number (C1, H1, M1, L1, etc.)
- **Title**: the heading text after the ID
- **Dimension**: the quality dimension (Accuracy, Completeness, etc.)
- **File**: the file path and line reference
- **Source**: which phase detected it (review, verify)
- **Issue**: description of what is wrong
- **Evidence**: quoted text or output demonstrating the problem
- **Fix**: the suggested correction (if present)

### Step 2: Resolve Jira Metadata

1. Check arguments first, then fall back to environment variables
2. Parse comma-separated labels into a list
3. Verify that `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` are set. If any
   are missing, stop and tell the user which variables need to be configured.
4. Check that **every** metadata field has been explicitly addressed — either
   set to a value or explicitly left blank. If any field is unspecified (not
   provided as an argument and not set as an environment variable), stop and
   ask the user for the missing fields. List each missing field by name so the
   user can provide a value or confirm it should be left blank.
5. Confirm the full plan with the user before creating issues:
   - Project key
   - Component (or "none")
   - Labels (or "none", in addition to `acp:document-review`)
   - Team (or "none")
   - Initial status transition (or "default")
   - Number of findings to file

### Step 3: Create the Epic

Use the Jira REST API via `curl` to create an Epic. All API calls use basic
authentication with `$JIRA_EMAIL:$JIRA_API_TOKEN` and target
`$JIRA_URL/rest/api/2/issue`.

#### Convert Markdown to Jira wiki markup

Jira REST API v2 description fields use wiki markup, not Markdown. Convert
content with pandoc before sending (pipe the Markdown through
`pandoc -f markdown -t jira`). This applies to the epic description and every
child issue description in Step 4.

#### Create the Epic with:

- **Project**: the resolved project key
- **Issue type**: `Epic`
- **Epic Name**: `Documentation Review: <date>` (use the date from the report
  header)
- **Summary**: `Documentation Review Report of <date> for <scope>` where
  `<date>` is the report date and `<scope>` is the repository or repositories
  listed in the report header (if multiple repos, join them with commas)
- **Description**: Only the header portion of `artifacts/report.md` — everything
  before the `## Summary` heading (title, date, repositories, and instruction). 
  Convert this extract to Jira wiki markup via pandoc before sending.
- **Labels**: merge `acp:document-review` with any user-provided labels
- **Component**: set if provided

Record the created epic key (e.g., `PROJ-123`).

#### Attach the full report

After creating the epic, attach `artifacts/report.md` to it using:

```bash
curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -X POST \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@artifacts/report.md" \
  "$JIRA_URL/rest/api/2/issue/<epic-key>/attachments"
```

This keeps the full report accessible from the epic without cluttering the
description field.

If an initial status was specified, transition the epic to that status using
`POST $JIRA_URL/rest/api/2/issue/<key>/transitions` — first GET the available
transitions to find the matching transition ID, then POST it.

### Step 4: Create Child Issues

For each finding in the report, create a child issue under the epic.

#### Classify as Bug or Task

Decide per-finding based on the issue content:

- **Bug** — the finding impacts external users or customers. Examples:
  - Incorrect instructions that would cause users to fail
  - Missing steps that block user workflows
  - Broken commands or wrong API references users would encounter
  - Misleading descriptions of user-facing behavior
  - Dead links in user-facing documentation

- **Task** — the finding impacts developers or is a maintenance/housekeeping
  item. Examples:
  - Internal inconsistencies between developer docs
  - Structural or organizational improvements
  - Stale references in contributor-facing documentation
  - Style or formatting issues
  - Missing code comments or developer-facing docs

#### Build the Issue

Use the Jira REST API via `curl` (same auth as Step 3) for each finding:

- **Project**: the resolved project key
- **Issue type**: `Bug` or `Task` (per classification above)
- **Parent**: the epic key from Step 3
- **Summary**: `<ID>. <title>` (e.g., `C1. Incorrect CLI flag in quickstart`)
- **Description**: structured as follows (convert to Jira wiki markup via
  `pandoc -f markdown -t jira` before sending):

```
## Issue

<issue text from the finding>

## Why This Is a Problem

<reasoning about why this matters, synthesized from the dimension, evidence,
and context — explain the impact on users or developers>

**Evidence:**
<quoted evidence from the finding>

**Affected file:** <file path and line>
**Quality dimension:** <dimension>
**Detected by:** <source phase(s)>

## Expected Outcome

<what needs to be true when this is resolved — derived from the Fix field if
present, otherwise describe the desired end state based on the issue>
```

- **Labels**: merge `acp:document-review` with any user-provided labels
- **Component**: set if provided

After creating each child issue, if an initial status was specified, transition
it using the same approach as the epic (GET available transitions, then POST).

### Step 5: Report Results

After all issues are created, present a summary to the user:

```
## Jira Issues Created

**Epic:** <EPIC-KEY> — Documentation Review: <date>

| ID | Type | Key | Summary |
|----|------|-----|---------|
| C1 | Bug  | PROJ-124 | Incorrect CLI flag in quickstart |
| H1 | Task | PROJ-125 | Inconsistent config key names |
| ... | ... | ... | ... |

**Total:** N issues (X bugs, Y tasks) under <EPIC-KEY>
```

## Error Handling

- If a `curl` call fails or returns an error response for a specific finding,
  log the error, continue with remaining findings, and report failures at
  the end
- If the epic creation fails, stop and report the error — do not attempt to
  create child issues without a parent epic
- If any of `JIRA_URL`, `JIRA_EMAIL`, or `JIRA_API_TOKEN` are not set, stop
  and tell the user which variables are missing
- If `pandoc` is not installed, install it with `pip install pypandoc_binary`.
  If that fails, stop and tell the user.

## Output

This skill does not write to `artifacts/`. Its output is the set of Jira
issues created via the Jira REST API.

## When This Phase Is Done

Report the summary table to the user and re-read the controller
(`.claude/skills/controller/SKILL.md`) for next-step guidance.
