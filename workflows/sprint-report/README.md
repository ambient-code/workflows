# Sprint Health Report Workflow

Generates comprehensive sprint health reports from Jira data. Analyzes delivery
metrics across 8 dimensions, detects anti-patterns, computes a health rating,
and produces actionable coaching recommendations — all in a 1–2 turn experience.

## How It Works

1. The startup prompt collects context: data source, team, audience, format
2. The agent reads the sprint-report skill and executes the full analysis pipeline
3. Artifacts are written to `artifacts/sprint-report/`

## Directory Structure

```text
sprint-report/
├── .ambient/
│   └── ambient.json                          # Workflow config
├── .claude/
│   └── skills/
│       └── sprint-report/
│           └── SKILL.md                      # Analysis methodology
├── templates/
│   └── report.html                           # HTML report template
└── README.md
```

## Data Sources

- **Jira CSV export** — upload a CSV exported from a Jira sprint board
- **Jira MCP** — query Jira directly via `jira_search` with a sprint or board ID
- **Other formats** — the agent adapts to whatever tabular data the user provides

## Output Formats

| Format | Description |
| --- | --- |
| Markdown | `{SprintName}_Health_Report.md` — full report with tables |
| HTML | `{SprintName}_Health_Report.html` — styled report with KPI cards, progress bars, and coaching notes using the included template |

## Metrics Analyzed

The report covers 8 dimensions:

1. **Commitment Reliability** — delivery rate, item completion rate
2. **Scope Stability** — mid-sprint additions/removals, scope change %
3. **Flow Efficiency** — cycle time, WIP count, status distribution
4. **Story Sizing** — point distribution, oversized/unestimated items
5. **Work Distribution** — load per assignee, concentration risk
6. **Blocker Analysis** — flagged items, impediment duration
7. **Backlog Health** — acceptance criteria coverage, priority distribution
8. **Delivery Predictability** — carryover count, zombie items, aging

## Health Rating

A 0–10 risk score derived from delivery rate, acceptance criteria coverage,
zombie items, never-started items, and priority gaps.

- **0–3** = HEALTHY
- **4–6** = MODERATE RISK
- **7–10** = HIGH RISK

## Testing with Custom Workflow

To test changes before merging:

| Field | Value |
| --- | --- |
| **URL** | `https://github.com/ambient-code/workflows.git` (or your fork) |
| **Branch** | your branch name |
| **Path** | `workflows/sprint-report` |
