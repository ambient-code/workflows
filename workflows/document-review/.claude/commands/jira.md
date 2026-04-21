# /jira - Create Jira Issues From Report

## Purpose

Creates a Jira epic from the documentation review report, with a child bug or
task for each finding. Bugs are for findings that impact external users or
customers. Tasks are for findings that impact developers or are maintenance
items.

## Prerequisites

- `artifacts/report.md` must exist (run `/report` first)
- `pandoc` must be installed (install via `pip install pypandoc_binary`)
- `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` environment variables must be set

## Usage

```text
/jira <project-key> [component=<name>] [labels=<a,b,c>] [team=<name>] [status=<name>]
```

Arguments override environment variables. If no project key is given, the
`JIRA_PROJECT` environment variable is used. Any field not provided via
arguments or environment variables will be prompted for — the user must
explicitly set a value or confirm it should be left blank.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `JIRA_PROJECT` | Default Jira project key |
| `JIRA_COMPONENT` | Default component name |
| `JIRA_LABELS` | Default comma-separated labels |
| `JIRA_TEAM` | Default team name |
| `JIRA_INITIAL_STATUS` | Workflow transition after creation (e.g., `Backlog`) |

### Examples

```text
/jira DOCS component=documentation labels=docs,review team=docs-team status=Backlog
/jira DOCS component=none labels=none team=none status=New
```

## Process

1. Read the skill at `.claude/skills/jira/SKILL.md`
2. Execute the skill's steps

## Output

Jira issues created via the Jira REST API:

- One **Epic** summarizing the full review
- One **Bug** or **Task** per finding, as children of the epic
