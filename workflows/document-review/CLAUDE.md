# Document Review Workflow

Systematic documentation review through these phases:

1. **Scan** (`/scan`) — Discover and catalog all documentation files
2. **Review** (`/review`) — Deep quality analysis against 7 dimensions
3. **Verify** (`/verify`) — *(Optional)* Cross-reference docs against source code
4. **Install-test** (`/install-test`) — *(Optional)* Execute installation instructions on a cluster
5. **Usage-test** (`/usage-test`) — *(Optional)* Interact with the installed project and verify usage docs
6. **Cleanup** (`/cleanup`) — Revert cluster changes from install-test and usage-test (runs automatically)
7. **Report** (`/report`) — Consolidate all findings into a single deduplicated report
8. **Fix** (`/fix`) — *(Optional)* Generate inline fix suggestions
9. **Create PRs** (`/create-prs`) — *(Optional)* Create GitHub pull requests from fix suggestions
10. **Handle Feedback** (`/handle-feedback`) — *(Optional)* Monitor PRs for reviewer comments and act on feedback
11. **Speedrun** (`/speedrun`) — Run scan → review + verify → report in one shot

Review, verify, and install-test are independent — they can run in parallel as
sub-agents after scan completes. Each writes to its own findings file.
Usage-test runs after a successful install-test, before cleanup. A validation
sub-agent checks their output for coverage, structure, and evidence quality,
retrying once on failure.

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

- Do not modify the project's documentation unless the user runs `/fix`
- Do not make assumptions about intended behavior — flag for verification
- Read-only access to project code unless explicitly told otherwise
- Never execute commands that could be destructive to the host system

## Working With the Project

This workflow gets deployed into different projects. Respect the target project:

- Understand the project's documentation conventions before critiquing
- Evaluate against the project's own standards, not arbitrary preferences
- Consider the project's maturity level when assessing completeness
- When in doubt about intended behavior, check git history and existing code
