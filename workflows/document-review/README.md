# Document Review Workflow

Systematic workflow for reviewing a project's documentation — assessing quality, completeness, accuracy, and consistency, then generating actionable findings and fixes.

## Features

- Auto-discovers all documentation files across the project
- Evaluates docs against 7 quality dimensions
- Classifies findings by severity for prioritized action
- Cross-references documentation claims against source code
- Runs review and verify in parallel as sub-agents for speed
- Validates sub-agent output and retries on quality failures
- Generates inline fix suggestions grouped by file
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
│   │   ├── create-prs.md         # PR creation
│   │   └── speedrun.md           # Full pipeline
│   └── skills/
│       ├── controller/SKILL.md   # Phase orchestration
│       ├── scan/SKILL.md         # Document discovery
│       ├── review/SKILL.md       # Quality evaluation
│       ├── verify/SKILL.md       # Source code verification
│       ├── validate/SKILL.md     # Output validation
│       ├── report/SKILL.md       # Report generation
│       ├── fix/SKILL.md          # Fix suggestion generation
│       └── create-prs/SKILL.md   # PR creation from fixes
├── templates/                    # Output format templates
│   ├── inventory.md
│   ├── findings-review.md
│   ├── findings-verify.md
│   ├── report.md
│   ├── fixes.md
│   └── pr-log.md
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
| `/create-prs` | Create GitHub pull requests from fix suggestions (optional) |
| `/speedrun` | Run scan → review + verify → report in one shot |

## Workflow Phases

```text
scan ──┬──> review (sub-agent) ──┬──> validate ──> report ──> fix ──> create-prs
       └──> verify (sub-agent) ──┘   (automatic;
                                      retries once
                                      on failure)
```

> **Note:** `validate` in the diagram is an automatic internal step, not a user-facing command.

Review and verify are independent after scan — they run in parallel as sub-agents, each writing to its own findings file. A validation sub-agent checks findings output for coverage, structure, and evidence quality, retrying failed agents once before proceeding.

### 1. Scan

Discovers all documentation files using glob patterns. Catalogs each file by path, format, topic, audience, and whether it contains executable instructions. Produces an inventory.

### 2. Review

Deep-reads each document evaluating 7 quality dimensions: accuracy, completeness, consistency, clarity, currency, structure, and examples. Identifies target audience per document and assesses audience-appropriateness. Classifies findings by severity.

### 3. Verify (Optional)

Cross-references documentation claims against actual source code. Checks CLI flags, API endpoints, configuration options, default values, and behavior descriptions. Flags undocumented features found in code.

### 4. Report

Consolidates all findings from review and verify into a single deduplicated report. Findings are grouped by severity (Critical → Low) with a dimension × severity summary table. Reads from whichever findings files exist.

### 5. Fix (Optional)

Generates inline fix suggestions for each finding. Quotes problematic text, provides replacement, and explains rationale. Groups suggestions into pull request units with automatable classification and self-contained context for reliable text matching.

### 6. Create PRs (Optional)

Creates draft GitHub pull requests from automatable fix suggestions. Only fixes classified as `Automatable: Yes` are applied — non-automatable fixes that need human decisions are skipped entirely. All PRs are created as drafts so a human reviewer can verify the changes before merging. Produces a PR log tracking what was created and any fixes skipped.

### 7. Speedrun

Runs scan → review + verify (parallel) → validate → report in one shot, pausing only for critical decisions.

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
| `artifacts/pr-log.md` | Created PR links and status |

## Prerequisites

Most phases require only read access to the target project. The `/create-prs`
phase has additional requirements:

### GitHub Token for `/create-prs`

The `/create-prs` phase forks the target repository, pushes branches to the
fork, and opens draft pull requests against the upstream repository. This
requires a GitHub token with the right scopes.

**Classic Personal Access Token (recommended):**

A Classic PAT with the **`public_repo`** scope is sufficient for public
repositories. This single scope covers forking, pushing to the fork, and
creating PRs on the upstream repo.

```bash
export GITHUB_TOKEN=ghp_...
# or
gh auth login --with-token <<< "$GITHUB_TOKEN"
```

If the target repository is private, use the **`repo`** scope instead.

**Fine-grained Personal Access Token (untested alternative):**

Fine-grained PATs are more restrictive but harder to configure for this
workflow because the fork does not exist when the token is created and the
upstream repository is owned by someone else. If using a fine-grained PAT:

- Scope to **All repositories** owned by the token holder
- Required permissions:
  - **Contents:** Read and Write (push to the fork)
  - **Pull requests:** Read and Write (open PRs)
  - **Administration:** Read and Write (create the fork)

This configuration has not been tested. The fork-then-PR-upstream flow may
encounter edge cases with fine-grained PAT scoping.

## Quick Start

1. Point the workflow at a project repository
2. Run `/scan` to discover documentation (or `/speedrun` for the full pipeline)
3. Run `/review` for quality analysis
4. Optionally run `/verify` to check docs against code
5. Run `/report` to consolidate all findings
6. Optionally run `/fix` for concrete fix suggestions
7. Optionally run `/create-prs` to submit fixes as GitHub pull requests
