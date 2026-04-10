# Document Review Workflow

Systematic documentation review through these phases:

1. **Scan** (`/scan`) — Discover and catalog all documentation files
2. **Quality Review** (`/quality-review`) — Deep quality analysis against 7 dimensions
3. **Code Check** (`/code-check`) — Cross-reference docs against source code
4. **Report** (`/report`) — Consolidate all findings into a single deduplicated report
5. **Jira** (`/jira`) — *(Optional)* Create Jira epic with child bugs/tasks from the report

### Convenience Commands

- **Full Review** (`/full-review`) — Run scan → quality-review + code-check → report in one shot

Quality review and code check are independent — they can run in parallel as sub-agents
after scan completes. Each writes to its own findings file.

The workflow controller lives at `.claude/skills/controller/SKILL.md`.
It defines how to execute phases, recommend next steps, and handle transitions.
Phase skills are at `.claude/skills/{name}/SKILL.md`.
Output files are written to `artifacts/`.

## Quality Dimensions

1. **Accuracy** — Do docs match reality?
2. **Completeness** — Are there gaps or missing docs?
3. **Consistency** — Do docs agree with each other? Is terminology uniform?
4. **Clarity** — Is language clear for the target audience?
5. **Currency** — Dead links, deprecated references, old versions?
6. **Structure** — Logical organization, navigation, headings?
7. **Examples** — Code samples present and correct?

## Finding Severities

- **Critical** — Incorrect information, broken commands, or missing steps that would block users or cause them to take wrong actions
- **High** — Significant gaps, contradictions, or outdated content that degrades the user experience
- **Medium** — Issues that cause confusion but have workarounds or limited impact
- **Low** — Minor improvements to clarity, structure, or presentation

## Principles

- Show evidence — quote the doc, cite file:line, don't make vague claims
- Be specific about what's wrong and why it matters
- Don't nitpick style when content is the real issue
- Assess audience-appropriateness for each document
- Flag uncertainty rather than guessing

## Hard Limits

- Do not modify the project's documentation — this workflow is read-only
- Do not make assumptions about intended behavior — flag for verification
- Read-only access to project code unless explicitly told otherwise
- Never execute commands that could be destructive to the host system

## Working With the Project

This workflow gets deployed into different projects. Respect the target project:

- Understand the project's documentation conventions before critiquing
- Evaluate against the project's own standards, not arbitrary preferences
- Consider the project's maturity level when assessing completeness
- When in doubt about intended behavior, check git history and existing code
