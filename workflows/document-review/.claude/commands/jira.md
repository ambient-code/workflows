# /jira - Create Jira Issues From Report

## Purpose

Creates a Jira epic from the documentation review report, with a child bug or
task for each finding. Bugs are for findings that impact external users or
customers. Tasks are for findings that impact developers or are maintenance
items.

## Prerequisites

- `artifacts/report.md` must exist (run `/report` first)
- `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` environment variables must be set

## Usage

```text
/jira <project-key> [component=<name>] [labels=<a,b,c>] [fixversion=<name>] [team=<name>]
```

Arguments override environment variables. If no project key is given, the
`JIRA_PROJECT` environment variable is used.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `JIRA_PROJECT` | Default Jira project key |
| `JIRA_COMPONENT` | Default component name |
| `JIRA_LABELS` | Default comma-separated labels |
| `JIRA_FIX_VERSION` | Default fix version |
| `JIRA_TEAM` | Default team name |

### Examples

```text
/jira DOCS
/jira DOCS component=documentation labels=docs,review
/jira DOCS fixversion=4.2 team=docs-team
```

## Process

1. Read the skill at `.claude/skills/jira/SKILL.md`
2. Execute the skill's steps

## Output

Jira issues created via the Jira REST API:

- One **Epic** summarizing the full review
- One **Bug** or **Task** per finding, as children of the epic
