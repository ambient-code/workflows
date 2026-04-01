# Document Review Workflow

Systematic workflow for reviewing a project's documentation — assessing quality, completeness, accuracy, and consistency, then generating actionable findings.

## Features

- Auto-discovers all documentation files across the project
- Evaluates docs against 7 quality dimensions
- Classifies findings by severity for prioritized action
- Cross-references documentation claims against source code using parallel discovery agents
- Runs quality-review and code-check in parallel as sub-agents for speed
- Creates Jira epics with child bugs/tasks from the report via Jira REST API
- Supports a full-review mode for one-shot review

## Quick Start

### Loading the Workflow

In ACP, select **Custom Workflow…** and fill in:

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/ambient-code/workflows.git` |
| **Branch** | `main` |
| **Path** | `workflows/document-review` |

Then open or point the session at the project whose documentation you want to review.

### One-Shot Review

Run `/full-review` — this executes scan → quality-review + code-check (parallel) → report automatically. Results are written to `artifacts/`.

### Step-by-Step Review

For more control, run phases individually:

1. `/scan` — discover and catalog all docs
2. `/quality-review` — deep quality analysis (runs as sub-agent)
3. `/code-check` — cross-reference docs against source code (runs as sub-agent, parallel with quality-review)
4. `/report` — consolidate findings into a single report
5. `/jira` — create Jira issues from the report (optional, requires Jira credentials)

### Environment Variables

Only required if using `/jira`:

| Variable | Required | `/jira` Argument | Description |
|----------|----------|------------------|-------------|
| `JIRA_URL` | Yes | — | Base URL of the Jira instance (e.g., `https://myorg.atlassian.net`) |
| `JIRA_EMAIL` | Yes | — | Email address for authentication |
| `JIRA_API_TOKEN` | Yes | — | API token for authentication |
| `JIRA_PROJECT` | No | first positional arg | Default project key |
| `JIRA_COMPONENT` | No | `component=<name>` | Default component name |
| `JIRA_LABELS` | No | `labels=<a,b,c>` | Default comma-separated labels |
| `JIRA_TEAM` | No | `team=<name>` | Default team name |
| `JIRA_INITIAL_STATUS` | No | `status=<name>` | Workflow transition after creation (e.g., `Backlog`) |

> **Warning:** `/jira` uses `curl` to call the Jira REST API directly because the Atlassian MCP does not support creating epics or issues. Your `JIRA_API_TOKEN` will be visible in the session history.

## Directory Structure

```text
workflows/document-review/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   ├── commands/
│   │   ├── scan.md               # Discover and catalog docs
│   │   ├── quality-review.md      # Quality review
│   │   ├── code-check.md         # Code cross-referencing
│   │   ├── report.md             # Consolidated report
│   │   ├── jira.md               # Jira issue creation
│   │   └── full-review.md        # Full pipeline
│   └── skills/
│       ├── controller/SKILL.md   # Phase orchestration
│       ├── scan/SKILL.md         # Document discovery
│       ├── quality-review/SKILL.md  # Quality evaluation
│       ├── code-check/SKILL.md     # Source code verification
│       ├── code-check/references/  # Discovery agent prompts
│       ├── report/SKILL.md       # Report generation
│       └── jira/SKILL.md         # Jira issue creation
├── templates/                    # Output format templates
│   ├── inventory.md
│   ├── findings-quality-review.md
│   ├── findings-code-check.md
│   └── report.md
├── CLAUDE.md                     # Behavioral context
└── README.md                     # This file
```

## Commands

| Command | Purpose |
|---------|---------|
| `/scan` | Discover and catalog all documentation in the project |
| `/quality-review` | Deep quality review against 7 dimensions |
| `/code-check` | Cross-reference docs against source code |
| `/report` | Consolidate all findings into a deduplicated report |
| `/jira` | Create Jira epic with child bugs/tasks from the report (optional) |
| `/full-review` | Run scan → quality-review + code-check → report in one shot |

## Workflow Phases

```text
scan ──┬──> quality-review (sub-agent) ──┬──> report ──> jira (optional)
       └──> code-check (sub-agent)     ──┘       
```

Quality review and code check are independent after scan — they run in parallel as sub-agents, each writing to its own findings file.

### 1. Scan

Discovers all documentation files using glob patterns. Catalogs each file by path, format, topic, audience, and whether it contains executable instructions. Produces an inventory.

### 2. Quality Review

Deep-reads each document evaluating 7 quality dimensions: accuracy, completeness, consistency, clarity, currency, structure, and examples. Identifies target audience per document and assesses audience-appropriateness. Classifies findings by severity.

### 3. Code Check

Runs a three-stage pipeline to systematically verify documentation against source code:

1. **Reconnaissance** — Detects languages, frameworks, and components in the project
2. **Discovery** — Dispatches up to 8 parallel agents to scan source code for env vars, CLI args, config schemas, API endpoints, data models, file I/O, external deps, and build targets
3. **Verification** — Cross-references the discovered code inventory against documentation to find inaccuracies, undocumented features, and stale references

### 4. Report

Consolidates all findings from quality review and code check into a single deduplicated report. Findings are grouped by severity (Critical → Low) with a dimension × severity summary table. Reads from whichever findings files exist.

### 5. Jira (Optional)

Creates a Jira epic from the report with a child bug or task for each finding. Bugs are for findings that impact external users or customers. Tasks are for developer-facing or maintenance items. Uses the Jira REST API via `curl` (requires `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` environment variables). Accepts project key, component, labels, fix version, and team as arguments or environment variables.

### 6. Full Review

Runs scan → quality-review + code-check (parallel) → report in one shot, pausing only for critical decisions.

## Quality Dimensions

| Dimension | What It Checks |
|-----------|---------------|
| Accuracy | Do docs match reality? |
| Completeness | Are there gaps or missing docs? |
| Consistency | Do docs agree with each other? |
| Clarity | Is language clear for the audience? |
| Currency | Dead links, deprecated refs? |
| Structure | Logical organization? |
| Examples | Code samples present and correct? |

## Finding Severities

| Severity | Definition |
|----------|-----------|
| Critical | Incorrect information, broken commands, or missing steps that block users |
| High | Significant gaps, contradictions, or outdated content |
| Medium | Issues that cause confusion but have workarounds |
| Low | Minor improvements to clarity, structure, or presentation |

## Output Artifacts

Output files are written to `artifacts/`:

| File | Content |
|------|---------|
| `artifacts/inventory.md` | Documentation file catalog |
| `artifacts/findings-quality-review.md` | Detailed findings by document |
| `artifacts/findings-code-check.md` | Code verification findings |
| `artifacts/report.md` | Consolidated findings report |
