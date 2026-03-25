# Document Review Workflow

Systematic workflow for reviewing a project's documentation — assessing quality, completeness, accuracy, and consistency, then generating actionable findings and fixes.

## Features

- Auto-discovers all documentation files across the project
- Evaluates docs against 7 quality dimensions
- Classifies findings by severity for prioritized action
- Cross-references documentation claims against source code using parallel discovery agents
- Runs review and verify in parallel as sub-agents for speed
- Generates inline fix suggestions grouped by file
- Creates Jira epics with child bugs/tasks from the report via Jira REST API
- Supports a speedrun mode for one-shot review

## Directory Structure

```text
workflows/document-review/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   ├── commands/
│   │   ├── scan.md               # Discover and catalog docs
│   │   ├── review.md             # Quality review
│   │   ├── verify.md             # Code cross-referencing
│   │   ├── report.md             # Consolidated report
│   │   ├── fix.md                # Fix suggestions
│   │   ├── jira.md               # Jira issue creation
│   │   └── speedrun.md           # Full pipeline
│   └── skills/
│       ├── controller/SKILL.md   # Phase orchestration
│       ├── scan/SKILL.md         # Document discovery
│       ├── review/SKILL.md       # Quality evaluation
│       ├── verify/SKILL.md       # Source code verification
│       ├── verify/references/   # Discovery agent prompts
│       ├── report/SKILL.md       # Report generation
│       ├── fix/SKILL.md          # Fix suggestion generation
│       └── jira/SKILL.md         # Jira issue creation
├── templates/                    # Output format templates
│   ├── inventory.md
│   ├── findings-review.md
│   ├── findings-verify.md
│   ├── report.md
│   └── fixes.md
├── CLAUDE.md                     # Behavioral context
└── README.md                     # This file
```

## Commands

| Command | Purpose |
|---------|---------|
| `/scan` | Discover and catalog all documentation in the project |
| `/review` | Deep quality review against 7 dimensions |
| `/verify` | Cross-reference docs against source code (optional) |
| `/report` | Consolidate all findings into a deduplicated report |
| `/fix` | Generate inline fix suggestions (optional) |
| `/jira` | Create Jira epic with child bugs/tasks from the report (optional) |
| `/speedrun` | Run scan → review + verify → report in one shot |

## Workflow Phases

```text
scan ──┬──> review (sub-agent) ──┬──> report ──> fix
       └──> verify (sub-agent) ──┘            └──> jira
```

Review and verify are independent after scan — they run in parallel as sub-agents, each writing to its own findings file.

### 1. Scan

Discovers all documentation files using glob patterns. Catalogs each file by path, format, topic, audience, and whether it contains executable instructions. Produces an inventory.

### 2. Review

Deep-reads each document evaluating 7 quality dimensions: accuracy, completeness, consistency, clarity, currency, structure, and examples. Identifies target audience per document and assesses audience-appropriateness. Classifies findings by severity.

### 3. Verify (Optional)

Runs a three-stage pipeline to systematically verify documentation against source code:

1. **Reconnaissance** — Detects languages, frameworks, and components in the project
2. **Discovery** — Dispatches up to 8 parallel agents to scan source code for env vars, CLI args, config schemas, API endpoints, data models, file I/O, external deps, and build targets
3. **Verification** — Cross-references the discovered code inventory against documentation to find inaccuracies, undocumented features, and stale references

### 4. Report

Consolidates all findings from review and verify into a single deduplicated report. Findings are grouped by severity (Critical → Low) with a dimension × severity summary table. Reads from whichever findings files exist.

### 5. Fix (Optional)

Generates inline fix suggestions for each finding. Quotes problematic text, provides replacement, and explains rationale. Groups suggestions into pull request units with automatable classification and self-contained context for reliable text matching.

### 6. Jira (Optional)

Creates a Jira epic from the report with a child bug or task for each finding. Bugs are for findings that impact external users or customers. Tasks are for developer-facing or maintenance items. Uses the Jira REST API via `curl` (requires `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` environment variables). Accepts project key, component, labels, fix version, and team as arguments or environment variables.

### 7. Speedrun

Runs scan → review + verify (parallel) → report in one shot, pausing only for critical decisions.

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
| `artifacts/findings-review.md` | Detailed findings by document |
| `artifacts/findings-verify.md` | Code verification findings |
| `artifacts/report.md` | Consolidated findings report |
| `artifacts/fixes.md` | Inline fix suggestions with PR grouping |

## Quick Start

1. Point the workflow at a project repository
2. Run `/scan` to discover documentation (or `/speedrun` for the full pipeline)
3. Run `/review` for quality analysis
4. Optionally run `/verify` to check docs against code
5. Run `/report` to consolidate all findings
6. Optionally run `/fix` for concrete fix suggestions
7. Optionally run `/jira` to create Jira issues for tracking
